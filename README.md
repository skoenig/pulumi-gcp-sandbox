# Pulumi GCP Sandbox

This is a simple Pulumi setup for creating GCP sandbox projects.

This repo includes a simple Pulumi program as well as a Makefile to easily create GCP 'throwaway'-projects that you can use for testing and later clean up leftover resources so they don't get billed.

Instead of the external Pulumi service, the local file service is used, so you don't need to create an account on https://app.pulumi.com/.

In addition, a Cloud Function is installed that is executed regularly to check whether the project has exceeded a certain expiry date (configurable via the environment variable `PROJECT_LIFETIME`) and automatically deletes the project if it is too old.

## Usage
1. Create the GCP project linked to your billing account and initialize Pulumi: `BILLING_ACCOUNT="012345-DEFGH8-67890A" make init`
2. Deploy the Pulumi stack: `make install`
3. Do your changes to `__main__.py` and repeat step 2 to deploy them.

To delete the Pulumi stack and GCP project without waiting for its expiry run `make clean`.
