# Events Organiser Ansible playbook

This playbook can be used to set up the servers with the appropriate software needed to run events organiser and parser. This playbook has been tested on CentOS 9, it might not work on other distributions.

## Prerequisites

A few community modules need to be installed before the Ansible playbook:
`ansible-galaxy collection install community.rabbitmq`
`ansible-galaxy collection install community.general`

Some roles will also need additional variables to be set (passwords/secrets etc) so that they can work. You can do that with Ansible Vault, creating it in the same directory as the playbook, or through some other means.

The list of required variables for each role is the following:
* mysql_install
    1. mysql_root_password
* rabbitmq_centos_install
    1. events_parser_rabbitmq_password

## Adding hosts
The VMs you want to set up have been split into two categories: controller and workers.
Controller is the VM which will set up Kubernetes, RabbitMQ, MySQL and other utilities. This will be the main server for events organiser.
Workers are VMs which will have Kubernetes installed and they be running different pods.

**********************Kubernetes role not implemented....

## Running the playbook

After setting up the hosts, you can run the following command with the playbook (if you used Ansible Vault): `ansible-playbook --ask-vault-password -i inventory/hosts playbook.yml`