import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def get_price(string):
    pr_string = re.compile(r'\d+,\d+')
    price = pr_string.findall(string.replace(".",""))
    return float(price[0].replace(".","").replace(",","."))

def get_prod_details(product):
    prod_details = pd.DataFrame()
    prod_details["source"] = ["babyartikel"]
    prod_details["brand"] = [product.find("a", class_="trackProdClick").find("b").get_text().strip()]
    prod_details["description"] = [product.find("a", class_="trackProdClick").get_text().strip()]
    # try:
    #     prod_details["description"] = [product.find(class_="col-sm-6 product__title product__view")["title"].strip()]
    # except:
    #     prod_details["description"] = [product.find(class_="col-sm-6 product__title product__view").get_text().strip()]
    try:
        prod_details["original_price"] = [get_price(product.find("div", class_="precos").find("del").get_text().strip())]
    except (AttributeError, IndexError):
        prod_details["original_price"] = [get_price(product.find("div", class_="precos").find_all("span")[-1].get_text().strip())]

    prod_details["final_price"] = [get_price(product.find("div", class_="precos").find_all("span")[-1].get_text().strip())]
    return prod_details


def get_prod_list(url):
    response = requests.get(url)
    if response.status_code == 200:
        print(f"Parsing url {url}")
    else:
        print(f"Encountered status code {response.status_code} while trying to parse!")
    soup = BeautifulSoup(response.content, features='lxml')
    products = soup.find_all("div", class_ = 'info')
    try:
        next_url = soup.find("a",class_="next")["href"]
    except TypeError:
        next_url = ""

    return products, next_url


url = "https://www.babyartikel.de/cat/hochstuehle-co"
next_url = "dummy"
product_consolidated = pd.DataFrame()
fout = "babyartikel.csv"
# next_url = "dummy"

while next_url != "":
    products, next_url = get_prod_list(url)
    url = "https://www.babyartikel.de" + next_url
    for product in products:
        product_consolidated = pd.concat([product_consolidated, get_prod_details(product)])
    product_consolidated.to_csv(fout,index=False)