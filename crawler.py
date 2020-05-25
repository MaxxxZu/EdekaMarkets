import os
import time
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import random
import xlsxwriter


__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))


class Crawler:
    def __init__(self, start_url):
        self.start_url = start_url
        self.page_links = []

    def _get_web_driver(self, CHROME_PATH, headless=False):
        ua = UserAgent()
        userAgent = ua.random
        options = Options()
        if headless:
            options.add_argument('headless')
        options.add_argument('user-agent={0}'.format(userAgent))
        driver = webdriver.Chrome(options=options, executable_path=CHROME_PATH)
        return driver

    def get_page_links(self, driver):
        driver.get(self.start_url)
        time.sleep(3)  # waiting for the page to load
        assert 'EDEKA Marktsuche: Öffnungszeiten, Anfahrt' in driver.title
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        links_ul = soup.find('div', {
            'class': 'sp_marktsuche_crosslinking sp_toggle_group'
            }).find_all('ul')
        if links_ul:
            for link in links_ul:
                for page_link in link.find_all('li'):
                    self.page_links.append(
                        f'https://www.edeka.de/{page_link.find("a")["href"]}'
                        )

    def get_page(self, driver):
        markets = []
        for page_link in self.page_links:
            driver.get(page_link)
            time.sleep(3)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            pages = soup.find_all('div',
                                  {'class': "sp_market_item_section sp_head"}
                                  )
            for page in pages:
                market = []
                title = page.find('div',
                                  {'class': "sp_market_col"}
                                  ).find('strong').text
                full_address = page.find('div',
                                         {'class': "sp_market_col sp_address"}
                                         ).find_all('span')
                market.append(title)
                for address in full_address:
                    market.append(address.text)
                markets.append(market)
        return markets


class Output(object):
    def __init__(self, all_markets):
        self.all_markets = all_markets
        self.to_xls()

    def to_xls(self):
        print('to Xls')
        with xlsxwriter.Workbook(OUTPUT_LOCATION) as workbook:
            worksheet = workbook.add_worksheet()
            for row, value in enumerate(self.all_markets):
                for col, data in enumerate(value):
                    worksheet.write(row, col, data)


if __name__ == "__main__":
    START_URL = 'https://www.edeka.de/marktsuche.jsp'
    CHROME_PATH = os.path.join(__location__, 'chromedriver')
    OUTPUT_LOCATION = os.path.join(__location__, 'markets.xlsx')
    crawler = Crawler(START_URL)
    driver = crawler._get_web_driver(CHROME_PATH, headless=True)
    crawler.get_page_links(driver)
    markets = crawler.get_page(driver)
    driver.quit()
    Output(markets)
