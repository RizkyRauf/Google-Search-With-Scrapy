# -*- Coding: utf-8 -*-

from email import header
import logging
import re
from datetime import date, datetime, timedelta
from scrapy import Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Request
from scrapy_selenium import SeleniumRequest
from scrapy.item import Item, Field
import json

import pandas as pd

from textblob import TextBlob

from lxml import html
from bs4 import BeautifulSoup
import requests


class ItemBerita(Item):
  judul = Field()
  reporter = Field()
  tanggal = Field()
  konten = Field()
  link = Field()

logger = logging.getLogger()

Konten_media = []
Konten_date = []
Konten_title = []
Konten_teks = []
Konten_url = []

class GoogleSpider(CrawlSpider):

    name = 'googlefix'
    url_raw = 'https://www.google.com/search?q='

    url_list = []
    
    key = [
        'Partai Kebangkitan Bangsa',
        'pkb'
        ]
    
    for keyword in key:
        page_number = ['0','10','20','30','40','50','60','70','80','90','100']
        for number in page_number:
            url = "{}{}&start={}".format(url_raw, keyword, number)
            url_list.append(url)

            
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36' }

    def start_requests(self):
       for url in self.url_list:
        yield Request (
            url=url,
            callback=self.parse_item,
            headers=self.headers
        )

    def parse_item(self, response):
        r = requests.get(self.url)
        soup = BeautifulSoup(r.text, 'html.parser')
        data = soup.findAll('div', {'class':'Gx5Zad fP1Qef xpd EtOod pkphOe'})
        for i in data:
            title = i.find('div', {'class':'BNeawe vvjwJb AP7Wnd'})
            title = title.text
            Konten_title.append(title)
                

            link = i.find('a')
            link = link['href']
            link = link.split('&sa=')
            link = link[0]
            if '/url?q=' in link:
                link = link.split('/url?q=')
                link = link[1]
                Konten_url.append(link)

            else:
                link = link
                Konten_url.append(link)

            media = i.find('div', {'class':'BNeawe UPmit AP7Wnd lRVwie'})
            if media:
                media = media.text
                media = media.split(' ')
                media = media[0]
                Konten_media.append(media)

            date = i.find('div', {'class':'BNeawe s3v9rd AP7Wnd'})
            for data in date:
                date = data.text
                date = date[:11]
                if '20' in date:
                    date = re.sub(r'[^A-Za-z0-9]+', ' ', date)
                    Konten_date.append(date)

                else:
                    date = datetime.now()
                    date = date.strftime('%d %b %Y')
                    Konten_date.append(date)
                

            teks = i.find('div', {'class':'BNeawe s3v9rd AP7Wnd'})
            teks = teks.text
            if '202' in teks:
                teks = teks[13:]
                Konten_teks.append(teks)

            else:
                teks = teks
                Konten_teks.append(teks)


        
        df = pd.DataFrame({
            'Nama Media': Konten_media,
            'Tanggal': Konten_date,
            'Judul': Konten_title,
            'Tulisan': Konten_teks,
            'Url': Konten_url,
        })

        df.drop_duplicates()
        df.to_csv(datetime.now().strftime("%d-%m-%Y") + '{}.xlsx'.format(self.keyword), index=False, encoding='utf-8')
