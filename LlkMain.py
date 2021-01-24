import json
import re
from collections import Set
from enum import Enum
import os

from bs4 import BeautifulSoup
from typing import List

from core.util import Utils
from functions import special_get, write_file, download_image



class LlkData(Enum):
    ARRAY_URL_STR = '.*?Array\\((.*?)\\);.*?'
    ARRAY_URL_REGEX = re.compile(ARRAY_URL_STR)
    GET_PLACE_URL_STR = '.*?\'(ptest.aspx\?.*?)\'.*?'
    GET_PLACE_URL_REGEX = re.compile(GET_PLACE_URL_STR)
    GET_PIC_PAGE_URL_STR = '^javascript:jsfreloadthis4\\([0-9]+,\'([0-9A-Za-z]+)\',\'fp\',[0-9]+\\);$'
    GET_PIC_PAGE_URL_REGEX = re.compile(GET_PIC_PAGE_URL_STR)
    GET_MAX_PAGE_NUM_STR = '.*jsfnumofpage=([0-9]+).*'
    GET_MAX_PAGE_NUM_REGEX = re.compile(GET_MAX_PAGE_NUM_STR)
    GET_PIC_URL_STR = '^javascript:jsfwindowopen\\(.*?fpurl=(.*?)\'\\);$'
    GET_PIC_URL_REGEX = re.compile(GET_PIC_URL_STR)
    PLACE_FILE = os.path.join(Utils.get_project_root(), 'llk_place_file.txt')
    PIC_PAGE_FILE = os.path.join(Utils.get_project_root(), 'llk_pic_page_file.txt')
    PIC_FILE = os.path.join(Utils.get_project_root(), 'llk_pic_file.txt')


def llk_main():
    pic_urls: Set[str] = _get_pic_urls()
    img_count = 1
    for pic_url in pic_urls:
        Utils.print(f'Processing url ({img_count}/{len(pic_urls)}): {pic_url}')
        image_response = special_get(pic_url)

        img_name = f'llk_img{img_count}'
        download_image(image_response, img_name)
        img_count += 1
        break



def _get_pic_urls():
    if os.path.exists(LlkData.PIC_FILE.value):
        Utils.print(f'Getting area urls from file {LlkData.PIC_FILE.value}:')
        with open(LlkData.PIC_FILE.value, 'r', encoding='utf8') as f:
            return {x.replace('\n', '') for x in f.readlines() if x != ''}
    pic_page_urls = _get_pic_page_urls()
    pic_urls = set()
    count = 1
    for pic_page_url_item in pic_page_urls:
        Utils.print(f'Getting pic urls ({count}/{len(pic_page_urls)})')
        raw_pic_page_html = special_get(pic_page_url_item, secured=False).content
        pic_page_html = BeautifulSoup(raw_pic_page_html, 'html.parser')
        all_urls = [x['href'] for x in pic_page_html.find_all('a', href=True)]
        matches: List[re.Match] or None = [LlkData.GET_PIC_URL_REGEX.value.match(x) for x in all_urls]
        matches: List[re.Match] = [x for x in matches if x is not None]
        target_urls: set[str] = set(x.group(1) for x in matches)
        pic_urls |= target_urls
        count += 1



    write_file(LlkData.PIC_FILE.value, pic_urls)



def _get_pic_page_urls():
    if os.path.exists(LlkData.PIC_PAGE_FILE.value):
        Utils.print(f'Getting area urls from file {LlkData.PIC_PAGE_FILE.value}:')
        with open(LlkData.PIC_PAGE_FILE.value, 'r', encoding='utf8') as f:
            return {x.replace('\n', '') for x in f.readlines() if x != ''}
    pic_page_urls: Set[str] = set()
    place_urls = _get_place_urls()
    count = 1
    for place_url_item in place_urls:
        Utils.print(f'Getting pic page urls ({count}/{len(place_urls)})')
        raw_place_html = special_get(f'{place_url_item}&info=fp&code2=&page=0', secured=False).content
        place_html = BeautifulSoup(raw_place_html, 'html.parser')
        # all_urls = [x['href'] for x in html.find_all('a', href=True)]

        # matches: List[re.Match] or None = [LlkData.GET_PIC_PAGE_URL_REGEX.value.match(x) for x in all_urls]
        #
        # matches: List[re.Match] = [x for x in matches if x is not None]
        # pic_page_urls_first_page = set(f'{place_url_item}&info=fp&code2=&page=0' for x in matches)
        temp = set()
        # for pic_page_urls_first_page_item in pic_page_urls_first_page:
        #     Utils.print(f'Getting pic page urls ({count}/{len(place_urls)}) Get Max Page')
        #     pic_page_urls_first_page_raw_html = special_get(pic_page_urls_first_page_item, secured=False).content
        #     # pic_page_urls_first_page_raw_html= special_get('https://www.ricacorp.com/ricadata/ptest.aspx?type=2&code=EEPEWPSXPW&info=fp&code2=&page=2', secured=False).content
        #     pic_page_urls_first_page_html = BeautifulSoup(pic_page_urls_first_page_raw_html, 'html.parser')

        match: re.Match or None = LlkData.GET_MAX_PAGE_NUM_REGEX.value.match(repr(place_html).replace('\n', ''))

        max_page_num = int(match.group(1)) if match is not None else 0

        counter2 = 1
        while counter2 <= max_page_num:
            Utils.print(f'Getting pic page urls ({count}/{len(place_urls)}) ({counter2}/{max_page_num})')
            temp.add(f'{place_url_item}&info=fp&code2=&page={counter2}')

            counter2 += 1

        # pic_page_urls |= pic_page_urls_first_page
        pic_page_urls |= temp
        count += 1



    write_file(LlkData.PIC_PAGE_FILE.value, pic_page_urls)




def _get_place_urls() -> set[str]:
    if os.path.exists(LlkData.PLACE_FILE.value):
        Utils.print(f'Getting area urls from file {LlkData.PLACE_FILE.value}:')
        with open(LlkData.PLACE_FILE.value, 'r', encoding='utf8') as f:
            return {x.replace('\n', '') for x in f.readlines() if x != ''}
    lkk_estate_raw_url = special_get(
        "https://www.ricacorp.com/ricadata/ptest.aspx?type=2&code=SSPPWPPYPS&info=fp&code2=&page=8",
        secured=False).content
    lkk_estate_url = BeautifulSoup(lkk_estate_raw_url, 'html.parser')
    lkk_estate_url_raw_array = repr(lkk_estate_url.getText).replace('</script>', '<script>').split('<script>')
    temp = ''
    for lkk_estate_url_raw_array_item in lkk_estate_url_raw_array:
        if 'arrHK' in lkk_estate_url_raw_array_item and 'arrKL' in lkk_estate_url_raw_array_item:
            temp = lkk_estate_url_raw_array_item.replace('\n', '').replace(' ', '').replace('\t', '')
    matches: [str] or None = LlkData.ARRAY_URL_REGEX.value.findall(temp)

    if matches is not None:

        string = ','.join(matches)

        url_list = set()
        temps = LlkData.GET_PLACE_URL_REGEX.value.findall(string)
        if temps is not None:
            for i in temps:
                url_list.add(f'https://www.ricacorp.com/ricadata/{i}')
        write_file(LlkData.PLACE_FILE.value, url_list)
        return url_list
