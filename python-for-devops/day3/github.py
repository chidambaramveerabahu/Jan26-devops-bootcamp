import requests
import os

domain = "https://api.github.com"
username = "akhileshmishrabiz"
repo_endpoint  = f"{domain}/users/{username}/repos"
create_repo_endpoint  = f"{domain}/user/repos"




def list_repos_names(repo_endpoint):
    response = requests.get(repo_endpoint)
    repos = response.json()
    total_repos = len(repos)
    print(f"Total repos: {total_repos}")
    # for repo in repos:
    #     print(repo["name"])
    #     print(repo.get('full_name'))

def list_repos_names_with_pagination(repo_endpoint):
    response = requests.get(
        repo_endpoint,
        
        params={
            "per_page": 7,
            "page": 2
        }
        )
    repos = response.json()
    total_repos = len(repos)
    print(f"Total repos: {total_repos}")
    for repo in repos:
        print(repo["name"])
# list_repos_names_with_pagination(repo_endpoint)

def create_repo(create_repo_endpoint, token, payload):
    response = requests.post(create_repo_endpoint, 
    json=payload,
     headers={"Authorization": f"Bearer {token}"}
     )
    print(response.status_code)


# export github_token="ghp_AlsdgsdgdqgdgXHns05XkIup3FiETv"
github_token=os.getenv("github_token")
payload = {
    "name": "janbootcamp-python-demo",
    "description": "This is a janbootcamp python repo only for demo purpose",
    "private": False
}
# create_repo(create_repo_endpoint, github_token, payload)

repo_id = "1223863054"
repo_name = "janbootcamp-python-demo"

def delete_repo(delete_repo_endpoint, token):
    response = requests.delete(delete_repo_endpoint, 
    headers={"Authorization": f"Bearer {token}"}
)
    print(response.status_code)
    print(response.json())

delete_repo_endpoint  = f"{domain}/repos/{username}/{repo_name}"
delete_repo(delete_repo_endpoint, github_token)