
# you can customize MINIO_HOST and INGRESS_NAME
MINIO_HOST   ?= minio.127.0.0.1.sslip.io
INGRESS_NAME = minio-passthrough

MINIO_KEY    = $$(kubectl get secrets/minio-creds -n epinio -o=go-template='{{index .data "accesskey" | base64decode}}')
MINIO_SECRET = $$(kubectl get secrets/minio-creds -n epinio -o=go-template='{{index .data "secretkey" | base64decode}}')
AWS_ENDPOINT_URL = https://$(MINIO_HOST)


disable-default:
	@echo "*** please specify a target"

# --------- targets for exposing minio instance ---------

expose-minio:
	@printf '{"apiVersion":"traefik.containo.us/v1alpha1","kind":"IngressRouteTCP","metadata":{"name":"%s","namespace":"epinio"},"spec":{"entryPoints":["websecure"],"routes":[{"match":"HostSNI(`%s`)","services":[{"name":"minio","port":9000}]}],"tls":{"passthrough":true}}}' \
	$(INGRESS_NAME) $(MINIO_HOST) | kubectl create -f -
	@echo "successfully exposed minio on endpoint $(AWS_ENDPOINT_URL)."

unexpose-minio:
	-kubectl -n epinio delete ingressroutetcp $(INGRESS_NAME)


# check for 'aws' command for command-line access to s3
check-aws:
	@command -v aws > /dev/null || (echo '"aws" is not installed'; exit -1)

aws-setup: check-aws
	@aws configure set aws_access_key_id $(MINIO_KEY)
	@aws configure set aws_secret_access_key $(MINIO_SECRET)
	@aws configure set default.region us-east-1
	echo "access minio s3 like this:\n\n    aws --no-verify-ssl --endpoint-url $(AWS_ENDPOINT_URL) s3 <s3-command>\n"

aws-test: aws-setup
	@echo "testing access to minio-s3; running 's3 ls' command..."
	aws --no-verify-ssl --endpoint-url $(AWS_ENDPOINT_URL) s3 ls


# --------- targets for epinio minio service creation ---------

SERVICE_DEFINITION = minio-service.json
SERVICE_NAME = $$(jq '.metadata.name' < $(SERVICE_DEFINITION) | tr -d '"')

register-minio-catalog-service: $(SERVICE_DEFINITION)
	kubectl apply -f $(SERVICE_DEFINITION)
	@echo "service \"$(SERVICE_NAME)\" added to epinio service catalog"

delete-minio-service-from-catalog:
	kubectl delete services.application.epinio.io -n epinio $(SERVICE_NAME)
	@echo "service \"$(SERVICE_NAME)\" removed from epinio service catalog"
