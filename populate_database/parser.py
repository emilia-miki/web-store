from bs4 import BeautifulSoup
import psycopg2
import urllib.request, urllib.error, urllib.parse
from random import Random
from typing import Tuple
from decimal import Decimal, InvalidOperation

conn = psycopg2.connect(host="localhost", port=5432, database="webstoredb",
                        user="postgres", password="admin")

cur = conn.cursor()

base_url = 'https://www.fashionnova.com'
url_men_menu = 'https://www.fashionnova.com/pages/men'

rand = Random()

def get_bs(url: str) -> BeautifulSoup:
    response = urllib.request.urlopen(url)
    if response.status != 200:
        raise Exception()
    content = response.read().decode("UTF-8")
    print(content)
    return BeautifulSoup(content)

def get_links(url: str, left: int, right: int) -> list[Tuple[str, str]]:
    bs = get_bs(url)
    link_elements = bs.find_all("a", class_="menu-category__link")[left:right]
    links = [el.attrs["href"] for el in link_elements]
    category_elements = bs.find_all("div", class_="menu-category__item-title")[left:right]
    categories = [str(el.string).strip() for el in category_elements]
    return zip(links, categories)

def parse_product(link: str, category: str) -> None:
    url = base_url + link
    try:
        bs = get_bs(url)
    except:
        return

    name_element = bs.find("h1", class_="product-info__title")
    name = str(name_element.string)
    print(name)

    description_element = bs.select_one("div.product-info__details-body > ul")
    try:
        description = description_element.get_text().strip()
    except AttributeError:
        print(bs.string)

    image_element = bs.find("button", 
                           class_="product-slideshow__syte-button syte-discovery-modal")
    img = image_element.attrs["data-image-src"]

    price_element = bs.find("div", class_="product-info__price-line")
    price_string = str(price_element)
    price_li = price_string.find("$")
    price_ri1 = price_string.find("&", price_li)
    price_ri2 = price_string.find("<", price_li)
    price_ri = min(price_ri1, price_ri2)
    price_li += 1
    price = price_string[price_li:price_ri]
    try:
        price = Decimal(price)
    except InvalidOperation:
        print("invalid price")
        print(bs.string)
        return

    left = rand.randint(0, 20)

    print(f"{name[:5]} {description[:5]} {category[:5]} {str(price)[:5]} {left} {img[:5]}")

    cur.execute("""INSERT INTO api_product (name, description, category, price, "left", img)
                   VALUES (%s, %s, %s, %s, %s, %s);""",
                (name, description, category, price, left, img))

    if cur.rowcount != 1:
        raise Exception()
    

def parse_products(link: str, category: str) -> None:
    print(f"Parsing {category}")

    url = base_url + link
    bs = get_bs(url)
    number_of_products = rand.randint(12, 24)
    link_elements = bs.select(
        "div.product-tile__product-title > a")[:number_of_products]
    links = [el.attrs["href"] 
             for el in link_elements]
    print(links)

    for link in links:
        parse_product(link, category)

    print("")

women_links = get_links(base_url, 5, 17)
men_links = get_links(url_men_menu, 4, 11)

print("Parsing Women's categories")
for link, category in women_links:
    parse_products(link, f'Women {category}')

print("Parsing Men's categories")
for link, category in men_links:
    parse_products(link, f'Men {category}')

conn.commit()

cur.close()
conn.close()
