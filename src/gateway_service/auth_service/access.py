import os, requests


def login(request):
    auth = request.authorization
    if not auth:
        return None, ("Missing credentials", 401)

    basic_auth = (auth.username, auth.password)
    response = requests.get(
        f"http://{os.environ.get('SERVICE_AUTH_ADDRESS')}/login",
        auth=basic_auth
    )
    if response.status_code == 200:
        return response.text, None