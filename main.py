from ozon_api import OzonAPI
from card import Card
from utils import read_file_as_list_of_strings
import pandas as pd
import json
from deep_translator import GoogleTranslator

def make_ozon_cards(description_list):
    ozon_api_key = '8134f5e6-ecf8-4e71-a7e1-c4b83c86af8b'
    ozon = OzonAPI(ozon_api_key)
    ozon.build()

    cards_list = []
    for description in description_list:
        card = Card(description, ozon)
        print(card.description)
        print("going to build card")
        card.build()
        print("going to make card")
        card.make()
        cards_list.append(card)
        print(str(card))

    print(str(cards_list))
    return cards_list


def transform_dict(input_dict):
    length = len(input_dict['category_url'])
    result = []
    for i in range(length):
        row = {}
        for key in input_dict:
            row[key] = input_dict[key][i]
        result.append(row)

    return result


def fake_main(file_path, output_file):
    data_list = read_file_as_list_of_strings(file_path)
    new_cards = make_ozon_cards(data_list)
    with open(output_file, 'a') as f:
        for line in new_cards:
            f.write(f"{line}\n")

def fake_main2():
    df = transform_dict(pd.read_csv('Вход.csv', encoding='utf-8').to_dict())
    with open('out.txt', 'w', encoding='utf-8') as f:
        json.dump(df, f, ensure_ascii=False, indent=4)
    
    print(type(df))
    text_lines = []
    for item in df:
        item = GoogleTranslator(source='auto', target='en').translate(str(item))
        text_lines.append(str(item))
    
    with open('out2.txt', 'w', encoding='utf-8') as f:
        f.write(str(text_lines))
    print("going to make_ozon_cards")
    new_cards = make_ozon_cards([text_lines[0]])
    with open('new_cards.txt', 'a') as f:
        for line in new_cards:
            f.write(f"{str(line)}\n")

def main():

    # fake_main('init/input.txt', 'init/output.txt')
    fake_main2()


if __name__ == "__main__":
    main()
