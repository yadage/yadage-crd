
buildandload:
	docker build -t yadage/crdctrl:latest -f images/crdctrl/Dockerfile images/crdctrl; kind load docker-image yadage/crdctrl:latest

restartctrl:
	 kubectl get pods -n yadage -o name|xargs kubectl delete -n yadage

cleanup:
	kubectl delete -f examples/wflow_mg.yml;kubectl get pods -o name|xargs kubectl delete;kubectl get jobs -o name|xargs kubectl delete;
