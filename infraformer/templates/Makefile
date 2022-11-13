SHELL:=/bin/bash
project={{project}}
BASE_PATH=terraform/${stack}

init: check-vars
	cd ${BASE_PATH}/environments/${environ} && rm -rf .terraform/ \
		&& TF_DATA_DIR=$(shell pwd)/${BASE_PATH}/environments/${environ}/.terraform \
			terraform -chdir=../.. init \
			-backend=true \
			-backend-config=$(shell pwd)/${BASE_PATH}/environments/${environ}/backend.generated.tfvars

lint: check-vars
	cd ${BASE_PATH}/environments/${environ}/ \
		&& TF_DATA_DIR=$(shell pwd)/${BASE_PATH}/environments/${environ}/.terraform \
			terraform -chdir=../.. validate

plan: check-vars
	cd ${BASE_PATH}/environments/${environ}/ \
		&& TF_DATA_DIR=$(shell pwd)/${BASE_PATH}/environments/${environ}/.terraform \
			terraform -chdir=../.. plan \
				-var-file=$(shell pwd)/${BASE_PATH}/environments/${environ}/terraform.tfvars \
				-out=$(shell pwd)/${BASE_PATH}/environments/${environ}/.terraform/terraformout.plan \
				-var "region=${AWS_REGION}"

apply: check-vars
	cd ${BASE_PATH}/environments/${environ}/ \
		&& TF_DATA_DIR=$(shell pwd)/${BASE_PATH}/environments/${environ}/.terraform \
			terraform -chdir=../.. \
				apply \
				$(shell pwd)/${BASE_PATH}/environments/${environ}/.terraform/terraformout.plan

output: check-vars
	cd ${BASE_PATH}/environments/${environ}/ \
		&& TF_DATA_DIR=$(shell pwd)/$(BASE_PATH)/environments/${environ}/.terraform \
			terraform -chdir=../.. output

destroy: check-vars
	cd ${BASE_PATH}/stacks/$(1)/environments/${environ}/ \
		&& TF_DATA_DIR=$(shell pwd)/terraform/${AWS_REGION}/$(1)/environments/${environ}/.terraform \
			terraform -chdir=../.. \
				destroy \
				-var-file=$(shell pwd)/terraform/${AWS_REGION}/$(1)/environments/${environ}/terraform.tfvars \
				-var "region=${AWS_REGION}"

destroy-auto-approve: check-vars
	cd ${BASE_PATH}/environments/${environ}/ \
		&& TF_DATA_DIR=$(shell pwd)/${BASE_PATH}/environments/${environ}/.terraform \
			terraform -chdir=../.. \
				destroy -auto-approve \
				-var-file=$(shell pwd)/${BASE_PATH}/environments/${environ}/terraform.tfvars \
				-var "region=${AWS_REGION}"

check-vars:
	@echo "Checking if mandatory variables are setup..."
	@test ${project}
	@test ${environ}
	@test ${stack}

all:
	# loop stacks (excluding names starting with underscore)
	for d in $(shell ls ${BASE_PATH}| grep -v ^_); do \
		$(MAKE) -f $(shell pwd)/Makefile init stack="${stack}/$${d}" environ=${environ}; \
		$(MAKE) -f $(shell pwd)/Makefile plan stack="${stack}/$${d}" environ=${environ}; \
		$(MAKE) -f $(shell pwd)/Makefile apply stack="${stack}/$${d}" environ=${environ}; \
	done
