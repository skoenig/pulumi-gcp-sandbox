import pulumi
from pulumi_gcp import compute, projects

# Get stack config
config = pulumi.Config('gcp')
project = config.require('project')

service_compute = projects.Service(
    'compute',
    project=project,
    disable_dependent_services=True,
    service='compute.googleapis.com',
)

compute_network = compute.Network(
    'network',
    auto_create_subnetworks=True,
)

compute_firewall = compute.Firewall(
    'firewall',
    network=compute_network.self_link,
    allows=[
        compute.FirewallAllowArgs(
            protocol='tcp',
            ports=['22', '80'],
        )
    ],
    source_ranges=['0.0.0.0/0'],
)

# A simple bash script that will run when the webserver is initalized
startup_script = '''#!/bin/bash
echo 'Hello, World!' > index.html
nohup python -m SimpleHTTPServer 80 &'''

instance_addr = compute.address.Address('address')
compute_instance = compute.Instance(
    'instance',
    machine_type='f1-micro',
    metadata_startup_script=startup_script,
    boot_disk=compute.InstanceBootDiskArgs(
        initialize_params=compute.InstanceBootDiskInitializeParamsArgs(
            image='debian-cloud/debian-9-stretch-v20181210'
        )
    ),
    network_interfaces=[
        compute.InstanceNetworkInterfaceArgs(
            network=compute_network.id,
            access_configs=[
                compute.InstanceNetworkInterfaceAccessConfigArgs(
                    nat_ip=instance_addr.address
                )
            ],
        )
    ],
    service_account=compute.InstanceServiceAccountArgs(
        scopes=['https://www.googleapis.com/auth/cloud-platform'],
    ),
    opts=pulumi.ResourceOptions(depends_on=[service_compute]),
)

pulumi.export('instance_address', instance_addr.address)
