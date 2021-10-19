Deploying to production
=======================

As an example, these are the instructions for restoring the production deployment on https://okd.hbp.eu/.

#. You can use the deployment configuration saved in `<openshift-prod-export.yaml>`_ provided in the repository as a starting point. Edit the route contained in this file to use the correct URL.
#. Create the project named `hbp-spatial-backend` on https://okd.hbp.eu/
#. Log in using the command-line ``oc`` tool (https://okd.hbp.eu/console/command-line), switch to the `hbp-spatial-backend` project with ``oc project hbp-spatial-backend``
#. Import the objects from your edited YAML file using ``oc create -f openshift-prod-export.yaml``
#. Re-create the Persistent Volume Claims and upload the data (see below).
#. Edit the Config Maps if needed, re-create the needed Secrets (namely ``github-webhook-secret``).
#. Start the build. The deployment should follow automatically.
#. For production, increase the number of replicas in order to be more resilient to node failures: go to `Applications` -> `Deployments` -> `flask` -> `Configuration` and change the number of `Replicas` to 3.
#. Go to `Builds` -> `Builds` -> `flask` -> `Configuration`, copy the GitHub Webhook URL and configure it into the GitHub repository (https://github.com/HumanBrainProject/hbp-spatial-backend/settings/hooks). Make sure to set the Content Type to ``application/json``.

The deployment configuration is saved to `<openshift-prod-export.yaml>`_ by running ``oc get -o yaml --export is,bc,dc,svc,route,pvc,cm,horizontalpodautoscaler > openshift-prod-export.yaml`` (`status`, `resourceVersion`, `generation`, `@sha256`, `PersistentVolumeClaim` metadata (`volumeName`, `finalizers`, `annotations`) and `secret` information is stripped manually, see https://collab.humanbrainproject.eu/#/collab/38996/nav/270508 for other edits that may be necessary).


Deployment on okd-dev.hbp.eu
============================

For the record, here are the steps that were used to create this OpenShift project:

#. Create the project / navigate to the project on https://okd-dev.hbp.eu/

#. Configure the Flask instance

   #. Add to Project -> Browse Catalog
   #. Choose Python (does not matter, configuration will be changed later). Hit Next
   #. In Step 2 (Configuration), hit `advanced options` and enter these values:

      - `flask` as Name
      - `https://github.com/HumanBrainProject/hbp-spatial-backend.git` as Git Repository
      - `dev` as Git Reference
      - Under Routing, enter `hbp-spatial-backend.apps-dev.hbp.eu` as Hostname
      - Under Routing, check `Secure route`
      - Under Routing, set `Insecure Traffic` to `Redirect`
      - Under `Build Configuration`, uncheck `Launch the first build when the build configuration is created`

   #. Hit `Create` at the bottom of the page
   #. Follow the instructions to configure the GitHub webhook

      #. (optional) If you are going to publish the OpenShift deployment configuration, make sure that the webhook secrets refer to a real `Secret` resource (e.g. ``github-webhook-secret``) instead of being stored in clear-text in the `BuildConfig` object.

   #. Change the build configuration to use the `Docker` build strategy:

      #. Go to `Builds` -> `Builds` -> `flask` -> `Actions` -> `Edit YAML`
      #. Replace the contents of the `strategy` key by::

           dockerStrategy:
             dockerfilePath: Dockerfile.server
           type: Docker

      #. Hit `Save`

   #. Add post-build tests and tweak build configuration

      #. Go to `Builds` -> `Builds` -> `flask` -> `Actions` -> `Edit`. Click on `advanced options`.
      #. Under `Image Configuration`, check `Always pull the builder image from the docker registry, even if it is present locally`
      #. Under `Post-Commit Hooks`, check `Run build hooks after image is built`. Choose `Hook Type` = `Shell Script` and enter the following Script::

           set -e
           # Without PIP_IGNORE_INSTALLED=0 the Debian version of pip would
           # re-install already installed dependencies in the user's home
           # directory
           # (https://github.com/pypa/pip/issues/4222#issuecomment-417672236)
           cd /source
           PIP_IGNORE_INSTALLED=0 python3 -m pip install --user -r test-requirements.txt
           python3 -m pytest tests/

      #. Hit `Save`

   #. Trigger the build by hitting `Start Build`
   #. Configure the Flask instance

      #. Go to `Applications` -> `Deployments` -> `flask` -> `Configuration`
      #. Under `Volumes`, hit `Add Config Files`
      #. Click `Create Config Map`

         - `Name` = `instance-dir`
         - `Key` = `config.py`
         - `Value`::

             CORS_ORIGINS = '*'
             PROXY_FIX = {
                 'x_for': 1,
                 'x_host': 1,
                 'x_port': 1,
                 'x_proto': 1,
             }
             DEFAULT_TRANSFORM_GRAPH = '/static-data/DISCO_20181004_sigV30_DARTEL_20181004_reg_x4/graph.yaml'

      #. Hit `Create`
      #. Back in the `Add Config Files` page, choose the newly created `instance-dir` as `Source`
      #. Set `Mount Path` = `/instance`
      #. Hit `Add`
      #. Go to the `Environment` tab and add these variables:

         - `INSTANCE_PATH` = `/instance`

   #. Create a volume to hold the static data (transformation graph and deformation fields)

      #. Go to `Applications` -> `Deployments` -> `flask` -> `Configuration`
      #. Under `Volumes`, hit `Add Storage`
      #. Hit `Create Storage`
      #. Set `Name` = `static-data`, `Size` = `10 GiB`
      #. Hit `Create`
      #. Set `Mount Path` = `/static-data`
      #. Check `Read only`
      #. Hit `Add`

   #. Upload the static data (transformation graph and deformation fields). We follow the method described on https://blog.openshift.com/transferring-files-in-and-out-of-containers-in-openshift-part-3/

      #. Install the OpenShift Command-Line Tools by following the instructions on https://okd-dev.hbp.eu/console/command-line
      #. Log in using the CLI (Under your name on the top right corner, hit `Copy Login Command` and paste it into a terminal)
      #. Switch to the project (``oc project hbp-spatial-backend``)
      #. Run a dummy pod for rsync transfer with ``oc run dummy --image ylep/oc-rsync-transfer``
      #. Mount the volume against the dummy pod ``oc set volume dc/dummy --add --name=tmp-mount --claim-name=static-data --mount-path /static-data``
      #. Wait for the deployment to be complete with ``oc rollout status dc/dummy``
      #. Get the name of the dummy pod with ``oc get pods --selector run=dummy``
      #. Copy the data using ``oc rsync --compress=true --progress=true /volatile/hbp-spatial-transformations-data/ dummy-2-7tdml:/static-data/`` (replace `dummy-2-7tdml` with the pod name from the previous step).
      #. Verify the contents of the directory with ``oc rsh dummy-2-7tdml ls -l /static-data``
      #. Delete everything related to the temporary pod with ``oc delete all --selector run=dummy``

   #. Add Health Checks

      #. Go to `Applications` -> `Deployments` -> `flask` -> `Actions` -> `Edit Health Checks`
      #. Add a `Readiness Probe` of type `HTTP GET`, using `Path` = `/health`, setting some `Initial Delay` (e.g. 5 seconds) and `Timeout` (e.g. 10 seconds)
      #. Add a `Liveness Probe` of type `HTTP GET`, using `Path` = `/health`, setting a long `Timeout` (e.g. 60 seconds)
      #. Hit `Save`
