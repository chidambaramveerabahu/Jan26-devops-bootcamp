import requests
from requests.auth import HTTPBasicAuth

domain = "https://mansipandey.in"
post_endpoint = "/wp-json/wp/v2/posts"
user_endpoint = "/wp-json/wp/v2/users"


app_posts_url = domain + post_endpoint
app_users_url = domain + user_endpoint

def get_posts_data(url):
    response = requests.get(url)
    status_code = response.status_code
    print(f" status code: {status_code}")
    posts_data = response.json()

    for items in posts_data:
        title = items.get("title").get("rendered")
        date = items.get("date")
        content = items.get("content").get("rendered")
        print(f" title : {title} \n content: {content} \n date published: {date}")

def get_users_data(url):
    response = requests.get(url)
    users_data = response.json()
    status_code = response.status_code
    print(f" status code: {status_code}")

    for items in users_data:
        name = items.get("name")
        # email = items.get("email")
        print(f" name : {name}")

# get_posts_data(app_posts_url)
# get_users_data(app_users_url)

def create_post(url, auth, payload):
    response = requests.post(url, json=payload, auth=auth)
    status_code = response.status_code
    print(f" status code: {status_code}")
    return response.json()


post1 = {
    "title": "post from api - draft",
    "content": "Post content goes here",
    "status": "draft",  # or  'publish', "draft", "pending", "private"
}
username = "livingdevops@gmail.com"
app_password = "DBeV dfg hgd adsf YFPD"

auth=HTTPBasicAuth(username, app_password)
# create_post(app_posts_url, auth, post1)

def update_post(base_url, auth, post_id, payload):
    url = f"{base_url}/{post_id}"
    response = requests.post(url, json=payload, auth=auth)
    status_code = response.status_code
    print(f" status code: {status_code}")
    return response.json()


post_id = 54
update_payload = {
    "title": "post from api - draft - update post again",
    # "content": "Post content goes here - updated data",
    # "status": "draft",  # or 'publish', "draft", "pending", "private"
}
# update_post(app_posts_url, auth, post_id, update_payload)

def patch_post(base_url, auth, post_id):
    url = f"{base_url}/{post_id}"
    response = requests.patch(url, json={"status": "publish"}, auth=auth)
    print(f"status code: {response.status_code}")
    return response.json()

def delete_post(base_url, auth, post_id):
    url = f"{base_url}/{post_id}"
    response = requests.delete(url, auth=auth)
    print(f"status code: {response.status_code}")
    return response.json()

# patch_post(app_posts_url, auth, post_id)
# delete_post(app_posts_url, auth, post_id)