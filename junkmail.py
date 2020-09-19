from bs4 import BeautifulSoup
import requests
import collections
import csv
from concurrent.futures import ThreadPoolExecutor
import time
import re


def car_details(car):
    """
    Return list of car details
    """
    title = car.find("a", class_="h2").text
    if not title:
        return {}
    url = car.find("a")["href"]
    price = car.find("h3").span.text
    year = re.search(r"^(?P<year>\d+)", title)
    if year:
        year = year.group("year")
    else:
        year = ""

    return {"price": price, "title": title, "url": url, "year": year}


def get_page_urls(total_pages):
    """
    get car details from the remainng pages
    """
    urls = []
    if not total_pages:
        return urls

    # host = "https://www.cars.co.za"
    for page in range(2, int(total_pages) + 1):
        url = f"https://www.junkmail.co.za/cars/mercedes-benz/page{page}"
        urls.append(url)
    return urls


def get_page(url):
    """
    Get html page from url
    """
    time.sleep(2)
    print(f"Working on url {url}")
    html = requests.get(url).text
    return BeautifulSoup(html, "html.parser")


def process_next_pages(html_pages, writer):
    for page in html_pages:
        cars = page.find_all("div", class_="search-result desktop-listing")
        for car in cars:
            details = car_details(car)
            if details:
                writer.writerow(details)


def get_next_pages(urls):
    futures_list = []
    html_pages = []
    with ThreadPoolExecutor(max_workers=17) as executor:
        for url in urls:
            futures = executor.submit(get_page, url)
            futures_list.append(futures)
        for f in futures_list:
            try:
                result = f.result(timeout=60)
                html_pages.append(result)
            except Exception as error:
                print(error)
    return html_pages


def page_links_config(page):
    count = page.find("div", class_="row m-b").find_all("b")[2].text
    return int(count) / 20


def get_home_page(url):
    page = get_page(url)
    cars = page.find_all("div", class_="search-result desktop-listing")
    with open("data/junkmail.csv", "w") as sale_file:
        fields = ["title", "price", "year", "url"]
        writer = csv.DictWriter(sale_file, fields)
        writer.writeheader()
        if len(cars) > 0:
            print(f"Found {len(cars)} cars")
            for car in cars:
                details = car_details(car)
                if details:
                    writer.writerow(details)

            total_pages = page_links_config(page)
            all_url_pages = get_page_urls(total_pages)
            html_pages = get_next_pages(all_url_pages)
            process_next_pages(html_pages, writer)
        else:
            print("Unable to find cars")


get_home_page("https://www.junkmail.co.za/cars/mercedes-benz")
