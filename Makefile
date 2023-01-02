
DOCKER_CMD = docker run -it --rm \
		 -v ~/.config/gcloud:/root/.config/gcloud \
		 -v ~/.pulumi:/root/.pulumi \
		 -v $(PWD):/pulumi/projects \
		 -w /pulumi/projects \
		 -e PULUMI_CONFIG_PASSPHRASE_FILE=.passphrase \
		 pulumi/pulumi-python \
		 /bin/bash

.passphrase:
	@dd if=/dev/urandom bs=32 count=1 status=none | base64 > $@

.PHONY: init
init: PROJECT := sandbox-$(shell date +%F-%H%M)
init: .passphrase
ifndef BILLING_ACCOUNT
	$(error BILLING_ACCOUNT variable must be defined)
endif

	gcloud projects create $(PROJECT)
	gcloud alpha billing projects link $(PROJECT) --billing-account=$(BILLING_ACCOUNT)
	$(DOCKER_CMD) -c "pulumi login --local"
	$(DOCKER_CMD) -c "pulumi stack init dev"
	$(DOCKER_CMD) -c "pulumi config set gcp:project $(PROJECT)"
	$(DOCKER_CMD) -c "pulumi config set gcp:zone europe-west6-a"
	$(DOCKER_CMD) -c "pulumi config set gcp:region europe-west6"

.PHONY: install
install: .passphrase
	$(DOCKER_CMD) -c "pulumi up"

.PHONY: shell
shell: .passphrase
	$(DOCKER_CMD)

.PHONY: clean
clean:
	$(eval PROJECT := $(shell $(DOCKER_CMD) -c "pulumi config get gcp:project 2>/dev/null"))
	$(DOCKER_CMD) -c "pulumi stack rm dev --force -y"
	gcloud projects delete $(PROJECT) --quiet

