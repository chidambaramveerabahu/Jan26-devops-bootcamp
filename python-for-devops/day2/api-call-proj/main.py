import requests

app_posts_url = "https://mansipandey.in/wp-json/wp/v2/posts"

# response = requests.get(app_posts_url)

# print(type(response))
# print(dir(response))
#  'content', 'cookies', 'elapsed', 'encoding', 'headers', 'history', 'is_permanent_redirect', 'is_redirect', 'iter_content', 'iter_lines', 'json', 'links', 'next', 'ok', 'raise_for_status', 'raw', 'reason', 'request', 'status_code', 'text', 'url']
# print(response.text)
# print(type(response.text))
# import json
# print(type(json.loads(response.text)))

# print(type(response.json()))

# posts_data = response.json()
# print(len(posts_data))
# print(posts_data[0])

# print(posts_data[1].get("title").get("rendered"))
# print(posts_data[1].get("date"))
# print(posts_data[1].get("content").get("rendered"))

def get_posts_data(post_url):
    response = requests.get(app_posts_url).json()

    for items in response:
        title = items.get("title").get("rendered")
        date = items.get("date")
        content = items.get("content").get("rendered")
        print(title, date, content)

get_posts_data(app_posts_url)