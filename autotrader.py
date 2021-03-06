from bs4 import BeautifulSoup
import requests
import collections
import csv
from concurrent.futures import ThreadPoolExecutor

Details = collections.namedtuple("Details", "year km transmission")


def car_details(car):
    """
    Return list of car details
    """
    title = car.find("span", class_="e-title").text
    if not title:
        return {}
    url = car.find("a")["href"]
    price = car.find("span", class_="e-price").text
    use_type = car.find("span", class_="e-type").text
    l = []
    for d in car.find("span", class_="e-icons").find_all("span"):
        l.append(d.get_text())

    if len(l) != 3:
        return {}
    details = Details(year=l[0], km=l[1], transmission=l[2])
    return {
        "price": price,
        "title": title,
        "use_type": use_type,
        "year": details.year,
        "km": details.km.replace(u'\xa0', u' '),
        "transmission": details.transmission,
        "url": url,
    }


def get_page_urls(total_pages):
    """
    get car details from the remainng pages
    """
    urls = []
    if not total_pages:
        return urls
    
    host = 'https://www.autotrader.co.za'
    for page in range(2, int(total_pages) + 1):
        url = f'{host}/cars-for-sale/mercedes-benz?pagenumber={page}'
        urls.append(url)
    return urls


def get_page(url):
    """
    Get html page from url
    """
    print(f'Working on url {url}')
    html = requests.get(url).text
    return BeautifulSoup(html, "html.parser")


def process_next_pages(html_pages, writer):
    for page in html_pages:
        cars = page.find_all("div", class_="b-result-tile")
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


def get_home_page(url):
    page = get_page(url)
    cars = page.find_all("div", class_="b-result-tile")
    with open("merc_for_sale.csv", "w") as sale_file:
        fields = ["title", "price", "use_type", "year", "km", "transmission", "url"]
        writer = csv.DictWriter(sale_file, fields)
        writer.writeheader()
        if len(cars) > 0:
            print(f"Found {len(cars)} cars")
            for car in cars:
                details = car_details(car)
                if details:
                    writer.writerow(details)
            links = page.find_all('li', class_='e-page-number')
            total_pages = links[-1].text
            all_url_pages = get_page_urls(total_pages)
            html_pages = get_next_pages(all_url_pages)
            process_next_pages(html_pages, writer)
        else:
            print("Unable to find cars")
            print(page)


get_home_page("https://www.autotrader.co.za/cars-for-sale/mercedes-benz")
