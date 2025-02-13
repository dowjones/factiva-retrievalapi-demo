import requests as r

# Authentication functions

def get_bearer_token(client_id, username, password, auth_url):
    bearer_token = None

    id_token_payload = {
        "client_id": client_id,
        "username": username,
        "grant_type": "password",
        "connection": "service-account",
        "scope": "openid service_account_id",
        "password": password
    }

    token_id_resp = r.post(auth_url, data=id_token_payload)

    if token_id_resp.status_code == 200:
        response_body = token_id_resp.json()
        id_token = response_body['id_token']
        access_token = response_body['access_token']

        bearer_token_payload = {
            "client_id": client_id,
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "connection": "service-account",
            "scope": "openid pib",
            "access_token": access_token,
            "assertion": id_token
        }

        jwt_token_resp = r.post(auth_url, data=bearer_token_payload)

        if jwt_token_resp.status_code == 200:
            response_body = jwt_token_resp.json()
            bearer_token = response_body['access_token']

    return bearer_token
