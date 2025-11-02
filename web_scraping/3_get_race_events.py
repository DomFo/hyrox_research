import requests

# 1. Define the target URL
BASE_URL = "https://results.hyrox.com/season-8/index.php"

# 2. Define the parameters as a Python dictionary.
# The 'options[...]' structure from the URL is mapped to nested dictionaries in 'params'.
# requests handles the proper encoding (e.g., [b] becomes %5Bb%5D) for the URL.
params = {
    'content': 'ajax2',
    'func': 'getSearchFields',
    'options[b][lists][event_main_group]': '2025 Stuttgart',
    'options[b][lists][event]': '',
    'options[b][lists][ranking]': '',
    'options[b][lists][sex]': '',
    'options[b][lists][age_class]': '',
    'options[b][lists][nation]': '',
    'options[lang]': 'EN_CAP',
    'options[pid]': 'start'
}

# 3. Send the GET request
try:
    response = requests.get(BASE_URL, params=params)

    # 4. Check if the request was successful
    response.raise_for_status()

    # 5. Print the URL that was actually requested (for verification)
    print(f"✅ Successfully requested URL:\n{response.url}\n")

    # 6. Print the content of the response
    print("--- Server Response Content (likely HTML/JSON fragment) ---\n")
    print(response.text)
    json = response.json()
    events = json.get('branches', {}).get('lists', {}).get('fields', {}).get('event', {}).get('data', [])

    print("\n--- Extracted Events ---\n")
    for event in events:
        id = event.get('v')[0]
        name = event.get('v')[1]
        print(f"Event ID: {id}, Event Name: {name}")

    foo = 1

except requests.exceptions.HTTPError as errh:
    print(f"❌ HTTP Error: {errh}")
except requests.exceptions.RequestException as err:
    print(f"❌ An error occurred: {err}")
