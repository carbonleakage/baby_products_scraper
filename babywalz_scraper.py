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
    prod_details["source"] = ["babywalz"]
    try: 
        prod_details["brand"] = [product.find("div", class_="bw-product__brand").get_text().strip() + " " + product.find("div", class_="bw-product__subbrand").get_text().strip()]
    except:
        prod_details["brand"] = [product.find("div", class_="bw-product__brand").get_text().strip()]

    try:
        prod_details["description"] = [product.find(class_="bw-product__name")["title"].strip()]
    except:
        prod_details["description"] = [product.find(class_="bw-product__name").get_text().strip()]
    try:
        prod_details["original_price"] = [get_price(product.find("div", class_= re.compile("bw-product__price--old")).get_text().strip())]
        prod_details["final_price"] = [get_price(product.find("div", class_="bw-product__price--promotion").get_text().strip())]
    except AttributeError:
        try:
            prod_details["original_price"] = [get_price(product.find("span", class_=re.compile("bw-product__price--single")).get_text().strip())]
            prod_details["final_price"] = [get_price(product.find("span", class_=re.compile("bw-product__price--single")).get_text().strip())]
        except:
            prod_details["original_price"] = 0
            prod_details["final_price"] = 0

    return prod_details


def get_prod_list(url):
    response = requests.get(url)
    if response.status_code == 200:
        print(f"Parsing url {url}")
    else:
        print(f"Encountered status code {response.status_code} while trying to parse!")
    soup = BeautifulSoup(response.content, features='lxml')
    products = soup.find_all("div", class_ = 'text')
    try:
        next_url = soup.find("div",class_="bw-pagination__arrow bw-pagination__arrow--right").parent["href"]
    except TypeError:
        next_url = ""

    return products, next_url


url = "https://www.baby-walz.de/hochstuehle/"
next_url = "dummy"
product_consolidated = pd.DataFrame()
fout = "babywalz.csv"
# next_url = "dummy"

while next_url != "":
    products, next_url = get_prod_list(url)
    if url == next_url:
        break
    else:
        url = next_url
        # url = "https://www.babymarkt.de" + next_url
        for product in products:
            product_consolidated = pd.concat([product_consolidated, get_prod_details(product)])
        product_consolidated.to_csv(fout,index=False)