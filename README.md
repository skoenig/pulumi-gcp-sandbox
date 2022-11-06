# Pulumi GCP Sandbox

This is a simple Pulumi setup for creating GCP sandbox projects.

This repo includes a simple Pulumi program as well as a Makefile to easily create GCP 'throwaway'-projects that you can use for testing and later clean up leftover resources so they don't get billed.

Instead of the external Pulumi service, the local file service is used, so you don't need to create an account on https://app.pulumi.com/.

