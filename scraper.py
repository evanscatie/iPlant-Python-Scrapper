import os
import json
import time

import requests
from bs4 import BeautifulSoup

def get_alphanumeric(str_):
    alphanumeric = ""

    for char in str_:
        if (char.isalnum() or char == ' ' 
                           or char == '_' 
                           or char == ','
                           or char == '/' 
                           or char == '-' 
                           or char == '>' 
                           or char == '<' 
                           or char == '(' 
                           or char == ')'):
            alphanumeric += char
    
    return alphanumeric

master_result = {}
for i in range (1, 1794):
    result = {}

    base_url = 'http://plantdatabase.kpu.ca'
    url = f'{base_url}/plant/plantDetail/{i}'

    result['plant_url'] = url

    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    tables = soup.find_all('table', class_='pdetail')
    for table in tables:
        rows = table.find_all("tr")

        for row in rows:
            try:
                print('----------------')
                cells = row.find_all('td')

                key = get_alphanumeric(cells[0].get_text().strip().replace(':','').replace(' ', '_').replace('/_','/'))
                print(f'KEY ----- {key}')
                
                value = get_alphanumeric(' '.join(cells[1].get_text().strip().split()))
                print(f'VALUE ----- {value}')
                
                if key == '' or value == '':
                    print('Nothing to Save - Skipping Record')
                    continue

                if len(key) > 25:
                    print('Bad Key, Too Long - Skipping Record')
                    continue

                result[key] = value
            except IndexError:
                print('IndexError - Skipping Record')

    imgs = soup.find_all('img', class_='image_alignment')
    imgs_list = []
    for img in imgs:
        imgs_list.append(f'{base_url}{img["src"]}')
    
    result['images_list'] = imgs_list
    master_result[i] = result

    if i > 3:
        break

    time.sleep(.25)

filename = f'outputs/plant_info.json'

if not os.path.exists(os.path.dirname(filename)):
    try:
        os.makedirs(os.path.dirname(filename))
    except OSError as exc: # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise

with open(filename, 'w') as outfile:
    json.dump(master_result, outfile, indent=4)

filename = f'outputs/plant_seeds.sql'
if not os.path.exists(os.path.dirname(filename)):
    try:
        os.makedirs(os.path.dirname(filename))
    except OSError as exc: # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise


with open(filename, 'w') as outfile:
    for value in range(1,5):
        seed = master_result[value]
        seeds = f'("{seed["plant_url"]}", "{seed["Scientific_Name"]}", "{seed["Common_Name"]}", "{seed["Plant_Type"]}", "{seed["Growth_Rate"]}", "{seed["Exposure"]}")'
        outfile.write('{}\n'.format(seeds))

