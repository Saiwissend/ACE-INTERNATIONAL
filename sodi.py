import scrapy
import re
import math
import warnings
from deep_translator import GoogleTranslator


class SodiSpider(scrapy.Spider):
    name = "sodi"
    start_urls = ["https://www.sodimac.com.mx/sodimac-mx/"]
    warnings.filterwarnings('ignore')
    def parse(self, response):
        for url_collection in response.xpath('//div[contains(@class,"ListItem-module_level-3")]/parent::a'):
            url = (url_collection.xpath('./@href').get('').strip())            
            yield response.follow(url,callback=self.list_collection)
    def list_collection(self,response):
        product_count = ''.join([i.replace('(','').replace(')','').replace('productos','').strip() for i in response.xpath('//div[contains(@class,"product-count")]/text()').getall()]).strip()
        if product_count:
            product_count_percentage = math.ceil(int(product_count)/28)            
            for page_count in range(1,int(product_count_percentage)+1):
                next_page_url = response.url+f'?currentpage={page_count}'
                yield response.follow(next_page_url,callback=self.url_collection,dont_filter=True)
        else:        
            yield response.follow(response.url,callback=self.url_collection,dont_filter=True)
    def url_collection(self,response):
            print('ENTERING   RESPONSE  URL ------>>>>>>>>>>>>>>  ',response.url)
            if response.xpath('//div[contains(@class,"search-results-products-container")]'):
                for url_collection in response.xpath('//div[contains(@class,"search-results-products-container")]/div//a[@id="title-pdp-link"]'):
                    url = (url_collection.xpath('./@href').get('').strip())                    
                    yield response.follow(url,callback=self.product_collection,cb_kwargs ={'navigation_url':response.url},dont_filter=True)        
    def product_collection(self,response,navigation_url):
        item = {}
        item['product_url'] = response.url
        title = response.xpath('//h1[contains(@class,"product-title")]/text()').get('').strip()
        if title:
            
            # item['title']  = title
            item['title'] = GoogleTranslator(source='es', target='en').translate(text=title)
        else:
            item['title'] = ''
        
        item['sku'] = re.findall(r'\"sku\"\:\s*\"([^>]*?)\"\,\s*"',response.text)[0].strip()
        item['image'] = re.findall(r'\"image\"\:\s*\"([^>]*?)\"\,\s*"description',response.text)[0].strip()
        item['price'] = re.findall(r'\"price\"\:\s*\"([^>]*?)\"\,\s*"priceCurrency',response.text)[0].strip()
        # item['price'] =  response.xpath('//div/@data-price').get('').strip()
        item['striked_price'] =  ''.join(response.xpath('//div[contains(@class,"product-basic-info")]//div[contains(@class,"secondary")]//text()').getall()).replace('$','').replace(',','').replace('c/u','').strip()
        item['brand'] = response.xpath('//div[contains(@class,"product-brand")]/text()').get('').strip()
        item['navigation_url'] = navigation_url
        # breakpoint()
        yield item
        
    