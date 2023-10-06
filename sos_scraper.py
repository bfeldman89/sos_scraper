# !/usr/bin/env python
"""This module does blah blah."""
import time
from io import BytesIO
import requests
from common import airtab_sos as airtab, client_v1, client_v2, dc, muh_headers, wrap_from_module

wrap_it_up = wrap_from_module('sos_scraper.py')


def get_images(dc_id):
    media_ids = []
    obj = dc.documents.get(dc_id)
    image_list = obj.normal_image_url_list[:4]
    for image in image_list:
        res = requests.get(image)
        res.raise_for_status()
        uploadable = BytesIO(res.content)
        media = client_v1.media_upload(file=uploadable)
        media_id = media.media_id
        media_ids.append(media_id)
    return media_ids


def scrape_exec_orders():
    """This function does blah blah."""
    t0, new, total = time.time(), 0, 0
    url = 'https://www.sos.ms.gov/content/executiveorders/EOFunctions.asmx/ListExecutiveOrders'
    r = requests.post(url, headers=muh_headers)
    annoying_blob = r.json()['d']
    rows = annoying_blob.replace('~~', '').split('^')
    for row in rows[:10]:
        cells = row.split('|')
        total = len(cells)
        this_dict = {}
        this_dict['order_number'] = cells[0].strip()
        m = airtab.match('order_number', this_dict['order_number'])
        if not m:
            new += 1
            # There's a new Exec Order!
            this_dict['order_url'] = f"https://www.sos.ms.gov/content/executiveorders/ExecutiveOrders/{cells[4]}"
            this_dict['url_description'] = cells[5]
            this_dict['date_of_order'] = cells[3]
            # upload to documnentcloud
            obj = dc.documents.upload(this_dict['order_url'])
            while obj.status != "success":
                time.sleep(5)
                obj = dc.documents.get(obj.id)
            obj.access = "public"
            obj.data = {'type': 'EO'}
            obj.title = 'Executive Order No. ' + this_dict['order_number']
            obj.source = 'MS SOS'
            obj.put()
            this_dict['dc_id'] = str(obj.id)
            this_dict['dc_title'] = obj.title
            this_dict['dc_access'] = obj.access
            this_dict['dc_pages'] = obj.pages
            this_dict['dc_url'] = obj.canonical_url
            status = (
                'The Sec. of State has added an executive order to its website.\n'
                f"On {this_dict['date_of_order']}, Gov. Reeves issued {this_dict['dc_title']}.\n"
                f"{this_dict['dc_url']}"
            )
            try:
                media_ids = get_images(obj.id)
            except requests.exceptions.HTTPError:
                media_ids = None
                print('error accessing and uploading the images of first 1-4 poages')
            client_v2.create_tweet(text=status, media_ids=media_ids)
            airtab.insert(this_dict, typecast=True)
    wrap_it_up(t0=t0, new=new, total=total, function='scrape_exec_orders')


def main():
    scrape_exec_orders()


if __name__ == '__main__':
    main()
