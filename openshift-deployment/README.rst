Deployment on openshift-dev.hbp.eu
==================================

For the record, here are the steps that were used to create this OpenShift project:

#. Create the project / navigate to the project

#. Configure the Flask instance

   #. Add to Project -> Browse Catalog
   #. Choose Python (does not matter, configuration will be changed later). Hit Next
   #. In Step 2 (Configuration), hit `advanced options` and enter these values:

      - `flask` as Name
      - `https://github.com/HumanBrainProject/hbp-spatial-backend.git` as Git Repository
      - `dev` as Git Reference
      - Under Routing, enter `hbp-spatial-backend.apps-dev.hbp.eu` as Hostname
      - Under Routing, check `Secure route`
      - Under `Build Configuration`, uncheck `Launch the first build when the build configuration is created`

   #. Hit `Create` at the bottom of the page
   #. Follow the instructions to configure the GitHub webhook
   #. Change the build configuration to use the `Docker` build strategy:

      #. Go to `Builds` -> `Builds` -> `flask` -> `Actions` -> `Edit YAML`
      #. Replace the contents of the `strategy` key by::

           dockerStrategy:
             dockerfilePath: Dockerfile
           type: Docker

      #. Hit `Save`

   #. Add post-build tests and tweak build configuration

      #. Go to `Builds` -> `Builds` -> `flask` -> `Actions` -> `Edit`. Click on `advanced options`.
      #. Under `Image Configuration`, check `Always pull the builder image from the docker registry, even if it is present locally`
      #. Under `Post-Commit Hooks`, check `Run build hooks after image is built`. Choose `Hook Type` = `Shell Script` and enter the following Script::

           set -e
           python3 -m pip install --user /source[tests]
           cd /source
           python3 -m pytest

      #. Hit `Save`

   #. Trigger the build by hitting `Start Build`
   #. Configure the Flask instance

      #. Go to `Applications` -> `Deployments` -> `flask` -> `Configuration`
      #. Under `Volumes`, hit `Add Config Files`
      #. Click `Create Config Map`

         - `Name` = `instance-dir`
         - `Key` = `config.py`
         - `Value`::

             CORS_ALLOW_ALL = True
             REQUEST_TIMEOUT = 30  # seconds
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

      #. Install the OpenShift Command-Line Tools by following the instructions on https://openshift-dev.hbp.eu/console/command-line
      #. Log in using the CLI (Under your name on the top right corner, hit `Copy Login Command` and paste it into a terminal)
      #. Switch to the project (``oc project hbp-spatial-transform``)
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


Deploying to production
=======================

#. Once the project is successfully deployed on openshift-dev, export the deployment configuration: run ``oc get -o yaml --export is,bc,dc,svc,route,pvc > openshift-dev-export.yaml``.
#. Process `openshift-dev-export.yaml` as described in https://collab.humanbrainproject.eu/#/collab/38996/nav/270508 , write the result to `openshift-prod-import.yaml`.
#. Create the project named `hbp-spatial-backend` on https://openshift.hbp.eu/
#. Log in to https://openshift.hbp.eu/ using the command-line ``oc`` tool, switch to the `hbp-spatial-backend` project
#. Import the object from your edited YAML file using ``oc create -f openshift-prod-import.yaml``
#. Create the needed Config Maps and Secrets
#. Upload the static data as explained above
#. Start the build. The deployment should follow automatically.

The production configuration has been exported to `openshift-prod-export.yaml` using ``oc get -o yaml --export is,bc,dc,svc,route,pvc`` (`status` information was manually stripped).
