SHELL:=/bin/bash
LAYERS=terraform/layers


create-state: check-vars
	cd terraform/00_state \
		&& terraform init \
		&& terraform apply -auto-approve -var prefix="${project}-${environ}"

init: check-vars
ifdef layer
	@echo 'layer is defined'
	$(call tf_init,$$layer)
else
	@echo 'you must pass a layer, i.e.: make layer=10_network  init'
endif

lint: check-vars
ifdef layer
	@echo 'layer is defined'
	$(call tf_lint,$$layer)
else
	@echo 'you must pass a layer, i.e.: make layer=10_network  init'
endif

plan: check-vars
ifdef layer
	@echo 'toto is defined'
else
	@echo 'you must pass a layer, i.e.: make layer=10_network  plan'
endif
	$(call tf_plan,$$layer)

apply: check-vars
ifdef layer
	@echo 'toto is defined'
else
	@echo 'you must pass a layer, i.e.: make layer=10_network  apply'
endif
	$(call tf_apply,$$layer)

destroy: check-vars
ifdef layer
	@echo 'toto is defined'
else
	@echo 'you must pass a layer, i.e.: make layer=10_network destroy'
endif
	$(call tf_destroy,$$layer)

check-vars:
	echo "Checking if project is setup..."
	@test ${project}
	echo "Checking if environ is setup..."
	@test ${environ}
	echo "Checking if AWS_REGION is setup..."
	@test ${AWS_REGION}
	echo "Checking if AWS_REGION is setup..."
	@test ${AWS_REGION}

define tf_init
	cd terraform/layers/$(1)/environments/${environ} && rm -rf .terraform/ \
		&& TF_DATA_DIR=$(shell pwd)/terraform/layers/$(1)/environments/${environ}/.terraform \
			terraform -chdir=../.. init \
			-backend=true \
			-backend-config=$(shell pwd)/terraform/layers/$(1)/environments/${environ}/backend.generated.tfvars
endef

define tf_lint
	cd terraform/layers/$(1)/environments/${environ}/ \
		&& TF_DATA_DIR=$(shell pwd)/terraform/layers/$(1)/environments/${environ}/.terraform \
			terraform -chdir=../.. validate
endef

define tf_plan
	cd terraform/layers/$(1)/environments/${environ}/ \
		&& TF_DATA_DIR=$(shell pwd)/terraform/layers/$(1)/environments/${environ}/.terraform \
			terraform -chdir=../.. plan \
				-var-file=$(shell pwd)/terraform/layers/$(1)/environments/${environ}/terraform.tfvars \
				-out=$(shell pwd)/terraform/layers/$(1)/environments/${environ}/.terraform/terraformout.plan
endef

define tf_apply
	cd terraform/layers/$(1)/environments/${environ}/ \
		&& TF_DATA_DIR=$(shell pwd)/terraform/layers/$(1)/environments/${environ}/.terraform \
			terraform -chdir=../.. \
				apply \
				$(shell pwd)/terraform/layers/$(1)/environments/${environ}/.terraform/terraformout.plan
endef

define tf_destroy
	cd terraform/layers/$(1)/environments/${environ}/ \
		&& TF_DATA_DIR=$(shell pwd)/terraform/layers/$(1)/environments/${environ}/.terraform \
			terraform -chdir=../.. \
				destroy -auto-approve \
				-var-file=$(shell pwd)/terraform/layers/$(1)/environments/${environ}/terraform.tfvars
endef


apply_layers:
	# loop layers (excluding names starting with underscore)
	for d in $(shell ls ${LAYERS}| grep -v ^_); do \
	  echo running layer $${d}; \
		cd $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST)))); \
		$(call tf_init,$${d});    \
		cd $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST)))); \
		$(call tf_plan,$${d});    \
		cd $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST)))); \
		$(call tf_apply,$${d});   \
	done

create-layer:
ifdef layer
	@echo "creating backend for ${layer} layer, environment ${environ}"
	@python main.py create-layer eu-west-1 $${project} $${environ} $${layer}
else
	@echo 'you must pass a layer, i.e.: make layer=10_network destroy'
endif
