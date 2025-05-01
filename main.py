import requests
import json
import datetime

STATIC_PRICING = [
    {
        "service": "contactlensamazonconnect",
        "url": "https://aws.amazon.com/connect/pricing/"
    },
    {
        "service": "simspaceweaver",
        "pricing_url": "https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/simspaceweaver/USD/current/simspaceweaver-instances.json"
    }
]

def deepmerge(source, destination):
    for key, value in source.items():
        if isinstance(value, dict):
            node = destination.setdefault(key, {})
            deepmerge(value, node)
        else:
            destination[key] = value

    return destination

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
        existing_file = open(filename, "r")
        existing_contents = existing_file.read()
        existing_file.close()
    except FileNotFoundError:
        existing_contents = None
    return existing_contents

def modify_region_name(region_name, code_contents_raw):
    modified_region_name = region_name
    code_contents = json.loads(json.dumps(code_contents_raw))
    del code_contents["price"]
    del code_contents["rateCode"]
    if "RegionlessRateCode" in code_contents:
        del code_contents["RegionlessRateCode"]
    if len(code_contents.keys()) > 0:
        modifier_str = ""
        for k in code_contents.keys():
            if len(str(code_contents[k])) > 0:
                modifier_str += k + ": " + code_contents[k] + ", "
        if len(modifier_str) > 0:
            modified_region_name += " (" + modifier_str[:-2] + ")"

    return modified_region_name

def process_contents(service, sanitized_service_name, contents):
    contents_obj = json.loads(contents)

    save_file("raw/{}.json".format(sanitized_service_name), json.dumps(contents_obj, indent=4))

    if service == "AWSDirectConnect":
        contents_obj["sets"] = {} # special case: poor sets allocation

    processed_contents = {}
    for region_name in contents_obj["regions"].keys():
        for code_name in list(contents_obj["regions"][region_name].keys()): # copy as we'll be mutating
            if code_name not in contents_obj["regions"][region_name]: # already captured
                continue

            #print(service, region_name, code_name)
            if "RegionlessRateCode" in contents_obj["regions"][region_name][code_name] and contents_obj["regions"][region_name][code_name]["RegionlessRateCode"] == code_name:
                continue

            modified_code_name = code_name
            for set_name in contents_obj["sets"].keys():
                if code_name in contents_obj["sets"][set_name]:
                    new_modified_code_name = ""
                    for alt_code_name in list(contents_obj["regions"][region_name].keys()):
                        if contents_obj["regions"][region_name][code_name]["rateCode"] != contents_obj["regions"][region_name][alt_code_name]["rateCode"]:
                            continue
                        if "RegionlessRateCode" not in contents_obj["regions"][region_name][alt_code_name]:
                            continue
                        if contents_obj["regions"][region_name][alt_code_name]["RegionlessRateCode"] == alt_code_name:
                            continue
                        should_continue = False
                        for alt_set_name in contents_obj["sets"].keys():
                            if alt_code_name in contents_obj["sets"][alt_set_name]:
                                should_continue = True
                                break
                        if should_continue:
                            continue
                        new_modified_code_name += alt_code_name + ";"
                        del contents_obj["regions"][region_name][alt_code_name]
                    
                    if new_modified_code_name == "":
                        modified_code_name = "[" + set_name + "]"
                    else:
                        modified_code_name = "[" + set_name + "] " + new_modified_code_name[:-1]

            if modified_code_name not in processed_contents:
                processed_contents[modified_code_name] = {}
                if "RegionlessRateCode" in contents_obj["regions"][region_name][code_name] and contents_obj["regions"][region_name][code_name]["RegionlessRateCode"] in contents_obj["regions"][region_name]:
                    pass
                    #modified_region_name = modify_region_name("Default", contents_obj["regions"][region_name][code_name])
                    #processed_contents[modified_code_name][modified_region_name] = [
                    #    contents_obj["regions"][region_name][contents_obj["regions"][region_name][code_name]["RegionlessRateCode"]]["price"]
                    #]
                else:
                    pass
                    #print("Outlier: ", service, region_name, code_name)
            
            modified_region_name = modify_region_name(region_name, contents_obj["regions"][region_name][code_name])

            if modified_region_name not in processed_contents[modified_code_name]:
                processed_contents[modified_code_name][modified_region_name] = contents_obj["regions"][region_name][code_name]["price"]
            elif processed_contents[modified_code_name][modified_region_name] != contents_obj["regions"][region_name][code_name]["price"]:
                print("WARNING: Found existing and conflicting price for {} {} {}".format(service, modified_code_name, modified_region_name))
                processed_contents[modified_code_name][modified_region_name] += ";" + contents_obj["regions"][region_name][code_name]["price"]

    # remove optional set names
    for metric_name in list(processed_contents.keys()):
        if metric_name.startswith("[optional set name"):
            processed_contents[metric_name[metric_name.index("]")+2:]] = processed_contents[metric_name]
            del processed_contents[metric_name]

    existing_processed_contents = load_file("processed/{}.json".format(sanitized_service_name))
    if existing_processed_contents:
        existing_contents_obj = json.loads(existing_processed_contents)

        # compare the two objects
        if json.dumps(existing_contents_obj) != json.dumps(processed_contents):
            modified_services.append(sanitized_service_name)
            modified_service_detail[sanitized_service_name] = ""
            for metric_name in existing_contents_obj.keys():
                if metric_name not in processed_contents:
                    modified_service_detail[sanitized_service_name] += "\n  - Billing metric removed: {} 💥".format(metric_name)
            for metric_name in processed_contents.keys():
                if metric_name not in existing_contents_obj:
                    modified_service_detail[sanitized_service_name] += "\n  - Billing metric added: {} 💡".format(metric_name)
                else:
                    for region_name in processed_contents[metric_name].keys():
                        if region_name not in existing_contents_obj[metric_name]:
                            modified_service_detail[sanitized_service_name] += "\n  - Region removed for metric {}: {} 💥".format(metric_name, region_name)
                    for region_name in existing_contents_obj[metric_name].keys():
                        if region_name not in processed_contents[metric_name]:
                            modified_service_detail[sanitized_service_name] += "\n  - Region added for metric {}: {} 🌎".format(metric_name, region_name)
                        else:
                            if existing_contents_obj[metric_name][region_name] != processed_contents[metric_name][region_name]:
                                # parse prices
                                try:
                                    symbol = "$"
                                    if sanitized_service_name.endswith("-cn"):
                                        symbol = "¥"

                                    old_price = float(existing_contents_obj[metric_name][region_name])
                                    new_price = float(processed_contents[metric_name][region_name])
                                    if old_price < new_price:
                                        modified_service_detail[sanitized_service_name] += "\n  - Price increased: {} {}  **{}{}** → **{}{}** 🤑".format(metric_name, region_name, symbol, old_price, symbol, new_price)
                                    elif old_price > new_price:
                                        modified_service_detail[sanitized_service_name] += "\n  - Price decreased: {} {}  **{}{}** → **{}{}** 💸".format(metric_name, region_name, symbol, old_price, symbol, new_price)
                                except:
                                    modified_service_detail[sanitized_service_name] += "\n  - Price changed: {} {} 💰".format(metric_name, region_name)
    else:
        new_services.append(sanitized_service_name)

    return processed_contents


###

services = []
not_found = []
modified_services = []
modified_service_detail = {}
new_services = []

service_list_obj = {}

out = ""

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
            processed_contents = process_contents(service, sanitized_service_name, contents)

            cncontents = get_url_contents("https://b0.p.awsstatic.cn/pricing/2.0/meteredUnitMaps/{}/CNY/current/{}.json".format(sanitized_service_name, sanitized_service_name))
            if cncontents:
                processed_contents_cn = process_contents(service, sanitized_service_name + "-cn", cncontents)
                processed_contents = deepmerge(processed_contents, processed_contents_cn)
            
            save_file("processed/{}.json".format(sanitized_service_name), json.dumps(processed_contents, indent=4))
        else:
            not_found.append(sanitized_service_name)

    if len(modified_services) + len(new_services) > 0:
        out += "## {}\n\n".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        if len(new_services) > 0:
            out += "**New services:**\n"
            for service in new_services:
                out += "\n- [{}](processed/{}.json) 🚀".format(service, service)
            out += "\n\n"
        if len(modified_services) > 0:
            out += "**Modified services:**\n"
            for service in modified_services:
                out += "\n- [{}](processed/{}.json)".format(service, service)
                out += "{}\n".format(modified_service_detail[service])
            out += "\n"

    # read readme file
    with open("README.md", "r") as readme_file:
        out += readme_file.read().split("## Not included services")[0]

    out += "## Not included services\n\n- {}".format('\n- '.join(not_found))

    save_file("README.md", out)