import re
import scrapy
import warnings
import openpyxl
from os import getcwd,path
from datetime import datetime
from bs4  import BeautifulSoup
import os, os.path, time, json, pathlib


class harveySpider(scrapy.Spider):
    name = "truevalve"
    now_time = time.localtime()
    now_date = time.strftime("%d-%m-%Y", now_time)
    time_on = time.strftime("%I:%M %p", now_time)
    timer_start = time.time()
    current_date = datetime.now().strftime('%d_%m_%Y')
    current_timestamp = datetime.now()

#---------------------------------------------------- 
    wb = openpyxl.Workbook()
    data_sheet = wb.active
    data_sheet["A1"] = "product_url"
    data_sheet["B1"] = "id_of_product"
    data_sheet["C1"] = "product_name"
    data_sheet["D1"] = "old_price (₱) "
    data_sheet["E1"] = "sale_price (₱)"
    data_sheet["F1"] = "image_url"  

# ---------------------------------------------------- 
    
    max_row = 2
    max_sheet = 2
    temporary_value = 500
    # warnings.filterwarnings('ignore')
# ----------------------------------------------------


    def clean(self,text):
        '''remove extra spaces & junk character'''
        text = re.sub(r'\n+','',text)
        text = re.sub(r'\s+',' ',text)
        text = re.sub(r'\r+',' ',text)
        return text.strip()
    
    def start_requests(self):
        url = "https://pre-prod-api.gocart.ph/s5/api/v1/web/product/list"
        for num in  range(1,64):
            payload = json.dumps({
            "buId": "4",
            "pageNo":f'{num}',
            "pageSize": "100",
            "sortBy": "0",
            "storeCode": "503",
            "zoneNum": "2",
            })
            headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://gocart.ph',
            'Referer': 'https://gocart.ph/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'client': 'WEB',
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
            }
            yield scrapy.Request(url,method="POST",headers=headers,body=payload,callback=self.parse)
    def parse(self,response):
        item = {}
        json_validate = json.loads(response.text)
        if json_validate['data'] !=[]:
            for collect_id in json_validate['data']:
                sold_out = collect_id['soldOut']
                if sold_out ==True:
                    stock_status = 'OUT STOCK'
                else:
                    stock_status = 'IN STOCK'
                item['id_of_product'] = str(collect_id['id'])
                product_name= collect_id['name']
                item['stock_status'] = stock_status
                item['image_url'] = collect_id['image']
                item['old_price'] = collect_id['originalPrice']
                item['sale_price'] = (collect_id['price'])
                title_lower = product_name.lower().replace(' ','-').replace('#','21')
                item['product_url'] = f'https://gocart.ph/truevalue/product/{title_lower}?buId=4&productId={item["id_of_product"]}&storeCode=503&zoneNum=2&isGoSubscribe=false'
                print('PRODUCT_URL----->>>>',item['product_url'])
                yield item
            # response = requests.request("POST", url, headers=headers, data=payload,verify=False)