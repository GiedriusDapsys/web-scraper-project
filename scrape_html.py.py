```python
import requests
from bs4 import BeautifulSoup
import csv
import time

# Pagrindinis kategorijos puslapis
t_START_URL = 'https://ailena.lt/lt/kartonines-dezes/'
# Kliento imitacija naršyklės
HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/124.0.0.0 Safari/537.36'
    )
}

def scrape_page(url):
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    items = []
    container = soup.select_one('#js-product-list')

    for card in container.select('article.product-miniature'):
        name_el  = card.select_one('.product-title a')
        price_el = card.select_one('.product-price-and-shipping .price')
        img_el   = card.select_one('.thumbnail-container img')

        name    = name_el.get_text(strip=True) if name_el else ''
        price   = price_el.get_text(strip=True) if price_el else ''
        link    = name_el['href'] if name_el else ''
        img_url = img_el.get('data-src') or img_el.get('src') or ''

        items.append({
            'name': name,
            'price': price,
            'link': link,
            'image_url': img_url
        })

    next_sel = soup.select_one('ul.pagination li a.next')
    next_url = next_sel['href'] if next_sel and next_sel.get('href') else None
    return items, next_url

def main():
    url = START_URL
    all_products = []

    while url:
        print(f"Scraping: {url}")
        items, url = scrape_page(url)
        all_products.extend(items)
        time.sleep(1)

    print(f"Viso produktų surinkta: {len(all_products)}")

    # CSV su BOM, kad Excel rodytų € teisingai
    with open('products_html.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'price', 'link', 'image_url'])
        writer.writeheader()
        for prod in all_products:
            writer.writerow(prod)

    print("✅ CSV sukurtas: products_html.csv")

if __name__ == "__main__":
    main()
```
