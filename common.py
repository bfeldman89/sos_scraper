#!/usr/bin/env /python
"""This module provides a function for shipping logs to Airtable."""

import os
import time
from airtable import Airtable
from documentcloud import DocumentCloud
from twython import Twython


airtab_log = Airtable(os.environ['log_db'],
                      table_name='log',
                      api_key=os.environ['AIRTABLE_API_KEY'])

airtab_sos = Airtable(os.environ['other_scrapers_db'],
                      table_name='exec_orders',
                      api_key=os.environ['AIRTABLE_API_KEY'])

airtab_tweets = Airtable(os.environ['botfeldman89_db'],
                         table_name='scheduled_tweets',
                         api_key=os.environ['AIRTABLE_API_KEY'])



dc = DocumentCloud(username=os.environ['MUCKROCK_USERNAME'],
                   password=os.environ['MUCKROCK_PW'])

muh_headers = {"Content-Type": "application/json; charset=utf-8",
               "Pragma": "no-cache",
               "Accept": "*/*",
               "Accept-Language": "en-us",
               "Accept-Encoding": "gzip, deflate, br",
               "Cache-Control": "no-cache",
               "Host": "www.sos.ms.gov",
               "Origin": "https://www.sos.ms.gov",
               "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Safari/605.1.15",
               "Referer": "https://www.sos.ms.gov/content/executiveorders/default.aspx",
               "Content-Length": "0",
               "Connection": "keep-alive",
               "Cookie": "f5_cspm=1234; _ga=GA1.2.1800542741.1584480254; _gat=1; _gid=GA1.2.639081259.1585870866; f5avraaaaaaaaaaaaaaaa_session_=NOKMMGKKIAGOJCILJLKFGAFONADMLGLLFPLFFNCONMMEHKMOHAHFCHKAAHHIDFALMPKDDNOLFLPJKNEFPKPAFOOCCHHPBMOKANAGKCEHOAMFKIGEMNFOFPPGGHOKMPEP; BIGipServerpl_sos_web_server_ext_https=rd1o00000000000000000000ffff0a0d3b0bo443; BIGipServerpl_msi_prod_https=rd1o00000000000000000000ffff0a0df71fo443",
               "X-Requested-With": "XMLHttpRequest"}

tw = Twython(os.environ['TWITTER_APP_KEY'], os.environ['TWITTER_APP_SECRET'],
             os.environ['TWITTER_OAUTH_TOKEN'], os.environ['TWITTER_OAUTH_TOKEN_SECRET'])


my_funcs = {'scrape_exec_orders': 'recBvGm8iIBnMQyRy'}


def wrap_from_module(module):
    def wrap_it_up(t0, new=None, total=None, function=None):
        this_dict = {
            'module': module,
            'function': function,
            '_function': my_funcs[function],
            'duration': round(time.time() - t0, 2),
            'total': total,
            'new': new
        }
        airtab_log.insert(this_dict, typecast=True)

    return wrap_it_up
