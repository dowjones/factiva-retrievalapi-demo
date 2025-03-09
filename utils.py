import requests as r
import json
import copy
from google import genai
from google.genai import types
from IPython.display import Markdown

# Authentication functions

def get_bearer_token(client_id, username, password, auth_url) -> str:
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


def print_full_chunks(chunks_list):
    for article in chunks_list:
        display(Markdown(f"### {article['attributes']['headline']['main']['text']}"))
        display(Markdown(f"**{article['meta']['source']['name']}** - {article['attributes']['publication_date']} - {article['meta']['original_doc_id']} - Lang: {article['meta']['language']['code']}"))
        display(Markdown(f"{article['attributes']['snippet']['content'][0]['text']} {article['attributes']['content'][0]['text']}"))
        display(Markdown(f"---"))


def print_partial_chunks(chunks_list):
    for article in chunks_list:
        display(Markdown(f"### {article['attributes']['headline']['main']['text']}"))
        display(Markdown(f"**{article['meta']['source']['name']}** - {article['attributes']['publication_date']} - {article['meta']['original_doc_id']} - Lang: {article['meta']['language']['code']}"))
        display(Markdown(f"{article['attributes']['snippet']['content'][0]['text']} {article['attributes']['content'][0]['text']})"[:150] + "..."))
        display(Markdown(f"---"))


def print_full_llm_prompt(llm_prompt):
    print(json.dumps(llm_prompt, indent=4))


def print_partial_llm_prompt(llm_prompt):
    llm_prompt_copy = copy.deepcopy(llm_prompt)
    for article in llm_prompt_copy['articles']:
        article['content'] = article['content'][:150] + "..."
    print(json.dumps(llm_prompt_copy, indent=4))
    

def gemini_generate(gemini_prompt, gproject, glocation) -> str:
  
    client = genai.Client(
        vertexai=True,
        project=gproject,
        location=glocation,
    )

    text1 = types.Part.from_text(text=json.dumps(gemini_prompt))

    model = "gemini-2.0-flash-001"
    contents = [
        types.Content(
        role="user",
        parts=[
            text1
          ]
        )
    ]
    
    generate_content_config = types.GenerateContentConfig(
        temperature = 0.2,
        top_p = 0.95,
        max_output_tokens = 8192,
        response_modalities = ["TEXT"],
        safety_settings = [types.SafetySetting(
        category="HARM_CATEGORY_HATE_SPEECH",
        threshold="OFF"
        ),types.SafetySetting(
        category="HARM_CATEGORY_DANGEROUS_CONTENT",
        threshold="OFF"
        ),types.SafetySetting(
        category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
        threshold="OFF"
        ),types.SafetySetting(
        category="HARM_CATEGORY_HARASSMENT",
        threshold="OFF"
        )],
    )

    response = ""
    for chunk in client.models.generate_content_stream(
        model = model,
        contents = contents,
        config = generate_content_config,
        ):
        response += chunk.text
        
    return response
