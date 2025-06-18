import requests
import json
import datetime
import time

STATIC_PRICING = [
    # {
    #     "service": "contactlensamazonconnect",
    #     "url": "https://aws.amazon.com/connect/pricing/",
    #     "dimensions": [
    #         {
    #             "selector": "#Amazon_Connect_with_unlimited_AI ~ div.lb-tbl > table > tbody > tr:nth-child(n+2) > td:nth-child(2)",
    #             "type": "metric",
    #             "title_prefix_selector": "#Amazon_Connect_with_unlimited_AI",
    #             "name_selector": "#Amazon_Connect_with_unlimited_AI ~ div.lb-tbl > table > tbody > tr:nth-child(n+2) > td:nth-child(1)",
    #             "regex": "^\\$?([0-9.]+)"
    #         },
    #         {
    #             "selector": "",
    #             "type": "metric",
    #             "title_prefix_selector": "#Amazon_Connect_with_individual_features + div > div > div > p > b",
    #             "name_selector": "#Amazon_Connect_with_unlimited_AI ~ div.lb-tbl > table > tbody > tr:nth-child(n+2) > td:nth-child(1)",
    #             "regex": "^\\$?([0-9.]+)"
    #         }
    #     ]
    # },
    {
        "service": "m2",
        "url": "https://aws.amazon.com/mainframe-modernization/pricing/",
        "dimensions": [
            {
                "master_selector": "#On-demand_pricing ~ div.lb-tbl",
                "selector": "table > tbody > tr:nth-child(n+1) > td:nth-child(2) > p",
                "unit_selector": "table > tbody > tr:nth-child(n+1) > td:nth-child(2) > p",
                "type": "metric",
                "title_prefix_selector": "#On-demand_pricing ~ div.lb-rtxt > p > b",
                "name_selector": "table > tbody > tr:nth-child(n+1) > td:nth-child(1) > p",
                "regex": "^\\$?([0-9.]+)",
                "unit_regex": "[pP]er (.+)"
            }
        ]
    },
    {
        "service": "simspaceweaver",
        "pricing_url": "https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/simspaceweaver/USD/current/simspaceweaver-instances.json"
    },
    {
        "service": "memorydb",
        "pricing_url": "https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/memorydb/USD/current/memorydb-instance.json"
    },
    {
        "service": "private5g",
        "url": "https://aws.amazon.com/private5g/pricing/",
        "prereqs": [
            {
                "selector": "#Pricing + div > table > tbody > tr:nth-child(1) > td:nth-child(1) > b",
                "expected_value": "Name"
            },
            {
                "selector": "#Pricing + div > table > tbody > tr:nth-child(1) > td:nth-child(2) > b",
                "expected_value": "60-day commitment and post commitment"
            },
            {
                "selector": "#Pricing + div > table > tbody > tr:nth-child(1) > td:nth-child(3) > b",
                "expected_value": "1-year commitment"
            },
            {
                "selector": "#Pricing + div > table > tbody > tr:nth-child(1) > td:nth-child(4) > b",
                "expected_value": "3-year commitment"
            },
            {
                "selector": "#Pricing + div > table > tbody > tr:nth-child(1) > td:nth-child(4) > b",
                "expected_value": "Regions"
            }
        ],
        "dimensions": [
            {
                "selector": "#Pricing + div > table > tbody > tr:nth-child(2) > td:nth-child(2) > b",
                "type": "metric",
                "name": "60-day commitment and post commitment",
                "name_prefix_selector": "#Pricing + div > table > tbody > tr:nth-child(2) > td:nth-child(1) > b",
                "region_list_selector": "#Pricing + div > table > tbody > tr:nth-child(2) > td:nth-child(5) > b",
                "unit": "hour",
                "regex": "^\\$?([0-9.]+)"
            },
            {
                "selector": "#Pricing + div > table > tbody > tr:nth-child(2) > td:nth-child(3) > b",
                "type": "metric",
                "name": "1-year commitment",
                "name_prefix_selector": "#Pricing + div > table > tbody > tr:nth-child(2) > td:nth-child(1) > b",
                "region_list_selector": "#Pricing + div > table > tbody > tr:nth-child(2) > td:nth-child(5) > b",
                "unit": "hour",
                "regex": "^\\$?([0-9.]+)"
            },
            {
                "selector": "#Pricing + div > table > tbody > tr:nth-child(2) > td:nth-child(4) > b",
                "type": "metric",
                "name": "3-year commitment",
                "name_prefix_selector": "#Pricing + div > table > tbody > tr:nth-child(2) > td:nth-child(1) > b",
                "region_list_selector": "#Pricing + div > table > tbody > tr:nth-child(2) > td:nth-child(5) > b",
                "unit": "hour",
                "regex": "^\\$?([0-9.]+)"
            }
        ]
    },
    {
        "service": "honeycode",
        "skip": True
    },
    {
        "service": "ecrpublic",
        "skip": True
    },
    {
        "service": "rds-storage",
        "pricing_url": "https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/rds/USD/current/rds-storage.json"
    },
    {
        "service": "rds-aurora-storage",
        "pricing_url": "https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/rds/USD/current/rds-aurora-storage.json"
    },
    {
        "service": "rds-aurora-ondemand",
        "pricing_url": "https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/rds/USD/current/rds-aurora-ondemand.json"
    },
    {
        "service": "rds-db2-ondemand",
        "pricing_url": "https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/rds/USD/current/rds-db2-ondemand.json"
    },
    {
        "service": "rds-mysql-ondemand",
        "pricing_url": "https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/rds/USD/current/rds-mysql-ondemand.json"
    },
    {
        "service": "rds-postgresql-ondemand",
        "pricing_url": "https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/rds/USD/current/rds-postgresql-ondemand.json"
    },
    {
        "service": "rds-oracle-ondemand",
        "pricing_url": "https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/rds/USD/current/rds-oracle-ondemand.json"
    },
    {
        "service": "rds-mariadb-ondemand",
        "pricing_url": "https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/rds/USD/current/rds-mariadb-ondemand.json"
    },
    {
        "service": "rds-sqlserver-ondemand",
        "pricing_url": "https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/rds/USD/current/rds-sqlserver-ondemand.json"
    },
    {
        "service": "rds-flex-ondemand",
        "pricing_url": "https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/rds/USD/current/rds-flex-ondemand.json"
    },
    {
        "service": "rds-proxy",
        "pricing_url": "https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/rds/USD/current/rds-proxy.json"
    },
    {
        "service": "sagemaker-training-plan",
        "pricing_url": "https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/sagemaker/USD/current/sagemaker-training-plan.json"
    },
    {
        "service": "sagemaker-instances-studionotebook",
        "pricing_url": "https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/sagemaker/USD/current/sagemaker-instances-studionotebook.json"
    },
    {
        "service": "carrierip",
        "pricing_url": "https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/carrierip.json"
    }
]

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

    sanitized_service_names = []
    for service in service_list_obj["offers"].keys():
        sanitized_service_name = service.lower().removeprefix("amazon").removeprefix("aws")
        sanitized_service_names.append(sanitized_service_name)

    sanitized_service_names.remove("rds")
    sanitized_service_names.append("rds-storage")
    sanitized_service_names.append("rds-aurora-storage")
    sanitized_service_names.append("rds-aurora-ondemand")
    sanitized_service_names.append("rds-db2-ondemand")
    sanitized_service_names.append("rds-mysql-ondemand")
    sanitized_service_names.append("rds-postgresql-ondemand")
    sanitized_service_names.append("rds-oracle-ondemand")
    sanitized_service_names.append("rds-mariadb-ondemand")
    sanitized_service_names.append("rds-sqlserver-ondemand")
    sanitized_service_names.append("rds-flex-ondemand")
    sanitized_service_names.append("rds-proxy")
    sanitized_service_names.append("sagemaker-training-plan")
    sanitized_service_names.append("sagemaker-instances-studionotebook")
    sanitized_service_names.append("carrierip")
    
    for sanitized_service_name in sanitized_service_names:
        pricing_url = "https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/{}/USD/current/{}.json?timestamp={}".format(sanitized_service_name, sanitized_service_name, str(int(time.time())))
        skip_service = False
        for static_service in STATIC_PRICING:
            if static_service["service"] == sanitized_service_name and "pricing_url" in static_service:
                pricing_url = static_service["pricing_url"]
                break
            if static_service["service"] == sanitized_service_name and "skip" in static_service:
                skip_service = True
                break
        if skip_service:
            continue
        contents = get_url_contents(pricing_url)
        # https://b0.p.awsstatic.cn/pricing/2.0/meteredUnitMaps/ec2/CNY/current/ec2.json
        if contents:
            contents_obj = json.loads(contents)

            save_file("raw/{}.json".format(sanitized_service_name), json.dumps(contents_obj, indent=4))

            if sanitized_service_name == "directconnect":
                contents_obj["sets"] = {} # special case: poor sets allocation

            processed_contents = {}
            for region_name in contents_obj["regions"].keys():
                for code_name in list(contents_obj["regions"][region_name].keys()): # copy as we'll be mutating
                    if code_name not in contents_obj["regions"][region_name]: # already captured
                        continue

                    #print(sanitized_service_name, region_name, code_name)
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
                            #print("Outlier: ", sanitized_service_name, region_name, code_name)
                    
                    modified_region_name = modify_region_name(region_name, contents_obj["regions"][region_name][code_name])

                    if modified_region_name not in processed_contents[modified_code_name]:
                        processed_contents[modified_code_name][modified_region_name] = contents_obj["regions"][region_name][code_name]["price"]
                    elif processed_contents[modified_code_name][modified_region_name] != contents_obj["regions"][region_name][code_name]["price"]:
                        print("WARNING: Found existing and conflicting price for {} {} {}".format(sanitized_service_name, modified_code_name, modified_region_name))
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
                                    modified_service_detail[sanitized_service_name] += "\n  - Region added for metric {}: {} 🌎".format(metric_name, region_name)
                            for region_name in existing_contents_obj[metric_name].keys():
                                if region_name not in processed_contents[metric_name]:
                                    modified_service_detail[sanitized_service_name] += "\n  - Region removed for metric {}: {} 💥".format(metric_name, region_name)
                                else:
                                    if existing_contents_obj[metric_name][region_name] != processed_contents[metric_name][region_name]:
                                        # parse prices
                                        try:
                                            old_price = float(existing_contents_obj[metric_name][region_name])
                                            new_price = float(processed_contents[metric_name][region_name])
                                            if old_price < new_price:
                                                modified_service_detail[sanitized_service_name] += "\n  - Price increased: {} {}  **${:.2f}** → **${:.2f}** 🤑".format(metric_name, region_name, old_price, new_price)
                                            elif old_price > new_price:
                                                modified_service_detail[sanitized_service_name] += "\n  - Price decreased: {} {}  **${:.2f}** → **${:.2f}** 💸".format(metric_name, region_name, old_price, new_price)
                                        except:
                                            modified_service_detail[sanitized_service_name] += "\n  - Price changed: {} {} 💰".format(metric_name, region_name)
            else:
                new_services.append(sanitized_service_name)

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
            out += "\n\n"

    # read readme file
    with open("README.md", "r") as readme_file:
        out += readme_file.read().split("## Not included services")[0]

    out += "## Not included services\n\n- {}".format('\n- '.join(not_found))

    save_file("README.md", out)