import os

os.chdir('../')
from utils.const import *


if __name__ == '__main__':
    for item in LOCATION_NAME.items():
        url = MVC_URL + item[0] + '/'
        print('## [' + [k for k, v in SERVICE_ID.items() if v == item[0]][0] + '](' + url + ')')
        print('| Name | Id | Address |')
        print('| :---: | :---: | :---: |')
        for subitem in item[1].items():
            md_line = '|[' + subitem[1] + '](' + url + subitem[0] + ')|' +\
                      subitem[0] + '|' + LOCATION_ADDR[item[0]][subitem[0]] + '|'
            print(md_line)
        print('\n')