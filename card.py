from ozon_api import OzonAPI
from utils import get_by_prompt

class TypeId:
    def __init__(self):
        self.type_id = ""
        self.description_category_id = ""

    def get_type_id(self, name, node, parent):
        if 'type_name' in node and node['type_name'] == name:
            self.type_id = str(node['type_id'])
            self.description_category_id = parent['description_category_id']
        if 'children' in node and node['children']:
            for child in node['children']:
                self.get_type_id(name, child, node)

class Card:
    def __init__(self, description, ozon):
        self.description = description
        self.best_category = ""
        self.type_id = ""
        self.description_category_id = ""
        self.ozon = ozon
        self.node = TypeId()
        self.attributes = []
    

    def find_category(self, answer, all_categories):
        for category in all_categories:
            if category in answer:
                return category
        return ""


    def set_best_category(self):
        print("in set_best_category")
        prompt = f"find the most close by sense category from the list of categories: {self.ozon.all_ozon_categories} for item description {self.description}"
        with open('init/example_for_llama.txt') as f:
            prompt += f.read()
        prompt += f" please for item with desciprtion {self.description} plese return only 1 caterogy_name exactly as it's in the list, please do not add any comments"
        not_correct_answer = get_by_prompt(prompt)
        print(not_correct_answer)
        self.best_category = self.find_category(not_correct_answer, self.ozon.all_ozon_categories)
        print(self.best_category)
        

    def set_type_and_description_category(self):
        print("in set_type_and_description_category")
        best_category, data = self.best_category, self.ozon.data
        for item in data[0][1]['result']:
            self.node.get_type_id(best_category, item, None)
            if self.node.type_id:
                self.type_id = self.node.type_id
                self.description_category_id = self.node.description_category_id
                break
        print(self.type_id, self.description_category_id)
    

    def make_attribute(self, all_attribute_characteristics, attribute):
        print("in make_attribute")
        attribute_dict = {}
        type_name = ""
        if attribute['dictionary_id'] != 0:
            characteristics = all_attribute_characteristics
            prompt = f"**Product Description**: {self.description} " + str(attribute['description']) + str(characteristics) + " answer should contain only 1 answer without comments"
            type_name = get_by_prompt(prompt)
            print(attribute['description'])
            print(type_name)
            print()
        else:
            prompt = f"**Product Description**: {self.description} " + str(attribute['description']) + "answer should contain only 1 answer without comments"
            type_name = get_by_prompt(prompt)
            print(attribute['description'])
            print(type_name)
            print()
            

        attribute_dict['complex_id'] = 0 # change if has video
        attribute_dict['id'] = attribute['id']
        attribute_dict['values'] = [
            {
                'dictionary_value_id': attribute['dictionary_id'],
                'value': type_name,
            }
        ]
        return attribute_dict


    def set_attributes(self):
        print("in set_attributes")
        all_item_attributes = self.ozon.get_attributes(self.type_id, self.description_category_id)
        for attribute in all_item_attributes:
            all_attribute_characteristics = self.ozon.get_attribute_characteristics(attribute['dictionary_id'], self.description_category_id, 0, 100, self.type_id)
            self.attributes.append(self.make_attribute(all_attribute_characteristics, attribute))


    def build(self):
        self.set_best_category()
        self.set_type_and_description_category()
        self.set_attributes()
    

    def get_or_empty_string(self, what_to_find):
        print("in get_or_empty_string")
        prompt = f"Find item {what_to_find} in the description " + self.description + ", please do not add any comments, if there's no appropriate {what_to_find}, print 'nothing'"
        answer = get_by_prompt(prompt)
        if answer != 'nothing':
            return answer
        return ""


    def get_or_empty_array(self, what_to_find):
        print("in get_or_empty_array")
        prompt = f"Find value of {what_to_find} in the item description " + self.description + ", please do not add any comments, if there's no appropriate {what_to_find}, return 'nothing'"
        answer = get_by_prompt(prompt)
        if answer != 'nothing':
            return answer
        return []
    

    def get_or_zero(self, what_to_find):
        print("in get_or_zero")
        prompt = f"Find item {what_to_find} in the description " + self.description + ", please do not add any comments, if there's no appropriate {what_to_find}, print 'nothing'"
        answer = get_by_prompt(prompt)
        if answer != 'nothing':
            return answer
        return 0
    

    def make(self):
        return {
            "attributes": self.attributes,
            "barcode": self.get_or_empty_string("barcode"),
            "description_category_id": self.description_category_id,
            "new_description_category_id": self.get_or_zero("new_description_category_id"),
            "color_image": self.get_or_empty_string("color_image"),
            "complex_attributes": self.get_or_empty_array("complex_attributes"),
            "currency_code": self.get_or_empty_string("currency_code"),
            "depth": self.get_or_zero("depth"),
            "dimension_unit": self.get_or_empty_string("mm"),
            "height": self.get_or_zero("height"),
            "images": self.get_or_empty_array("images"),
            "images360": self.get_or_empty_array("images360"),
            "name": self.get_or_empty_string("name"),
            "offer_id": self.get_or_empty_string("offer_id"),
            "old_price": self.get_or_empty_string("old_price"),
            "pdf_list": self.get_or_empty_array("pdf_list"),
            "price": self.get_or_empty_string("price"),
            "primary_image": self.get_or_empty_string("primary_image"),
            "vat": self.get_or_empty_string("vat"),
            "weight": self.get_or_zero("weight"),
            "weight_unit": self.get_or_empty_string("weight_unit"),
            "width": self.get_or_zero("width")
    }

    
