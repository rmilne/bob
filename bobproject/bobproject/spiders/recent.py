# -*- coding: utf-8 -*-

import datetime
import scrapy
import sqlite3
from email.utils import parsedate_tz, mktime_tz


class RecentSpider(scrapy.Spider):
    name = "recent"
    allowed_domains = ["www.iheartradio.ca"]
    start_urls = ['http://www.iheartradio.ca/99-9-bob-fm/99-9-bob-fm-1.1748024/recently-played-1.1748025?mode=history&ot=ajax.ot']

    def __init__(self):
        self.db = sqlite3.connect('bob.db',
                detect_types=sqlite3.PARSE_DECLTYPES)
        self.cur = self.db.cursor()
        self.create_table()

    def create_table(self):
        self.cur.execute('''CREATE TABLE IF NOT EXISTS 
        bob(title text, band text, timestamp date,
        UNIQUE (title, band, timestamp));''')
        self.db.commit()

    def parse(self, response):
        #self.log('here')
        #self.log('songs: %s' % response.css("ul.songs li"))
        for song in response.css("ul.songs li"):
            #self.log('song %s' % song)
            titleband = song.css("span::text").extract()[0]
            timestamp = song.css('time::attr(datetime)').extract()[0]
            #self.log('date %s' % timestamp)
            #date = datetime.datetime.strptime(timestamp, '%a %b %d %H:%M:%S %Z %Y')
            date = datetime.datetime.utcfromtimestamp(mktime_tz(parsedate_tz(timestamp)))
            #self.log('type %s' % type(date))
            title, _, band = titleband.partition(u' ̵ ')
            title = title.strip('"')
            #self.log('titleband: >%s<' % titleband)
            data = {'title': title, 'band': band, 'date': date}
            try:
                self.cur.execute('''INSERT INTO bob (title, band, timestamp) VALUES (?, ?, ?)''',  (data['title'], data['band'], data['date'],))
                self.db.commit()
                self.log('title, band: >%s< >%s<  inserted' % (title, band))
            except sqlite3.IntegrityError as e:
                self.log('found duplicate, not inserted')
                pass
            yield data


