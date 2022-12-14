import pulumi
from pulumi_gcp import projects, storage, cloudfunctions, serviceaccount, cloudscheduler

# Get stack config
config = pulumi.Config('gcp')
project = config.require('project')
region = config.require('region')

apis = {
    'compute.googleapis.com': None,
    'logging.googleapis.com': None,
    'cloudfunctions.googleapis.com': None,
    'cloudbuild.googleapis.com': None,
    'cloudresourcemanager.googleapis.com': None,
    'cloudscheduler.googleapis.com': None,
}


# enable needed APIs for Cloud Functions
def enable_service_apis(apis):
    for servicename in apis:
        api = projects.Service(
            servicename.split('.')[0],
            service=servicename,
            project=project,
            disable_dependent_services=True,
        )
        apis[servicename] = api


enable_service_apis(apis)

bucket = storage.Bucket('bucket', location=region)
py_bucket_object = storage.BucketObject(
    'python-zip',
    bucket=bucket.name,
    source=pulumi.asset.AssetArchive(
        {'.': pulumi.asset.FileArchive('./resourcemanager')}
    ),
)

py_function = cloudfunctions.Function(
    'python-func',
    runtime='python38',
    source_archive_bucket=bucket.name,
    source_archive_object=py_bucket_object.name,
    entry_point='entry_point',
    trigger_http=True,
    https_trigger_security_level='SECURE_ALWAYS',
    available_memory_mb=128,
    environment_variables={'PROJECT_LIFETIME': 7},
    service_account_email=f'resourcemanager@{project}.iam.gserviceaccount.com',
    opts=pulumi.ResourceOptions(
        depends_on=[
            apis['cloudfunctions.googleapis.com'],
            apis['cloudbuild.googleapis.com'],
            apis['cloudresourcemanager.googleapis.com'],
        ]
    ),
)

invoker = cloudfunctions.FunctionIamMember(
    'python-invoker',
    project=py_function.project,
    region=py_function.region,
    cloud_function=py_function.name,
    role='roles/cloudfunctions.invoker',
    member=f'serviceAccount:resourcemanager@{project}.iam.gserviceaccount.com',
)

service_account = serviceaccount.Account(
    'python-serviceaccount',
    account_id='resourcemanager',
)

for role in ['roles/resourcemanager.projectDeleter', 'roles/viewer']:
    projects.IAMMember(
        role.split('/')[-1],
        project=py_function.project,
        role=role,
        member=f'serviceAccount:resourcemanager@{project}.iam.gserviceaccount.com',
    )

job = cloudscheduler.Job(
    'python-scheduler',
    description='Resourcemanager Function Scheduler',
    schedule='01 * * * *',
    time_zone='Europe/London',
    http_target=cloudscheduler.JobHttpTargetArgs(
        http_method="GET",
        uri=py_function.https_trigger_url,
        oidc_token=cloudscheduler.JobHttpTargetOidcTokenArgs(
            service_account_email=service_account.email,
        ),
    ),
    opts=pulumi.ResourceOptions(
        depends_on=[
            apis['cloudscheduler.googleapis.com'],
        ],
    ),
)

pulumi.export('cloud_function_trigger_url', py_function.https_trigger_url)
