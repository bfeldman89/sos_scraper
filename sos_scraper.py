# !/usr/bin/env python3
"""This module does blah blah."""
import os
import time
from io import BytesIO
import requests
from bs4 import BeautifulSoup
from ..jail_scrapers import airtab_sos as airtab, dc, tw, muh_headers, wrap_from_module


wrap_it_up = wrap_from_module('sos_scraper.py')


def scrape_exec_orders():
    """This function does blah blah."""
    url, t0, new, total = 'https://www.sos.ms.gov/Education-Publications/Pages/Executive-Orders.aspx', time.time(), 0, 0
    t0 = time.time()
    r = requests.get(url, headers=muh_headers)
    soup = BeautifulSoup(r.text, "html.parser").find('table', class_='table-striped')
    rows = soup.find_all("tr")
    for row in rows:
        cells = row.find_all("td")
        if len(cells) == 3:
            total += 1
            this_dict = {}
            if cells[0].string:
                this_dict["order_number"] = cells[0].string.strip()
                m = airtab.match("order_number", this_dict["order_number"])
                if not m:
                    new += 1
                    # There's a new Exec Order!
                    this_dict["order_url"] = f"https://www.sos.ms.gov{cells[1].a.get('href')}"
                    this_dict["url_description"] = cells[1].get_text(
                        "\n", strip=True)
                    if cells[2].string:
                        this_dict["date_of_order"] = cells[2].string.strip()
                    # upload to documnentcloud
                    fn = "Executive Order No. " + this_dict["order_number"]
                    obj = dc.documents.upload(
                        this_dict["order_url"], title=fn, source='MS SOS', access="public", data={'type': 'EO'})
                    obj = dc.documents.get(obj.id)
                    while obj.access != "public":
                        time.sleep(7)
                        obj = dc.documents.get(obj.id)
                    this_dict["dc_id"] = obj.id
                    this_dict["dc_title"] = obj.title
                    this_dict["dc_access"] = obj.access
                    this_dict["dc_pages"] = obj.pages
                    full_text = obj.full_text.decode("utf-8")
                    this_dict["dc_full_text"] = os.linesep.join(
                        [s for s in full_text.splitlines() if s])
                    airtab.insert(this_dict, typecast=True)
                    media_ids = []
                    image_list = obj.normal_image_url_list[:4]
                    for image in image_list:
                        res = requests.get(image)
                        res.raise_for_status()
                        uploadable = BytesIO(res.content)
                        response = tw.upload_media(media=uploadable)
                        media_ids.append(response["media_id"])
                    status = (
                        "The Sec. of State has added an executive order to its website.\n"
                        f"On {this_dict['date_of_order']}, Gov. Bryant issued {this_dict['dc_title']}.\n"
                        f"{this_dict['order_url']}"
                    )
                    tw.update_status(status=status, media_ids=media_ids)
    wrap_it_up(function='scrape_exec_orders', t0=t0, new=new, total=total)


def main():
    scrape_exec_orders()


if __name__ == "__main__":
    main()
