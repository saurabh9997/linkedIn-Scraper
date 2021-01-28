import scrapy
from selenium import webdriver
from parsel import Selector
# from scrapy.selector import Selector
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from time import sleep
from scrapy.linkextractors import LinkExtractor
from selenium.webdriver.common.keys import Keys
import pandas as pd
import fake_useragent


class LinkedIn(scrapy.Spider):
    name = 'LinkedIn'
    start_urls = 'https://www.google.com'
    linkedin_url = 'https://www.linkedin.com'
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "accept-encoding": "gzip, deflate, sdch, br",
        "accept-language": "en-US,en;q=0.8,ms;q=0.6",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
    }
    AUTOTHROTTLE_ENABLED = True
    AUTOTHROTTLE_START_DELAY = 10
    allowed_domains = ["linkedin.com"]
    handle_httpstatus_list = [999]
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    def start_requests(self):
        yield scrapy.Request(self.start_urls, callback=self.google_search)

    def linkedIn_login(self):
        self.driver.get(self.linkedin_url)
        linkedin_username = 'saurabh.j@eazr.in'
        linkedin_password = 'S@jha1234'
        username = self.driver.find_element_by_id('session_key')
        # linkedin_username, linkedin_password = par.get_params()
        username.send_keys(linkedin_username)
        sleep(1)

        password = self.driver.find_element_by_id('session_password')
        password.send_keys(linkedin_password)
        sleep(1)

        sign_in_button = self.driver.find_element_by_xpath('/html/body/main/section[1]/div[2]/form/button')
        sign_in_button.click()
        sleep(1)

    def google_search(self, response):
        self.linkedIn_login()
        self.driver.get(response.url)
        sleep(3)
        search_query1 = 'site:linkedin.com/in/ AND "computer engineer" AND "Mumbai"'
        # file_name = 'results_file.csv'
        search_query = self.driver.find_element_by_xpath('//*[@id="tsf"]/div[2]/div[1]/div[1]/div/div[2]/input')
        search_query.send_keys(search_query1)
        sleep(1)

        search_query.send_keys(Keys.RETURN)
        sleep(3)
        # res = self.driver.page_source
        sleep(0.5)
        yield scrapy.Request(self.driver.current_url, callback=self.google_link)

    def google_link(self, response):
        df = pd.DataFrame()
        xlink = LinkExtractor()
        link_list = []
        link_text = []
        ignored_links = {'maps', 'news', 'videos', 'images', 'shopping', 'books', 'past hour', 'past 24 hours',
                         'past week', 'past month', 'past year', 'verbatim', 'sign in', 'recruiting for start-ups',
                         'technology recruitment', 'register today', 'tech job news',
                         'report inappropriate predictions', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'next'}
        for link in xlink.extract_links(response):
            # print(link.url)
            if len(str(link)) > 200 or 'Journal' in link.text:
                print(len(str(link)), link.text, link, "\n")
                if 'linkedin' in link.url and link.text.lower() not in ignored_links:
                    link_list.append(link.url)
                    link_text.append(link.text)
        df['links'] = link_list
        df['link_text'] = link_text
        df.to_csv('a.csv')
        for link in link_list:
            yield scrapy.Request(link, callback=self.parse, headers=self.headers)

    def parse(self, response):
        self.driver.get(response.url)
        sleep(3)
        name = response.css("#ember53 > div.ph5.pb5 > div.display-flex.mt2 > div.flex-1.mr5 > ul.pv-top-card--list.inline-flex.align-items-center > li.inline.t-24.t-black.t-normal.break-words ::text").get()
        bio = response.css("#ember53 > div.ph5.pb5 > div.display-flex.mt2 > div.flex-1.mr5 > h2 ::text").get()
        location = response.css("#ember53 > div.ph5.pb5 > div.display-flex.mt2 > div.flex-1.mr5 > ul.pv-top-card--list.pv-top-card--list-bullet.mt1 > li.t-16.t-black.t-normal.inline-block ::text").get()
        sleep(1)
        yield{
            'name': name,
            'bio': bio,
            'location': location,
            'link': response.url
            }