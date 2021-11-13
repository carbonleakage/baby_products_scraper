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
    prod_details["source"] = ["babyone"]
    # try: 
    #     prod_details["brand"] = [product.find("div", class_="product-brand").get_text().strip() + " " + product.find("div", class_="bw-product__subbrand").get_text().strip()]
    # except:
    prod_details["brand"] = [product.find("div", class_="product-brand").get_text().strip()]

    # try:
    #     prod_details["description"] = [product.find("div", class_="product-name")["title"].strip()]
    # except:
    prod_details["description"] = [product.find("div", class_="product-name").get_text().strip()]
    try:
        prod_details["original_price"] = [get_price(product.find("span", class_= "price-standard").get_text().strip())]
        prod_details["final_price"] = [get_price(product.find("span", class_="price-sales").get_text().strip())]
    except AttributeError:
        try:
            prod_details["original_price"] = [get_price(product.find("span", class_="price-sales").get_text().strip())]
            prod_details["final_price"] = [get_price(product.find("span", class_="price-sales").get_text().strip())]
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
    products = soup.find_all("div", class_ = 'product-tile-section product-information')
    
    return products


product_consolidated = pd.DataFrame()
fout = "babyone.csv"
# next_url = "dummy"

for i in range(48,529,48):
    url = f"https://www.babyone.de/kombi-kinderwagen?start={i}&sz=48&format=infinite"
    products= get_prod_list(url)
    for product in products:
        product_consolidated = pd.concat([product_consolidated, get_prod_details(product)])
    product_consolidated.to_csv(fout,index=False)

