import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

commodity_Sites = {"Zinc" : "https://www.lme.com/en/metals/non-ferrous/lme-zinc#Summary",
                   "Aluminum" : "https://www.lme.com/en/metals/non-ferrous/lme-aluminium#Trading+summary",
                   "Copper" : "https://www.lme.com/en/metals/non-ferrous/lme-copper#Trading+summary"}

def create_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Firefox(options=options)

def LME_commodities(url):
    driver = create_driver()
    driver.get(url)
    try:
        # Wait for the table body to be loaded (more reliable than a specific cell)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'tbody.data-set-table__body'))
        )
    except Exception as e:
        print("Timed out waiting for page to load:", e)
        driver.quit()
        return None, None

    # Parse the page with BeautifulSoup
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    driver.quit()  # Close the browser after loading and parsing

    # Find the row for "3-month"
    rows = soup.find_all('tr', class_='data-set-table__row')
    for row in rows:
        contract_cell = row.find('th', attrs={'data-table-column-header': 'Contract'})
        if contract_cell and contract_cell.get_text(strip=True) == '3-month':
            bid_cell = row.find('td', attrs={'data-table-column-header': 'Bid'})
            offer_cell = row.find('td', attrs={'data-table-column-header': 'Offer'})

            if bid_cell and offer_cell:
                bid = round(float(bid_cell.get_text(strip=True).replace(',', ''))/2204.62,4)
                offer = round(float(offer_cell.get_text(strip=True).replace(',', ''))/2204.62,4)
                print("3-month Bid:", bid, "\n3-month Offer:", offer)
                return bid, offer

    print("3-month contract not found.")
    

def get_copper_prices(url="https://comexlive.org/copper/"):
    driver = create_driver()
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "main-table"))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        tables = soup.find_all("table", class_="main-table bold")
        high, low, open_price = None, None, None

        for table in tables:
            header_cells = table.find_all("td")
            headers = [cell.get_text(strip=True).lower() for cell in header_cells]
            if "high" in headers and "low" in headers and "open" in headers:
                data_row = table.find_all("tr")[1]
                data_cells = data_row.find_all("td")
                if len(data_cells) == 3:
                    high = float(data_cells[0].get_text(strip=True))
                    low = float(data_cells[1].get_text(strip=True))
                    open_price = float(data_cells[2].get_text(strip=True))
                break
        return high, low, open_price
    finally:
        driver.quit()

print('Aluminum')
aluminum_high, aluminum_low = LME_commodities(commodity_Sites['Aluminum'])
print('Zinc')
zinc_high, zinc_low = LME_commodities(commodity_Sites['Zinc'])
print('Copper')
copper_high, copper_low = LME_commodities(commodity_Sites['Copper'])
print('COMEX Copper')
comex_high, comex_low, comex_open = get_copper_prices()



from datetime import date, timedelta

yesterday = date.today() - timedelta(days=1)
yesterday_str = yesterday.strftime("%Y-%m-%d")

print(f"Today's date is {yesterday_str}")

from SupaUpload import supa_upload

print(f"Uploading to 'lme_copper'")
supa_upload(date=yesterday_str, low = copper_low, high=copper_high, last = (copper_high+copper_low)/2, table_name='lme_copper')

print(f"Uploading to 'lme_aluminum'")
supa_upload(date=yesterday_str, low = aluminum_low, high=aluminum_high, last = (aluminum_high+aluminum_low)/2, table_name='lme_aluminum')

print(f"Uploading to 'lme_zinc'")
supa_upload(date=yesterday_str, low = zinc_low, high=zinc_high, last = (zinc_high+zinc_low)/2, table_name='lme_zinc')

today_str = date.today().strftime("%Y-%m-%d")

print(f"Uploading to 'comex_copper'")
supa_upload(date=today_str, low = comex_low, high=comex_high, last = comex_open, table_name='comex_copper')
