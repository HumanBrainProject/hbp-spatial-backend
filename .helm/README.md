# Deploying to production

This document is intended for a documentation on how hbp-spatial-backend can be deployed to a [kubernetes (k8s)](https://kubernetes.io/) cluster via [helm](https://helm.sh/).

Whilst the helm chart is produced with a rancher installation at https://rancher.tc.humanbrainproject.eu/ , the concept should be applicable to other k8s installations.

## Get started

1/ Create resources listed in adhoc (they may need to be adjusted based on the cluster you are working on) with:

```sh
kubectl apply -f .helm/adhoc/*.yaml
```
2/ cp the static files needed to startup the service:

```sh
pod_name=$(kubectl get pod -l app=busy-box -o jsonpath="{.items[0].metadata.name}")

for f in $(find /volatile/hbp-spatial-transformations-data/)
do

    kubectl cp $f $pod_name:/static-data/${f#/volatile/hbp-spatial-transformations-data/}
done
```

3/ Start application with `helm install prod .helm/hbp_spatial_backend`
