# This is a sample Python script.
import json
import time
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import urllib
import re
from contextlib import closing
from http import HTTPStatus
from http.client import IncompleteRead
from os import path
from typing import List, Set

from bs4 import BeautifulSoup
from requests import get
from requests.exceptions import RequestException
from requests.models import Response

from LlkMain import llk_main
from MidMain import mid_main
from util import Utils


# and a_area_url.parent in parents_area

# first stage for hkp
def hkp_retrieve_img_url():
    # <915
    # might need to change the counter when bug and re run from the number from then on
    # if bugged at 350, re run at 350
    # counter = 1
    counter = 1

    while counter <= 1:
        print(str(counter))
        hkp_url_file = open('hkp' + str(counter).zfill(3) + '.txt', 'w', encoding='utf8')
        req = urllib.request.Request("https://www.hkp.com.hk/zh-hk/estate/E00" + str(counter).zfill(3),
                                     headers={'User-Agent': 'Mozilla/5.0'})
        print("https://www.hkp.com.hk/zh-hk/estate/E00" + str(counter).zfill(3))

        html = urllib.request.urlopen(req).read

        print(repr(html))
        """
        hkp_estate_url = BeautifulSoup(hkp_estate_raw_url, 'html.parser')
        hkp_pic_url_html_raw_array = repr(hkp_estate_url.getText).split('floorplans')

        hkp_pic_url_html_raw = hkp_pic_url_html_raw_array[-1].split(';')[0]

        hkp_pic_url_html_raw_array = hkp_pic_url_html_raw.replace('{', '').replace('[', '').replace('}', '') \
            .replace('\"', '').replace(']', '').split(',')
        hkp_pic_url_html_real = []

        for hkp_pic_url_html_raw_array_item in hkp_pic_url_html_raw_array:

            if 'wan_doc_path:' in hkp_pic_url_html_raw_array_item:
                hkp_pic_url_html_raw_array_item = hkp_pic_url_html_raw_array_item.replace('\\u0026', '&') \
                    .replace('%3A', ':').replace('%2F', '/').replace('wan_doc_path:', '')
                hkp_pic_url_html_real.append(hkp_pic_url_html_raw_array_item)
                hkp_url_file.write(hkp_pic_url_html_raw_array_item)
                hkp_url_file.write('\n')
        
        hkp_url_file.close()
        """
        counter += 1



# jsfnumofpage

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # cent_main()
    # mid_main()
    llk_main()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
