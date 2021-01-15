import json
import re
from enum import Enum
from os import path
from typing import List, Set

from bs4 import BeautifulSoup
from requests import get

from functions import simple_get, write_file, special_get, download_image

from util import Utils


class CentaData(Enum):
    JS_STR = '^javascript:common.redirect\\(([0-9]+),"([0-9A-Za-z]+)","(CD2_Detail_Nav)","/Floorplan.aspx"\\);$'
    JS_REGEX = re.compile(JS_STR)
    AREA_FILE = 'CentArea.txt'
    PLACE_FILE = 'CentPlace.txt'
    PIC_FILE = 'CentPic.txt'


def get_urls_from_centa_link(html, exclude_urls: Set[str]) -> Set[str]:
    all_urls = [x['href'] for x in html.find_all('a', href=True)]
    matches: List[re.Match] or None = [CentaData.CENTADATA_JS_REGEX.value.match(x) for x in all_urls]
    matches: List[re.Match] = [x for x in matches if x is not None]
    target_urls = [f'http://hk.centadata.com/Floorplan.aspx?type={x.group(1)}&code={x.group(2)}&ref={x.group(3)}'
                   for x in matches]
    return {x for x in target_urls if x not in exclude_urls}


def cent_main():
    pic_urls: Set[str] = _get_pic_urls()
    img_count = 1
    for pic_url in pic_urls:
        Utils.print(f'Processing url ({img_count}/{len(pic_urls)}): {pic_url}')
        image_response = special_get(pic_url)

        img_name = f'mid_img{img_count}'
        download_image(image_response, img_name)
        img_count += 1


def _get_urls(url: str, exclude_urls: Set[str]) -> Set[str]:
    Utils.print(f'Processing url: {url}')
    raw_html = simple_get(url)
    if raw_html is None:
        return set()
    html = BeautifulSoup(raw_html, 'html.parser')

    return get_urls_from_centa_link(html, exclude_urls)


def _get_area_urls() -> Set[str]:
    if path.exists(CentaData.AREA_FILE.value):
        Utils.print(f'Getting area urls from file {CentaData.AREA_FILE.value}:')
        with open(CentaData.AREA_FILE.value, 'r', encoding='utf8') as f:
            return {x.replace('\n', '') for x in f.readlines() if x != ''}

    area_urls: Set[str] = _get_urls('http://hk.centadata.com/Floorplan.aspx?type=22&code=102&ref=CD2_Detail_Nav',set())
    area_urls = {x for x in area_urls if x is not None}
    write_file(area_urls)
    return area_urls


def _get_place_urls() -> Set[str]:
    if path.exists(CentaData.PLACE_FILE.value):
        Utils.print(f'Getting area urls from file {CentaData.PLACE_FILE.value}:')
        with open(CentaData.PLACE_FILE.value, 'r', encoding='utf8') as f:
            return {x.replace('\n', '') for x in f.readlines() if x != ''}
    place_urls: Set[str] = set()
    area_urls = _get_area_urls()

    for area_url in area_urls:
        place_urls |= _get_urls(area_url, area_urls)  # Union of two sets
    write_file(place_urls)
    return place_urls


def _get_pic_urls() -> Set[str]:
    if path.exists(CentaData.PIC_FILE.value):
        Utils.print(f'Getting area urls from file {CentaData.PIC_FILE.value}:')
        with open(CentaData.PIC_FILE.value, 'r', encoding='utf8') as f:
            return {x.replace('\n', '') for x in f.readlines() if x != ''}

    pic_urls: Set[str] = set()
    place_urls = _get_place_urls()

    counter = 1
    for place_url in place_urls:
        Utils.print(f'Processing url ({counter}/{len(place_urls)}): {place_url}')
        raw_html = simple_get(place_url)
        html = BeautifulSoup(raw_html, 'html.parser')
        pic_html = repr(html.getText).split(';')
        pic_html_img_urls = [x.replace('config.imgUrl = ', '') for x in pic_html if 'config.imgUrl = [' in x]
        for pic_html_img_url in pic_html_img_urls:
            pic_json = json.loads(pic_html_img_url.replace("config.imgUrl = ", ""))
            pic_urls |= [x['url'] for x in pic_json
                         if '規劃' not in x['name'] and '傳單' not in x['name'] and '設施圖' not in x['name']]
        counter += 1
    write_file(pic_urls)
    return pic_urls
