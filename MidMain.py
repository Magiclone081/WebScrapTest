import json
import re
from collections import Set
from enum import Enum
from os import path

from bs4 import BeautifulSoup
from typing import List
from functions import special_get, write_file, download_image

# picurl = []
# for i in a['props']['pageProps']['result']['estateData']['floorplans']:
#     picurl.append(i.__getitem__('wan_doc_path'))
#
# print(picurl)
from core.util import Utils


class MidData(Enum):
    PLACE_STR = '.*?<scriptid="__NEXT_DATA__"type="application/json">(.*?)</script>.*?'
    PLACE_URL_REGEX = re.compile(PLACE_STR)
    PIC_FILE = path.join(Utils.get_project_root(), 'mid_pic_file.txt')


def _get_urls() -> set[str]:
    if path.exists(MidData.PIC_FILE.value):
        Utils.print(f'Getting area urls from file {MidData.PIC_FILE.value}:')
        with open(MidData.PIC_FILE.value, 'r', encoding='utf8') as f:
            return {x.replace('\n', '') for x in f.readlines() if x != ''}
    urls = set()
    counter = 1
    max_count = 915
    # max_count = 2
    while counter <= max_count:
        Utils.print(f'Getting url : ({counter}/{max_count})')
        raw_mid_estate_url = special_get("https://www.midland.com.hk/zh-hk/estate/E00" + str(counter).zfill(3)).content
        mid_estate_url = BeautifulSoup(raw_mid_estate_url, 'html.parser')
        mid_estate_text = repr(mid_estate_url)

        mid_estate_text = mid_estate_text.replace(' ', '').replace('\n', '').replace('\r', '')

        matches: List[re.Match] or None = MidData.PLACE_URL_REGEX.value.match(mid_estate_text)

        # matches: List[re.Match] = [x for x in matches if x is not None]
        if matches is not None:
            target_storage = matches.group(1)

            # target_storage = repr(target_storage)

            target_json_unwrap = json.loads(target_storage)

            try:
                for i in target_json_unwrap['props']['pageProps']['result']['estateData']['floorplans']:
                    if 'wan_doc_path' in i:

                        urls.add(i['wan_doc_path'].replace('\\u0026', '&').replace('%3A', ':').replace('%2F', '/'))
            except:
                Utils.print(f'url {counter} does not exist')
        counter += 1
    print(urls)
    write_file(MidData.PIC_FILE.value, urls)
    return urls




def mid_main():
    pic_urls: Set[str] = _get_urls()
    img_count = 1

    for pic_url in pic_urls:
        Utils.print(f'Processing url ({img_count}/{len(pic_urls)}): {pic_url}')
        image_response = special_get(pic_url)

        img_name = f'mid_img{img_count}'
        download_image(image_response, img_name)
        img_count += 1
