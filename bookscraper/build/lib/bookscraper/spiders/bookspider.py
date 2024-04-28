import scrapy
from bookscraper.items import BookItem
from urllib.parse import urlencode
import random

API_KEY = 'cc8cd688-2fe6-4ad6-8ce7-e6992613b479'

def get_proxy_url(url):
    payload = {'api_key': API_KEY, 'url': url}
    proxy_url = 'https://proxy.scrapeops.io/v1/?' + urlencode(payload)
    return proxy_url

class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com", "proxy.scrapeops.io"]
    start_urls = ["https://books.toscrape.com"]

    def start_requests(self):
        yield scrapy.Request(url=get_proxy_url(self.start_urls[0]), callback=self.parse)

    def parse(self, response):
        books = response.css('article.product_pod')
        for book in books:
            relative_url = book.css('h3 a').attrib['href']
            if 'catalogue/' in relative_url:
                book_url = 'https://books.toscrape.com/' + relative_url
            else:
                book_url = 'https://books.toscrape.com/catalogue/' + relative_url
            yield scrapy.Request(url=get_proxy_url(book_url), callback=self.parse_book_page)

        next_page = response.css('li.next a ::attr(href)').get()
        if next_page is not None:
            if 'catalogue/' in next_page:
                next_page_url = 'https://books.toscrape.com/' + next_page
            else:
                next_page_url = 'https://books.toscrape.com/catalogue/' + next_page

            yield scrapy.Request(url=get_proxy_url(next_page_url), callback=self.parse)
    
    def parse_book_page(self, response):
        book = response.css("article.product_page")
        rows = response.css("table.table-striped tr")
        book_item = BookItem()

        book_item['url'] = response.url
        book_item['title'] = book.css("div.product_main h1::text").get()
        book_item['upc'] = rows[0].css("td::text").get()
        book_item['product_type'] = rows[1].css("td::text").get()
        book_item['price_excl_tax'] = rows[2].css("td::text").get()
        book_item['price_incl_tax'] = rows[3].css("td::text").get()
        book_item['tax'] = rows[4].css("td::text").get()
        book_item['availability'] = rows[5].css("td::text").get()
        book_item['num_reviews'] = rows[6].css("td::text").get()
        book_item['stars'] = book.css("p.star-rating").attrib['class']
        book_item['category'] = response.css('div.product_main').xpath("//ul[@class='breadcrumb']/li/preceding-sibling::li[1]/a/text()").get()
        book_item['description'] = book.xpath("//div[@id='product_description']/following-sibling::p/text()").get()
        book_item['price'] = book.css("div.product_main p.price_color::text").get()
        
        yield book_item
