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
        print("Error saving the file: {}".format(e))

def load_file(filename):
    existing_contents = None
    try:
        existing_file = open("raw/{}.json".format(sanitized_service_name), "r")
        existing_contents = existing_file.read()
        existing_file.close()
    except FileNotFoundError:
        existing_contents = None
    return existing_contents


services = []
not_found = []
modified_services = []
new_services = []

service_list_obj = {}

service_list = get_url_contents("https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/index.json")
if service_list:
    save_file("raw/_service_list.json", service_list)
    try:
        service_list_obj = json.loads(service_list)
    except json.JSONDecodeError as e:
        print("Error decoding JSON: {}".format(e))

    for service in service_list_obj["offers"].keys():
        sanitized_service_name = service.lower().removeprefix("amazon").removeprefix("aws")
        contents = get_url_contents("https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/{}/USD/current/{}.json".format(sanitized_service_name, sanitized_service_name))
        if contents:
            contents_obj = json.loads(contents)
            existing_contents = load_file(sanitized_service_name)
            if existing_contents:
                existing_contents_obj = json.loads(existing_contents)

                # compare the two objects
                if existing_contents_obj != contents_obj:
                    modified_services.append(sanitized_service_name)
            else:
                new_services.append(sanitized_service_name)
            
            save_file("raw/{}.json".format(sanitized_service_name), contents)
        else:
            not_found.append(sanitized_service_name)

    print("## Latest Changes\n\n")
    print("**New services:**\n\n- {}".format('\n- '.join(new_services)))
    print("\n**Modified services:**\n\n- {}".format('\n- '.join(modified_services)))
    print("\n**Not found services:**\n\n- {}".format('\n- '.join(not_found)))
