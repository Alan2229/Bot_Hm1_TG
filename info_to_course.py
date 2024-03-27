from bs4 import BeautifulSoup
import requests

# Сайт для получения курса валют Тенге и Бел_Рубль
main_url_mir = "https://onlymir.ru"

# Сайт для получения курса валют Долларов и Евро
main_url_mp = "https://mp-bank.ru/currency/"


# Получение курса валют в долларах и в евро
def convert_usd_euro(type):
    # Получение данных с сайта
    page_usd_and_euro = requests.get(f"{main_url_mp}")
    soup_mp = BeautifulSoup(page_usd_and_euro.text, "html.parser")
    table = soup_mp.find('table')
    tbody = table.find('tbody')

    # Извлекаем данные из таблицы
    rows = tbody.find_all('tr')
    dollars = []
    euro = []
    for row in rows:
        cols = row.find_all('td')
        for col in cols:
            col = col.text.replace(',', '.')
            try:
                float(col)
                if (len(dollars) < 2):
                    dollars.append(float(col))
                else:
                    euro.append(float(col))
            except ValueError:
                continue
    if type == 1:
        ans = str(dollars[0]) + " " + str(dollars[1])
        return ans
    else:
        return euro


# Получение курса валюты тенге
def convert_kzt():
    # Получение данных с сайта
    page_kzt = requests.get(f"{main_url_mir}/kzt/")
    soup_mir_kzt = BeautifulSoup(page_kzt.text, "html.parser")
    cour_kzt = soup_mir_kzt.find('p', class_='textable css21')
    par_cout_kzt = ' '.join(cour_kzt.findAll(string=True, recursive=False)).split()
    kzt_to_rub = float(par_cout_kzt[1])
    rub_to_kzt = float(par_cout_kzt[3])
    ans = str(kzt_to_rub) + " " + str(rub_to_kzt)
    return ans


# Получение курса валюты бел_рубль
def convert_byn():
    # Получение данных с сайта
    page_byn = requests.get(f"{main_url_mir}/byn/")
    soup_mir_byn = BeautifulSoup(page_byn.text, "html.parser")
    cour_byn = soup_mir_byn.find('p', class_='textable css21')
    par_cout_byn = ' '.join(cour_byn.findAll(string=True, recursive=False)).split()
    byn_to_rub = float(par_cout_byn[1])
    rub_to_byn = float(par_cout_byn[3])
    ans = str(byn_to_rub) + " " + str(rub_to_byn)
    return ans
