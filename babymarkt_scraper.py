from numpy.core.fromnumeric import prod
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
    prod_details["source"] = ["babymarkt"]
    prod_details["brand"] = [product.find("div", class_="col-sm-6 product__brand").get_text().strip()]
    try:
        prod_details["description"] = [product.find(class_="col-sm-6 product__title product__view")["title"].strip()]
    except:
        prod_details["description"] = [product.find(class_="col-sm-6 product__title product__view").get_text().strip()]
    try:
        prod_details["original_price"] = [get_price(product.find("div", class_="product__price product__price--old").get_text().strip())]
    except AttributeError:
        prod_details["original_price"] = [get_price(product.find("div", class_="product__price").get_text().strip())]

    prod_details["final_price"] = [get_price(product.find("div", class_="product__price").get_text().strip())]
    return prod_details


def get_prod_list(url):
    response = requests.get(url)
    if response.status_code == 200:
        print(f"Parsing url {url}")
    else:
        print(f"Encountered status code {response.status_code} while trying to parse!")
    soup = BeautifulSoup(response.content, features='lxml')
    products = soup.find_all("article", class_ = 'product')
    try:
        next_url = soup.find("a",class_="pagination__link pagination__link--next")["href"]
    except TypeError:
        next_url = ""

    return products, next_url


url = "https://www.babymarkt.de/unterwegs/kinderwagen/?per-page=60"
next_url = "dummy"
product_consolidated = pd.DataFrame()
fout = "babymarkt.csv"
# next_url = "dummy"

while next_url != "":
    products, next_url = get_prod_list(url)
    url = "https://www.babymarkt.de" + next_url
    for product in products:
        product_consolidated = pd.concat([product_consolidated, get_prod_details(product)])
    product_consolidated.to_csv(fout,index=False)