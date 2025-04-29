import logging
import requests
from bs4 import BeautifulSoup
import csv
import time
import datetime
import os
import configparser

# Load config
config = configparser.ConfigParser()
config.read('config.ini')
START_URL    = config['settings']['start_url']
WAIT_SECONDS = float(config['settings']['wait_seconds'])
OUTPUT_CSV   = config['settings']['output_csv']
HEADERS      = {'User-Agent': config['settings']['user_agent']}

# Setup logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    filename='logs/main.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)
logger = logging.getLogger()

def scrape_page(url):
    logger.info(f"Scraping {url}")
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    items = []
    container = soup.select_one('#js-product-list')
    if not container:
        logger.error("Produktų konteinerio neradau")
        return items, None
    for card in container.select('article.product-miniature'):
        # Name & link
        a = card.select_one('h2.h3.product-title a')
        name = a.get_text(strip=True) if a else ''
        link = a['href'] if a else ''

        # Price
        price_el = card.select_one('span.current-price') or card.select_one('.product-price-and-shipping .price')
        price = price_el.get_text(strip=True) if price_el else ''

        # Image URL
        img = card.select_one('.thumbnail-container img')
        img_url = img.get('data-src') or img.get('src') or ''

        items.append({'name':name,'price':price,'link':link,'image_url':img_url})

    next_sel = soup.select_one('ul.pagination li a.next')
    next_url = next_sel['href'] if next_sel else None
    return items, next_url

def main():
    url = START_URL
    all_products = []
    while url:
        items, url = scrape_page(url)
        all_products.extend(items)
        time.sleep(WAIT_SECONDS)
    logger.info(f"Rasta produktų: {len(all_products)}")
    # Save CSV
    now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = OUTPUT_CSV.replace('.csv',f'_{now}.csv')
    with open(filename,'w',newline='',encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['name','price','link','image_url'], delimiter=';')
        writer.writeheader()
        for row in all_products:
            writer.writerow(row)
    logger.info(f"Duomenys įrašyti į {filename}")

if __name__ == "__main__":
    main()
