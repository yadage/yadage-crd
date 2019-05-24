Kubernetes CRD for yadage workflows

[![Build Status](https://travis-ci.com/yadage/yadage-crd.svg?branch=master)](https://travis-ci.com/yadage/yadage-crd)


on a checkout

```
helm install metacontroller --namespace metacontroller
helm install \
--namespace yadage \
-f ../helm_values/ci.yml \
--set secrets.username=XXXX \
--set secrets.password=YYYY \
--set imageCredentials.username=ZZZZ \
--set imageCredentials.password=AAAA \
yadage
```

from the release

```
helm repo add yadage https://yadage.github.io/yadage-crd
helm repo update
helm install yadage/metacontroller --namespace metacontroller
helm install \
--namespace yadage \
-f ../helm_values/ci.yml \
--set secrets.username=XXXX \
--set secrets.password=YYYY \
--set imageCredentials.username=ZZZZ \
--set imageCredentials.password=AAAA \
yadage/yadage
```