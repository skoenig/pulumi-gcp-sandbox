.PHONY: init
init: PROJECT := sandbox-$(shell date +%F-%H%M)
init:
	gcloud projects create $(PROJECT)
	pulumi stack init dev
	pulumi config set gcp:project $(PROJECT)
	pulumi config set gcp:zone europe-north1-a
	pulumi config set gcp:region europe-north1

.PHONY: install
install:
	pulumi up

.PHONY: clean
clean: PROJECT := $(shell pulumi config get gcp:project 2>/dev/null)
clean:
	pulumi stack rm dev -y
	gcloud projects delete $(PROJECT) --quiet

