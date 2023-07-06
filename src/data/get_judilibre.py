import pandas as pd
import requests
import time
import urllib

oauth_url = "https://sandbox-oauth.piste.gouv.fr/api/oauth/token"

# Create the API URL
api_url = "{base_url}?query={query}&page_size={page_size}&operator={operator}&page={page}&jurisdiction={jurisdiction}"
def create_url(page, jurisdiction):
    parameters["page"] = page
    parameters["jurisdiction"] = jurisdiction
    return api_url.format(base_url=base_url, **parameters)

def get_bearer_token():
    headers = {
    "Content-Type": "application/x-www-form-urlencoded"
    }
    data = 'grant_type=client_credentials&client_id=f6727907-dc80-4837-8344-cf2d50b76142&client_secret=4000fa75-46ab-4d3f-807a-f7aa956828f6&scope=openid'
    response = requests.post(oauth_url, headers=headers, data=data)
    if response.status_code == 200:
        print("Access token fetched successfully!")
        token_info = response.json()
        access_token = token_info["access_token"]
        expires_in = token_info["expires_in"]
        return access_token, expires_in
    else:
        print(response)
        print("Failed to fetch access token.")
        return None, None

def call_api(url, token, max_retries=5):
    headers = {"Authorization": "Bearer {}".format(token)}
    
    for _ in range(max_retries):
        response = requests.get(url, headers=headers)
        if response.status_code != 500:  # If the status code is not 500, we break the loop and return the response
            break
        print("Got a 500 status code. Retrying...")
        time.sleep(1)  # Optionally, add a small delay before retrying
    
    return response

token, expires_in = get_bearer_token()
start_time = time.time()

ids = []

base_url = "https://sandbox-api.piste.gouv.fr/cassation/judilibre/v1.0/search"
parameters = {
    "query": "rupture brutale",
    "page_size": 50,
    "operator": "exact",
    "jurisdiction": {},
    "page": {}  # This will be formatted later in the script
}

jurisdictions = ["cass", "ca"]
for jurisdiction in jurisdictions:
    for page in range(200):  # Assuming you want to start from page 1
        url = create_url(page, jurisdiction)

        if token is None or time.time() - start_time >= expires_in - 300:      
            token, expires_in = get_bearer_token()
            start_time = time.time()
        
        if token is not None:
            response = call_api(url, token)
            if response.status_code == 200:
                print(f"Call to {url} successful!")
                try:
                    ids.extend([row["id"] for row in response.json()["results"]])
                except:
                    print(f"Failed to get ids for {url}")
            else:
                print(f"Call to {url} failed with status code: {response.status_code}")

decision_url = "https://sandbox-api.piste.gouv.fr/cassation/judilibre/v1.0/decision?id={}"

clean_ids = [id for id in ids if id is not None]

decisions = []
for clean_id in clean_ids:

  url = decision_url.format(urllib.parse.quote(str(clean_id)))

  if token is None or time.time() - start_time >= expires_in - 300:      
      token, expires_in = get_bearer_token()
      start_time = time.time()
  
  if token is not None:
      response = call_api(url, token)
      if response.status_code == 200:
          print(f"Call to {url} successful!")
          try:
            decisions.append(response.json())
          except:
            print(f"Failed to get ids for {url}")
      else:
          print(f"Call to {url} failed with status code: {response.status_code}")

df=pd.DataFrame(decisions)
df.to_csv("data/raw/decisions.csv")