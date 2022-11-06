export PULUMI_CONFIG_PASSPHRASE_FILE=.passphrase

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
	pulumi login --local
	pulumi stack init dev
	pulumi config set gcp:project $(PROJECT)
	pulumi config set gcp:zone europe-north1-a
	pulumi config set gcp:region europe-north1

.PHONY: install
install: .passphrase
	pulumi up

.PHONY: clean
clean: PROJECT := $(shell pulumi config get gcp:project 2>/dev/null)
clean:
	pulumi stack rm dev --force -y
	gcloud projects delete $(PROJECT) --quiet

