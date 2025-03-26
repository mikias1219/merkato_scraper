from celery import shared_task
from bs4 import BeautifulSoup
import requests
import logging
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from .models import Category, Subcategory, Business

logging.basicConfig(level=logging.INFO)
DOMAIN = 'https://www.2merkato.com'
URL = 'https://www.2merkato.com/directory/'

def get_session_with_retries():
    session = requests.Session()
    retry_strategy = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    return session

@shared_task
def scrape_categories():
    session = get_session_with_retries()
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}
    try:
        response = session.get(URL, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        categories = soup.find_all('div', class_='row-fluid mtree_category')
        for category in categories:
            for a in category.find_all('a'):
                Category.objects.update_or_create(
                    name=a.get_text(strip=True),
                    defaults={'href': DOMAIN + a['href']}
                )
        logging.info("Step 1: Categories scraped successfully.")
    except Exception as e:
        logging.error(f"Error in Step 1 (Categories): {e}")

@shared_task
def scrape_subcategories(category_id):
    category = Category.objects.get(id=category_id)
    session = get_session_with_retries()
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}
    try:
        response = session.get(category.href, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        subcategories_div = soup.find('div', class_='row-fluid mtree_sub_category')
        if subcategories_div and (ul := subcategories_div.find('ul', class_='pad10')):
            for li in ul.find_all('li'):
                a = li.find('a')
                Subcategory.objects.update_or_create(
                    category=category,
                    name=a.get_text(strip=True),
                    defaults={'href': DOMAIN + a['href']}
                )
        logging.info(f"Step 2: Subcategories for {category.name} scraped successfully.")
    except Exception as e:
        logging.error(f"Error in Step 2 (Subcategories) for {category.name}: {e}")

@shared_task
def scrape_businesses(subcategory_id):
    subcategory = Subcategory.objects.get(id=subcategory_id)
    session = get_session_with_retries()
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}
    business_url = subcategory.href
    while business_url:
        try:
            response = session.get(business_url, headers=headers, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            businesses_div = soup.find('div', id='listings')
            if businesses_div:
                for listing in businesses_div.find_all('div', class_='span12 heading'):
                    h4 = listing.find('h4')
                    if h4 and (a := h4.find('a')):
                        details = scrape_business_details(DOMAIN + a['href'])
                        Business.objects.update_or_create(
                            subcategory=subcategory,
                            name=a.get_text(strip=True),
                            defaults={'href': DOMAIN + a['href'], 'details': details}
                        )
                next_page = soup.find('a', title='Next')
                business_url = DOMAIN + next_page['href'] if next_page else None
                time.sleep(2)
            else:
                business_url = None
        except Exception as e:
            logging.error(f"Error in Step 3 (Businesses) for {subcategory.name}: {e}")
            break

def scrape_business_details(business_url):
    session = get_session_with_retries()
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}
    try:
        response = session.get(business_url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        details_table = soup.find('table', class_='table-condensed')
        details = {}
        if details_table:
            for row in details_table.find_all('tr'):
                cols = row.find_all('td')
                if len(cols) == 2:
                    details[cols[0].get_text(strip=True)] = cols[1].get_text(strip=True)
        return details
    except Exception as e:
        logging.error(f"Error scraping details from {business_url}: {e}")
        return {}