from gensim.models import KeyedVectors
from sklearn.metrics.pairwise import cosine_similarity
import requests
import codecs
import json
import pandas as pd
import simplejson
import csv
from deep_translator import GoogleTranslator
from csv import DictReader
from transformers import GPT2LMHeadModel, GPT2Tokenizer

# ozon_api.py
class OzonAPI:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_tree_and_categories(self):
        url = "https://api-seller.ozon.ru/v1/description-category/tree"
        headers = {"Client-Id": "1955012", "Api-Key": self.api_key}
        json_data = {"language": "EN"}  # Change to "RU", "TR", "ZH_HANS", or "DEFAULT" as needed
        response = requests.post(url, headers=headers, json=json_data)

        if response.status_code == 200:
            categories = response.json().get('result', [])[0]
            return ("Success:", response.json()), categories
        else:
            return ("Error:", response.status_code, response.text), []

    def get_attributes(self, category_id):
        url = f"https://api-seller.ozon.ru/v1/category/attribute?category_id={category_id}"
        headers = {"Client-Id": "1955012", "Api-Key": self.api_key}
        json_data = {"language": "EN"}  # Change to "RU", "TR", "ZH_HANS", or "DEFAULT" as needed
        response = requests.post(url, headers=headers, json=json_data)
        return response.json()

# transform.py
class DataTransformer:
    def __init__(self, ozon_api_key):
        self.ozon_api = OzonAPI(ozon_api_key)
        self.model_name = "sberbank-ai/rugpt3small_based_on_gpt2"
        self.model = GPT2LMHeadModel.from_pretrained(self.model_name)
        self.tokenizer = GPT2Tokenizer.from_pretrained(self.model_name)

    def map_index(self, word, array):
        word_translated = GoogleTranslator(source='auto', target='en').translate(word)
        max_similarity_index, max_similarity = 0, 0.0

        for i, word2 in enumerate(array):
            word2_translated = GoogleTranslator(source='auto', target='en').translate(word2)
            similarity = cosine_similarity([word_translated], [word2_translated])
            if similarity > max_similarity:
                max_similarity, max_similarity_index = similarity, i

        return max_similarity_index

    def ai_convert_measures(self, value, from_unit, to_unit):
        prompt = f"Convert {value} {from_unit} to {to_unit}."
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(**inputs, max_length=50)
        conversion_result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return conversion_result

    def ai_convert_colors(self, value, from_color, to_color):
        prompt = f"Convert colors: {from_color} to {to_color}."
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(**inputs, max_length=50)
        conversion_result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return conversion_result

    def transform(self, input_csv, source_marketplace, target_marketplace):
        with open(input_csv, 'r') as f:
            data = list(DictReader(f))

        model = KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True)
        api_response, ozon_categories = self.ozon_api.get_tree_and_categories()

        # выводит все дерево категорий в файл
        with open("twitterData.json", "w") as file:
            file.write(simplejson.dumps(api_response, indent=4, sort_keys=True))

        # создаем пулл новых карточек
        transformed_data = []

        for row in data:
            # создаем новую карточку
            transformed_card = {}

            # ищем индекс похожей категории
            similarity_index = self.map_index(row['Категория'], ozon_categories)

            # формируем новую карточку
            # new_card[категория] = категория озона[max_similarity_index] название
            # new_card[название] = название
            # new_card[описание] = описание
            transformed_card['Категория'] = ozon_categories[similarity_index]['category_name']
            transformed_card['Название'] = row['Название']
            transformed_card['Описание'] = row['Описание']

            # берем type_id по найденному индексу
            similarity_type_id = ozon_categories[similarity_index]['type_id']

            # ищем для него атрибуты
            target_attributes = self.ozon_api.get_attributes(similarity_type_id)

            # итерируемся по столбцам атрибутов озона not in ['Название', 'Категория', 'Описание']
            for key in target_attributes:
                if key not in ['Название', 'Категория', 'Описание']:
                    # отдельно рассматриваем случай когда key близок к цвету
                    if 'Цвет' == self.map_index('Цвет'):
                        transformed_card[key] = self.ai_convert_colors(row[key], 'source_color', 'target_color')
                        continue

                    splitted_key = key.split(',')
                    # для озона ищем подходящий атрибут среди атрибутов в исходной карточке
                    current_attribute = self.map_index(splitted_key[0], row)
                    parts = current_attribute.split(',')

                    # переводим величины
                    converted_measure_value = self.ai_convert_measures(
                        row[current_attribute], parts[1], splitted_key[1]
                    )
                    transformed_card[key] = converted_measure_value

            # обновляем пул карточек
            transformed_data.append(transformed_card)

        print(transformed_data)

        output_csv = input_csv.replace(".csv", f"_{target_marketplace}.csv")
        pd.DataFrame(transformed_data).to_csv(output_csv, index=False)
        return output_csv


ozon_api_key = '376ff8a6-f8b7-4c31-a8aa-7aa374000d9e'
transformer = DataTransformer(ozon_api_key)
input_csv = 'input.csv'
source_marketplace = 'Seller'
target_marketplace = 'Ozon'
output_csv = transformer.transform(input_csv, source_marketplace, target_marketplace)
print(f"Transformed CSV saved at: {output_csv}")
