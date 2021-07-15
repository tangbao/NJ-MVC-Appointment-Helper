import json
import os

import requests
from lxml import etree

os.chdir('../')
from const import *


def main():
    loc_dict = {}
    for code in SERVICE_ID.values():
        service_time_url = MVC_URL + code
        response = requests.get(service_time_url)
        dom = etree.HTML(response.text)
        js_content = str(dom.xpath('/html/body/script[22]/text()')[0])
        loc_data_raw = js_content.split('\r\n')[1][27:-1]
        loc_data = json.loads(loc_data_raw)

        for item in loc_data:
            loc_dict[str(item['LocAppointments'][0]['LocationId'])] = item['Name'].split('-')[0][:-1]

    print(loc_dict)


if __name__ == '__main__':
    main()
