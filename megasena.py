import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import json
import zipfile
import urllib.request
import sys
import pathlib
from http.cookiejar import CookieJar

print('\33c')

# Grab content from URL
WINNERS_ONLY = True
# LAST_CONTESTS = [3, 5, 10, 25, 50, 100, 250, 500, 1000, 1500, 2000, 2500, 3000]
LAST_CONTESTS = [50, 100]
BASE_DIR = pathlib.Path(__file__).parent.absolute()
ZIP_FILE = BASE_DIR / 'megasena.zip'
HTML_FILE = BASE_DIR / 'd_mega.htm'

ZIP_URL = 'http://www1.caixa.gov.br/loterias/_arquivos/loterias/D_megase.zip'


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
        json_file = BASE_DIR / \
            str('megasena_winners_' + str(contests) + '.json')
    else:
        json_file = BASE_DIR / str('megasena_' + str(contests) + '.json')

    # Dezenas da Mega Sena
    dozens = {}
    for i in range(1, 61):
        dozens[i] = 0

    table = html_parse()

    # Data Frame - Pandas
    df_full = pd.read_html(str(table))[0].tail(contests)
    df = df_full[['1ª Dezena', '2ª Dezena', '3ª Dezena',
                  '4ª Dezena', '5ª Dezena', '6ª Dezena', 'Ganhadores_Sena', 'Cidade']]
    df.columns = ['_1', '_2', '_3', '_4', '_5', '_6', 'ganhadores', 'cidade']

    js = df.to_dict('records')

    for k in js:
        if WINNERS_ONLY:
            if k['ganhadores'] <= 0:
                continue
        dozens[k['_1']] = dozens[k['_1']] + 1
        dozens[k['_2']] = dozens[k['_2']] + 1
        dozens[k['_3']] = dozens[k['_3']] + 1
        dozens[k['_4']] = dozens[k['_4']] + 1
        dozens[k['_5']] = dozens[k['_5']] + 1
        dozens[k['_6']] = dozens[k['_6']] + 1

    ordered_dozens = {k: v for k, v in sorted(
        dozens.items(), key=lambda item: item[1], reverse=True)}

    print('Number of contests: ' + str(contests))
    print(ordered_dozens)

    # Dump and Save to JSON file (Converter e salvar em um arquivo JSON)
    with open(str(json_file), 'w', encoding='utf-8') as jp:
        js = json.dumps(ordered_dozens, indent=4)
        jp.write(js)


def ranking_dozens():
    for contests in LAST_CONTESTS:
        calc_ocurrencies(contests)


zip_download()
ranking_dozens()
