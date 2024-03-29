import os
import sys
import shutil
import pathlib
import json
import zipfile
import requests
import urllib.request
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from http.cookiejar import CookieJar
from itertools import combinations
from typing import OrderedDict


# Settings
MIN_DOZEN = 1
MAX_DOZEN = 60
WINNERS_ONLY = False
DOZENS_MOST_SORTED = 7
BETS_DOZENS_COUNT = 6
LAST_CONTESTS = [200]

# Megasena Data Source
ZIP_URL = 'http://www1.caixa.gov.br/loterias/_arquivos/loterias/D_megase.zip'

# Paths Constants
BASE_DIR = pathlib.Path(__file__).parent.absolute()
JSON_BASE_DIR = pathlib.Path(__file__).parent.absolute() / 'json'
ZIP_FILE = BASE_DIR / 'megasena.zip'
HTML_FILE = BASE_DIR / 'd_mega.htm'

print('\33c')

try:
    os.stat(JSON_BASE_DIR)
    shutil.rmtree(JSON_BASE_DIR)
except:
    os.makedirs(JSON_BASE_DIR)

try:
    os.stat(JSON_BASE_DIR)
except:
    os.makedirs(JSON_BASE_DIR)


def zip_download():
    try:
        req = urllib.request.Request(ZIP_URL, None, {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; G518Rco3Yp0uLV40Lcc9hAzC1BOROTJADjicLjOmlr4=) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
                                                     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3', 'Accept-Encoding': 'gzip, deflate, sdch', 'Accept-Language': 'en-US,en;q=0.8', 'Connection': 'keep-alive'})
        cj = CookieJar()
        opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(cj))
        response = opener.open(req)
        raw_response = response.read()
        with open(str(ZIP_FILE), 'wb') as jp:
            jp.write(raw_response)
        response.close()
    except urllib.request.HTTPError as inst:
        output = format(inst)
        print(output)

    with zipfile.ZipFile(str(ZIP_FILE), 'r') as zip_ref:
        zip_ref.extractall(str(BASE_DIR))


def html_parse():
    option = Options()
    option.headless = True
    driver = webdriver.Firefox(options=option)

    driver.get('file://' + str(HTML_FILE))
    # driver.implicitly_wait(5)

    element = driver.find_element_by_xpath("//table")
    html = element.get_attribute('outerHTML')

    # HTML Parse
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find(name='table')

    driver.quit()

    return table


def calc_ocurrencies(contests):
    if WINNERS_ONLY:
        json_file = JSON_BASE_DIR / \
            str('megasena_winners_' + str(contests) + '.json')
        results_file = JSON_BASE_DIR / \
            str('results_winners_' + str(contests) + '.json')
    else:
        json_file = JSON_BASE_DIR / str('megasena_' + str(contests) + '.json')
        results_file = JSON_BASE_DIR / \
            str('results_' + str(contests) + '.json')

    # Dezenas da Mega Sena
    dozens = {}
    for i in range(1, 61):
        dozens[i] = 0

    # Números Sorteados
    df_full = pd.read_html(str(table))[0]
    df = df_full[['1ª Dezena', '2ª Dezena', '3ª Dezena',
                  '4ª Dezena', '5ª Dezena', '6ª Dezena', 'Ganhadores_Sena', 'Cidade']]
    df.columns = ['_1', '_2', '_3', '_4', '_5', '_6', 'ganhadores', 'cidade']
    df = df.drop_duplicates(keep='first', subset=[
                            '_1', '_2', '_3', '_4', '_5', '_6'])
    js = df.tail(contests).to_dict('records')

    results = []
    for k in js:
        if WINNERS_ONLY:
            if k['ganhadores'] == 0:
                continue

        results_list = [int(k['_1']), int(k['_2']), int(
            k['_3']), int(k['_4']), int(k['_5']), int(k['_6'])]
        results_list.sort()
        results.append(results_list)

        if MIN_DOZEN <= int(k['_1']) <= MAX_DOZEN:
            dozens[int(k['_1'])] += 1
        if MIN_DOZEN <= int(k['_2']) <= MAX_DOZEN:
            dozens[int(k['_2'])] += 1
        if MIN_DOZEN <= int(k['_3']) <= MAX_DOZEN:
            dozens[int(k['_3'])] += 1
        if MIN_DOZEN <= int(k['_4']) <= MAX_DOZEN:
            dozens[int(k['_4'])] += 1
        if MIN_DOZEN <= int(k['_5']) <= MAX_DOZEN:
            dozens[int(k['_5'])] += 1
        if MIN_DOZEN <= int(k['_6']) <= MAX_DOZEN:
            dozens[int(k['_6'])] += 1

    with open(str(results_file), 'w', encoding='utf-8') as jp:
        js = json.dumps(results, indent=4)
        jp.write(js)

    ordered_dozens = {k: v for k, v in sorted(
        dozens.items(), key=lambda item: item[1], reverse=True)}

    # Dump and Save to JSON file (Converter e salvar em um arquivo JSON)
    with open(str(json_file), 'w', encoding='utf-8') as jp:
        js = json.dumps(ordered_dozens, indent=4)
        jp.write(js)


def ranking_dozens():
    for contests in LAST_CONTESTS:
        calc_ocurrencies(contests)


def write_bets():
    for contests in LAST_CONTESTS:
        if WINNERS_ONLY:
            json_file = JSON_BASE_DIR / \
                str('megasena_winners_' + str(contests) + '.json')
            results_file = JSON_BASE_DIR / \
                str('results_winners_' + str(contests) + '.json')
            bets_quadra_file = JSON_BASE_DIR / \
                str('bets_winners_quadra_' + str(contests) + '.txt')
            bets_quina_file = JSON_BASE_DIR / \
                str('bets_winners_quina_' + str(contests) + '.txt')
            bets_sena_file = JSON_BASE_DIR / \
                str('bets_winners_sena_' + str(contests) + '.txt')
        else:
            json_file = JSON_BASE_DIR / \
                str('megasena_' + str(contests) + '.json')
            results_file = JSON_BASE_DIR / \
                str('results_' + str(contests) + '.json')
            bets_quadra_file = JSON_BASE_DIR / \
                str('bets_quadra_' + str(contests) + '.txt')
            bets_quina_file = JSON_BASE_DIR / \
                str('bets_quina_' + str(contests) + '.txt')
            bets_sena_file = JSON_BASE_DIR / \
                str('bets_sena_' + str(contests) + '.txt')

        counter = 0
        bets_quadra = []
        bets_quina = []
        bets_sena = []
        selected_dozens = []

        with open(json_file) as json_file_read:
            data = json.load(json_file_read)
            for p in data.keys():
                counter += 1
                if counter > DOZENS_MOST_SORTED:
                    break
                selected_dozens.append(int(p))

        selected_dozens.sort()

        combination_list = combinations(selected_dozens, BETS_DOZENS_COUNT)

        bets_combinations = list(map(sorted, combination_list))

        with open(results_file) as json_result_file_read:
            data = json.load(json_result_file_read, parse_int=int)
            for result in data:
                for bet in bets_combinations:
                    intersection = set(result) & set(bet)
                    if len(intersection) == 6:
                        bets_sena.append(bet)
                    elif len(intersection) == 5:
                        bets_quina.append(bet)
                    elif len(intersection) == 4:
                        bets_quadra.append(bet)

        with open(str(bets_sena_file), 'w', encoding='utf-8') as jp:
            for bet in bets_sena:
                jp.write("%s\n" % ' '.join(str(x).zfill(2) for x in bet))

        with open(str(bets_quina_file), 'w', encoding='utf-8') as jp:
            for bet in bets_quina:
                jp.write("%s\n" % ' '.join(str(x).zfill(2) for x in bet))

        with open(str(bets_quadra_file), 'w', encoding='utf-8') as jp:
            for bet in bets_quadra:
                jp.write("%s\n" % ' '.join(str(x).zfill(2) for x in bet))


def results():
    if WINNERS_ONLY:
        results_file = JSON_BASE_DIR / str('results_winners.txt')
    else:
        results_file = JSON_BASE_DIR / str('results.txt')

    # Números Sorteados
    results = []
    results_sorted = []
    df_full = pd.read_html(str(table))[0]
    df = df_full[['1ª Dezena', '2ª Dezena', '3ª Dezena',
                  '4ª Dezena', '5ª Dezena', '6ª Dezena', 'Ganhadores_Sena']]
    df.columns = ['_1', '_2', '_3', '_4', '_5', '_6', 'ganhadores']
    js = df.to_dict('records')

    for k in js:
        if WINNERS_ONLY:
            if int(k['ganhadores']) <= 0:
                continue

        result_list = [k['_1'], k['_2'], k['_3'], k['_4'], k['_5'], k['_6']]
        result_list.sort()

        result_line = ''.join(str(x).zfill(2) for x in result_list)

        results.append(result_line)

    results.sort()

    results = list(dict.fromkeys(results))

    with open(str(results_file), 'w', encoding='utf-8') as jp:
        for line in results:
            jp.write("%s\n" % ' '.join(str(line[i:i+2])
                                       for i in range(0, len(line), 2)))


def check_repeated_results():
    for contests in LAST_CONTESTS:
        if WINNERS_ONLY:
            results_file = JSON_BASE_DIR / \
                str('results_winners_' + str(contests) + '.json')
        else:
            results_file = JSON_BASE_DIR / \
                str('results_' + str(contests) + '.json')

        quadra = 0
        quina = 0

        with open(results_file) as json_result_file_read:
            data = json.load(json_result_file_read, parse_int=int)
            for result_1 in data:
                for result_2 in data:
                    intersections = len(set(result_1) & set(result_2))
                    if intersections == 5:
                        quina += 1
                    if intersections == 4:
                        quadra += 1

        print('Quadra: ' + str(quadra))
        print('Quina: ' + str(quina))


zip_download()
table = html_parse()
ranking_dozens()
write_bets()
results()
check_repeated_results()
