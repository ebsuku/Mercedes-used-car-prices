from bs4 import BeautifulSoup
import requests
import collections
import csv
from concurrent.futures import ThreadPoolExecutor
import time

Details = collections.namedtuple("Details", "year km transmission petrol")


def car_details(car):
    """
    Return list of car details
    """
    title = car.find('a',class_='vehicle-list__vehicle-name').text
    if not title:
        return {}
    url = car.find("a")["href"]
    price = car.find('span', class_='vehicle-list__vehicle-price').text
    l = []
    for d in car.find_all('li', class_='vehicle-list__vehicle-attr'):
        l.append(d.get_text())

    if len(l) != 4:
        return {}
    details = Details(year=l[0], km=l[1], transmission=l[2], petrol=l[3])
    return {
        "price": price.replace('\n', '').replace(u'\xa0', u' '),
        "title": title,
        "year": details.year,
        "km": details.km.replace(u'\xa0', u' '),
        "transmission": details.transmission,
        "url": url,
        'petrol': details.petrol
    }


def get_page_urls(total_pages):
    """
    get car details from the remainng pages
    """
    urls = []
    if not total_pages:
        return urls
    
    host = 'https://www.cars.co.za'
    for page in range(2, int(total_pages) + 1):
        url = f'{host}/usedcars/Mercedes-Benz/?P={page}'
        urls.append(url)
    return urls


def get_page(url):
    """
    Get html page from url
    """
    time.sleep(2)
    print(f'Working on url {url}')
    html = requests.get(url).text
    return BeautifulSoup(html, "html.parser")


def process_next_pages(html_pages, writer):
    for page in html_pages:
        cars = page.find_all('div', class_='vehicle-list__item')
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
    links = page.find('div', 'resultsnum pagination__page-number pagination__page-number_right')
    text = links.text
    fix = text.replace('\n','').split('of')
    total_number = fix[1].strip()
    return int(total_number) / 20 + 1
    


def get_home_page(url):
    page = get_page(url)
    cars = page.find_all('div', class_='vehicle-list__item')
    with open("carscoza.csv", "w") as sale_file:
        fields = ["title", "price", "petrol", "year", "km", "transmission", "url"]
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


get_home_page("https://www.cars.co.za/usedcars/Mercedes-Benz/")
