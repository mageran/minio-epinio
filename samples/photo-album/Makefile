

APPNAME ?= test-access-minio
TARGET ?= test-minio-namespace 
SERVICENAME ?= devMinio

CATALOG_SERVICE = minio-service-dev


MINIO_URL ?= https://minio.127.0.0.1.sslip.io

define create-service
	@if [ -z "$(1)" -o -z "$(2)" ]; then echo "*** macro \"$(0)\" needs 2 arguments"; exit -1; fi
	@(epinio service show $(2) > /dev/null && echo "$(1) service already created.") || epinio service create $(1) $(2)
endef

define get-s3-bucket-name
	conf=$$(epinio app show $(APPNAME) | grep $(CATALOG_SERVICE) | awk '{ print $$5 }'); \
	$(1)_name=$$(epinio configuration show $${conf} | grep s3_bucket_name | awk '{ print $$4 }'); \
	echo $$$(1)_name
endef

all:
	@echo "*** use explicit target"

deploy: create-app epinio-environment-yml build-ui-client
	epinio app push -n $(APPNAME)

target:
	@epinio namespace show $(TARGET) > /dev/null || epinio namespace create $(TARGET)
	epinio target $(TARGET)

epinio-environment-yml: environment_dev.yml
	cat environment_dev.yml | grep -v '#dev' > environment.yml

create-service-instances:
	$(call create-service, $(CATALOG_SERVICE), $(SERVICENAME))

delete-service-instance:
	-epinio service delete $(SERVICENAME)

npm-install-ui-client:
	cd client; npm install

build-ui-client: npm-install-ui-client
	cd client; npm run build

create-app: delete-app create-service-instances
	epinio app create $(APPNAME) && \
	epinio service bind $(SERVICENAME) $(APPNAME)

delete-app: target
	-epinio app delete $(APPNAME)

check-app-exists:
	epinio app show $(APPNAME) > /dev/null

show-app-bucket-name: check-app-exists
	$(call get-s3-bucket-name)

check-aws:
	@command -v aws > /dev/null || (echo '"aws" is not installed'; exit -1)

upload-to-bucket: check-aws check-app-exists
	@if [ -z "$${FILE}" ]; then printf "use like this:\n\n  FILE=foo make upload-to-bucket\n\n"; exit -1; fi
	$(call get-s3-bucket-name, bucket); \
	aws --no-verify-ssl --endpoint-url $(MINIO_URL) s3 cp $${FILE} s3://$${bucket_name}