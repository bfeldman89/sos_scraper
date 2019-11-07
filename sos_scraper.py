# !/usr/bin/env python3
"""This module does blah blah."""
import os
import time
from io import BytesIO
import requests
from airtable import Airtable
from bs4 import BeautifulSoup
from documentcloud import DocumentCloud
from tabulate import tabulate
from twython import Twython


def scrape_exec_orders(quiet=True):
    """This function does blah blah."""
    t0 = time.time()
    dc = DocumentCloud(
        os.environ['DOCUMENT_CLOUD_USERNAME'], os.environ['DOCUMENT_CLOUD_PW'])
    tw = Twython(
        os.environ['TWITTER_APP_KEY'],
        os.environ['TWITTER_APP_SECRET'],
        os.environ['TWITTER_OAUTH_TOKEN'],
        os.environ['TWITTER_OAUTH_TOKEN_SECRET'],
    )
    airtab = Airtable(os.environ['other_scrapers_db'],
                      "exec orders", os.environ['AIRTABLE_API_KEY'])
    url = "https://www.sos.ms.gov/Education-Publications/Pages/Executive-Orders.aspx"
    muh_headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36"}
    r = requests.get(url, headers=muh_headers)
    soup = BeautifulSoup(r.text, "html.parser").find('table', class_='table-striped')
    rows = soup.find_all("tr")
    new_rows, total_rows = 0, 0
    for row in rows:
        cells = row.find_all("td")
        if len(cells) == 3:
            total_rows += 1
            this_dict = {}
            if cells[0].string:
                this_dict["order_number"] = cells[0].string.strip()
                m = airtab.match("order_number", this_dict["order_number"])
                if not m:
                    new_rows += 1
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
                    try:
                        full_text = obj.full_text.decode("utf-8")
                        this_dict["dc_full_text"] = os.linesep.join([s for s in full_text.splitlines() if s])
                    except:
                        pass
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
    table = [['scraper', 'seconds', 'new', 'total']]
    table.append(['sos scraper', round(time.time() - t0, 2), new_rows, total_rows])
    if not quiet:
        print(tabulate(table, headers="firstrow", tablefmt="fancy_grid"))


def main():
    scrape_exec_orders(quiet=False)


if __name__ == "__main__":
    main()
