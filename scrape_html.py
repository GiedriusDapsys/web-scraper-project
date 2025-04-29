import configparser
import requests
from bs4 import BeautifulSoup
import csv
import time
import os
import logging

# Sukurk katalogą logams
os.makedirs('logs', exist_ok=True)
# Įjungti log'inimą į logs/main.log
logging.basicConfig(
    filename='logs/main.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)
logger = logging.getLogger()

# Nuskaityti konfigūraciją
config = configparser.ConfigParser()
config.read('config.ini')
settings = config['settings']

START_URL = settings.get('start_url')
WAIT_SECONDS = settings.getfloat('wait_seconds', fallback=1.0)
OUTPUT_CSV = settings.get('output_csv')
USER_AGENT = settings.get('user_agent')
HEADERS = {'User-Agent': USER_AGENT}


def scrape_page(url):
    logger.info(f"Scraping: {url}")
    resp = requests.get(url, headers=HEADERS)
    try:
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return [], None
    soup = BeautifulSoup(resp.text, 'html.parser')

    items = []
    container = soup.select_one('#js-product-list')
    if not container:
        logger.error("Could not find product container on page")
        return items, None

    for card in container.select('article.product-miniature'):
        a = card.select_one('h2.h3.product-title a')
        name = a.get_text(strip=True) if a else ''
        link = a['href'] if a else ''

        price_el = card.select_one('span.current-price') or card.select_one('.product-price-and-shipping .price')
        price = price_el.get_text(strip=True) if price_el else ''

        img_el = card.select_one('.thumbnail-container img')
        img_url = img_el.get('data-src') or img_el.get('src') or ''

        items.append({'name': name, 'price': price, 'link': link, 'image_url': img_url})

    next_sel = soup.select_one('ul.pagination li a.next')
    next_url = next_sel['href'] if next_sel and next_sel.get('href') else None
    return items, next_url


def main():
    url = START_URL
    all_products = []

    while url:
        items, url = scrape_page(url)
        all_products.extend(items)
        time.sleep(WAIT_SECONDS)

    logger.info(f"Total products found: {len(all_products)}")

    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'price', 'link', 'image_url'], delimiter=';')
        writer.writeheader()
        for prod in all_products:
            writer.writerow(prod)

    logger.info(f"Data written to CSV: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
