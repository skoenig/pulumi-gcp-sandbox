from datetime import datetime

import google.auth
from google.cloud import resourcemanager_v3

MAX_PROJECT_AGE = 86400  # seconds in a days


def get_organization_name():
    client = resourcemanager_v3.OrganizationsClient()
    request = resourcemanager_v3.SearchOrganizationsRequest()
    page_result = client.search_organizations(request=request)

    for result in page_result:
        return result.name

    return None


def get_project(project_id):
    client = resourcemanager_v3.ProjectsClient()
    request = resourcemanager_v3.SearchProjectsRequest(query=f"id:{project_id}")
    page_result = client.search_projects(request=request)

    for result in page_result:
        if result.project_id == project_id:
            return result

    return None


def check_project_age():
    credentials, project_id = google.auth.default()
    project = get_project(project_id)
    if not project:
        return f"project {project_id} not found", 404

    expiry_date = project.create_time.timestamp() + MAX_PROJECT_AGE * 7

    if expiry_date > int(datetime.now().timestamp()):
        return f'project {project_id} still within expiry range ({datetime.fromtimestamp(expiry_date):%F})'
    else:
        return f'project {project_id} expired ({datetime.fromtimestamp(expiry_date):%F}), deleting now'


def entry_point(request):
    return check_project_age()


if __name__ == "__main__":
    print(check_project_age())
