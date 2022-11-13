# Infraformer

Terraform project generator.

It should create a Terraform project like this one: https://github.com/rtacconi/aws-msk-terraform/tree/master/terraform

Contents:
* terraform
* Makefile
* terraform/<region> (terraform/eu-west-1)
* terraform/modules
* terraform/<region>/<stack> (terraform/eu-west-1/10_network)
* terraform/<region>/<stack>/environments/<env-name> (terraform/eu-west-1/10_network/environments/dev)


Copyright 2022 - Recursive Labs LTD

## How to run it
Create a new project:

`python infraformer/main.py create project <project-name>`

Create a new stack:

`cd <project>`

`python infraformer/main.py create stack <stack-name> <region-name> <env-name>`
