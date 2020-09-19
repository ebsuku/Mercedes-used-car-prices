from bs4 import BeautifulSoup
import requests
import collections
import csv
from concurrent.futures import ThreadPoolExecutor
import time
import re

Details = collections.namedtuple("Details", "year km transmission petrol")


def car_details(car):
    """
    Return list of car details
    """
    title_1 = car.find("p").text
    title_2 = car.find("h3").text.replace("\n", "").strip()
    title = title_1 + " " + title_2
    if not title:
        return {}
    url = car.find("a")["href"]
    price = car.find_all("span")[4].text if car.find_all("span")[4] else ""
    year = car.find("i", class_="ye").text if car.find("i", class_="ye") else ""
    transmission = car.find("i", class_="tr").text if car.find("i", class_="tr") else ""
    km = car.find("i", class_="mi").text if car.find("i", class_="mi") else ""
    petrol = car.find("i", class_="fu").text if car.find("i", class_="fu") else ""

    return {
        "price": price,
        "title": title,
        "year": year,
        "km": km,
        "transmission": transmission,
        "url": url,
        "petrol": petrol,
    }


def get_page_urls(total_pages):
    """
    get car details from the remainng pages
    """
    urls = []
    if not total_pages:
        return urls

    # host = "https://www.cars.co.za"
    for page in range(2, int(total_pages) + 1):
        url = f"https://www.automart.co.za/cars/mercedes-benz/page{page}"
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
        cars = page.find_all("div", class_="card p-b-sm")
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
    count = page.find("div", class_="result-items-container").get_text()
    count = count.replace("\n", "")
    m = re.search(r"(?P<total>\d+)", count)
    if m.group("total"):
        return int(m.group("total")) / 20 + 1
    return 0


def get_home_page(url):
    page = get_page(url)
    cars = page.find_all("div", class_="card p-b-sm")
    with open("data/automart.csv", "w") as sale_file:
        fields = ["title", "price", "year", "km", "url", "petrol", "transmission"]
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
            print(page)


get_home_page("https://www.automart.co.za/cars/mercedes-benz/")
