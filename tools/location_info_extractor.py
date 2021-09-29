import json
import os

import requests
from lxml import etree

os.chdir('../')
from utils.const import *


def main():
    loc_id_dict = {}
    loc_id_addr_dict = {}

    loc_name_dict = {}
    loc_addr_dict = {}
    for code in SERVICE_ID.values():
        service_time_url = MVC_URL + code
        response = requests.get(service_time_url)
        dom = etree.HTML(response.text)
        js_content = str(dom.xpath('/html/body/script[22]/text()')[0])
        loc_data_raw = js_content.split('\r\n')[1][27:-1]
        loc_data = json.loads(loc_data_raw)

        loc_name_sub_dict = {}
        loc_addr_sub_dict = {}
        for item in loc_data:
            id = str(item['LocAppointments'][0]['LocationId'])
            loc_id_dict[id] = item['Name'].split('-')[0][:-1]
            loc_name_sub_dict[id] = item['Name'].split('-')[0][:-1]

            address = item['Street1'] + ', '
            if item['Street2'] is not None:
                address = address + item['Street2'] + ', '
            address = address + item['City'] + ', ' + item['State'] + ', ' + item['Zip']

            loc_id_addr_dict[id] = address
            loc_addr_sub_dict[id] = address

        loc_name_dict[code] = loc_name_sub_dict
        loc_addr_dict[code] = loc_addr_sub_dict

    loc_id_dict['0'] = 'All'
    print(loc_id_dict)
    print(loc_name_dict)
    print(loc_id_addr_dict)
    print(loc_addr_dict)


if __name__ == '__main__':
    main()
