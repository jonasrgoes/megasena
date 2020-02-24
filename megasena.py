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
LAST_CONTESTS = [3, 5, 10, 25, 50, 100, 250, 500, 1000, 1500, 2000, 2500, 3000]
BASE_DIR = pathlib.Path(__file__).parent.absolute()
ZIP_FILE = BASE_DIR / 'megasena.zip'
HTML_FILE = BASE_DIR / 'd_mega.htm'

ZIP_URL = 'http://www1.caixa.gov.br/loterias/_arquivos/loterias/D_megase.zip'

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

# Dezenas da Mega Sena
dozens = {
    1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0,
    11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0,
    21: 0, 22: 0, 23: 0, 24: 0, 25: 0, 26: 0, 27: 0, 28: 0, 29: 0, 30: 0,
    31: 0, 32: 0, 33: 0, 34: 0, 35: 0, 36: 0, 37: 0, 38: 0, 39: 0, 40: 0,
    41: 0, 42: 0, 43: 0, 44: 0, 45: 0, 46: 0, 47: 0, 48: 0, 49: 0, 50: 0,
    51: 0, 52: 0, 53: 0, 54: 0, 55: 0, 56: 0, 57: 0, 58: 0, 59: 0, 60: 0,
}

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


def calc_ocurrencies(contests):
    if WINNERS_ONLY:
        json_file = BASE_DIR / str('megasena_winners_' + str(contests) + '.json')
    else:
        json_file = BASE_DIR / str('megasena_' + str(contests) + '.json')

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


for contests in LAST_CONTESTS:
    calc_ocurrencies(contests)

driver.quit()
