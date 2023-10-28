import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import os

base_url = 'https://www.sweetwaterorganiccoffee.com/coffee/?page='
urls = [f'{base_url}{page}' for page in range(1,4)]

def get_product_info(url: str):
    response = requests.get(url)
    if response.status_code == 200:
        details = {}
        soup = BeautifulSoup(response.content)
        # Get the product details page and iterate to find all information
        
        # Price
        price = ''.join(re.findall(string=soup\
                           .find('span', class_='price-value')\
                           .get_text(strip=True),
                           pattern=r'[0-9.]'))
        details['price'] = price
        # flavor details
        labels = ['aroma','body','flavor','acidity']
        items = soup.find_all('span', class_='product-info-value')
        for label, item in zip(labels, items):
            details[label] = item.get_text(strip=True)

        
        # Review stars and count
        try:
            star_review_count = len(soup\
                                    .find('span', class_='product-rating')\
                                    .find_all('span', class_='icon icon-star'
                                    ))

            review_count = ''.join(re.findall(
                                    string=soup\
                                        .find('h3', class_='section-title')\
                                        .get_text(strip=True),
                                    pattern = r'[\d]'
                                      ))
        except:
            star_review_count, review_count = [0,0]
        
        details['stars'] = int(star_review_count)
        details['reviews'] = int(review_count)
        details['url'] = url
        
    return details

    

def get_html(url: str):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # Items are stored as div classes called product-item-details
        divs = soup.find_all('div', class_='product-item-details')
        products = []
        for div in divs:
            # Parse div tag, get all <a></a> tags which store the link and name
            a_tag = div.find('a')
            if a_tag is not None:
                link_to_item = a_tag.get('href')
                name = a_tag.get('alt')
                # Call function to extract product information
                details = get_product_info(link_to_item)
                
                df = pd.DataFrame.from_dict({name: details}, orient='index')
                products.append(df)
                
        return pd.concat(products)

coffee = pd.concat([get_html(url) for url in urls])
