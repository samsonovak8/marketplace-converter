import json
import requests
import pandas as pd

class OzonAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.data = {}
        self.all_ozon_categories = []
        self.headers = {}

    def traverse(self, categories, node):
        if 'category_name' in node:
            categories.append(node['category_name'])
        if 'type_name' in node:
            categories.append(node['type_name'])
        if 'children' in node and node['children']:
            for child in node['children']:
                self.traverse(categories, child)

    def build(self):
        url = "https://api-seller.ozon.ru/v1/description-category/tree"
        self.headers = {"Client-Id": "696499", "Api-Key": self.api_key}
        json_data = {
            "language": "EN"  # Change to "RU", "TR", "ZH_HANS", or "DEFAULT" as needed 
        }
        response = requests.post(url, headers=headers, json=json_data)
        # на случай если если слишком нмого делать запросов
        # with open('init/twitterData.json', 'r') as file:
        #     self.data = pd.DataFrame(json.load(file))

        self.all_ozon_categories = []
        for item in self.data[0][1]['result']:
            self.traverse(self.all_ozon_categories, item)
        
        if response.status_code == 200:
            return("Success:", response.json())
        return("Error:", response.status_code, response.text), []
        

    def get_attributes(self, type_id, description_category_id):
        url = f"https://api-seller.ozon.ru//v1/description-category/attribute"
        headers = {"Client-Id": "696499", "Api-Key": self.api_key}
        json_data = {
            "description_category_id": description_category_id,
            "language": "EN",
            "type_id": type_id,
        }
        response = requests.post(url, headers=headers, json=json_data)
        if response.status_code == 200:
            return("Success:", response.json())
        return("Error:", response.status_code, response.text)
        # with open('init/twitterData2.json', 'r') as file:
        #     attribues = json.load(file)
        # return attribues[1]['result']

    def get_attribute_characteristics(self, attribute_id, description_category_id, last_value_id, limit, type_id):
        url = "https://api-seller.ozon.ru/v1/description-category/attribute/values"
        headers = {"Client-Id": "696499", "Api-Key": self.api_key}
        json_data = {
            "attribute_id": attribute_id,
            "description_category_id": description_category_id,
            "language": "EN",
            "last_value_id": last_value_id,
            "limit": limit,
            "type_id": type_id
        }
        response = requests.post(url, headers=headers, json=json_data)
        if response.status_code == 200:
            return("Success:", response.json())
        return("Error:", response.status_code, response.text), []
