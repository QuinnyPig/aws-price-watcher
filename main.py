import requests
import json


def get_url_contents(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        return None
    
def save_file(filename, contents):
    try:
        with open(filename, 'w') as file:
            file.write(contents)
    except IOError as e:
        print(f"Error saving the file: {e}")


services = []
not_found = []

service_list_obj = {}

service_list = get_url_contents("https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/index.json")
if service_list:
    save_file("raw/_service_list.json", service_list)
    try:
        service_list_obj = json.loads(service_list)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")

    for service in service_list_obj["offers"].keys():
        sanitized_service_name = service.lower().removeprefix("amazon").removeprefix("aws")
        contents = get_url_contents(f"https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/{sanitized_service_name}/USD/current/{sanitized_service_name}.json")
        if contents:
            save_file(f"raw/{sanitized_service_name}.json", contents)
        else:
            not_found.append(sanitized_service_name)
            print(f"Service {sanitized_service_name} not found.")

