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

from core.util import Utils

CENTADATA_JS_STR = '^javascript:common.redirect\\(([0-9]+),"([0-9A-Za-z]+)","(CD2_Detail_Nav)","/Floorplan.aspx"\\);$'
CENTADATA_JS_REGEX = re.compile(CENTADATA_JS_STR)
CENTADATA_AREA_FILE = 's000.txt'
CENTADATA_PLACE_FILE = 's001.txt'
CENTADATA_PIC_FILE = 's002.txt'


def simple_get(url: str, secured=True) -> bytes or None:
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/86.0.4240.75 Safari/537.36'}
        with closing(get(url, stream=True, headers=headers, verify=secured)) as resp:
            return resp.content if is_good_response(resp) else None
    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp: Response) -> bool:
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == HTTPStatus.OK
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e: str):
    """
    It is always a good idea to log errors.
    This function just prints them, but you can
    make it do anything.
    """
    # logger.error(e)
    print(e)


def get_urls_from_js_link(html, exclude_urls: Set[str]) -> Set[str]:
    all_urls = [x['href'] for x in html.find_all('a', href=True)]
    matches: List[re.Match] or None = [CENTADATA_JS_REGEX.match(x) for x in all_urls]
    matches: List[re.Match] = [x for x in matches if x is not None]
    target_urls = [f'http://hk.centadata.com/Floorplan.aspx?type={x.group(1)}&code={x.group(2)}&ref={x.group(3)}'
                   for x in matches]
    return {x for x in target_urls if x not in exclude_urls}


def get_urls(url: str, exclude_urls: Set[str]) -> Set[str]:
    Utils.print(f'Processing url: {url}')
    raw_html = simple_get(url)
    if raw_html is None:
        return set()
    html = BeautifulSoup(raw_html, 'html.parser')
    return get_urls_from_js_link(html, exclude_urls)


def get_area_urls() -> Set[str]:
    if path.exists(CENTADATA_AREA_FILE):
        Utils.print(f'Getting area urls from file {CENTADATA_AREA_FILE}:')
        with open(CENTADATA_AREA_FILE, 'r', encoding='utf8') as f:
            return {x.replace('\n', '') for x in f.readlines() if x != ''}
    area_urls: Set[str] = get_urls('http://hk.centadata.com/Floorplan.aspx?type=22&code=102&ref=CD2_Detail_Nav', set())
    area_urls = {x for x in area_urls if x is not None}
    with open(CENTADATA_AREA_FILE, 'a+', encoding='utf8') as f:
        f.writelines(area_urls)
    return area_urls


def get_place_urls() -> Set[str]:
    if path.exists(CENTADATA_PLACE_FILE):
        with open(CENTADATA_PLACE_FILE, 'r', encoding='utf8') as f:
            return {x.replace('\n', '') for x in f.readlines() if x != ''}
    place_urls: Set[str] = set()
    area_urls = get_area_urls()
    for area_url in area_urls:
        place_urls |= get_urls(area_url, area_urls)  # Union of two sets
    with open(CENTADATA_PLACE_FILE, 'a+', encoding='utf8') as f:
        f.writelines(place_urls)
    return place_urls


def get_pic_urls() -> Set[str]:
    if path.exists(CENTADATA_PIC_FILE):
        with open(CENTADATA_PIC_FILE, 'r', encoding='utf8') as f:
            return {x.replace('\n', '') for x in f.readlines() if x != ''}
    pic_urls: Set[str] = set()
    place_urls = get_place_urls()
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
    with open(CENTADATA_PIC_FILE, 'a+', encoding='utf8') as f:
        f.writelines(pic_urls)
    return pic_urls


# download cent
def cent_main():
    pic_urls: Set[str] = get_pic_urls()
    img_count = 1
    for pic_url in pic_urls:
        Utils.print(f'Processing url ({img_count}/{len(pic_urls)}): {pic_url}')
        img_name = f'cent_img{img_count}.png'
        if path.exists(img_name):
            Utils.print(f'{img_name} downloaded previously')
        else:
            image_response = get(pic_url)
            with open(img_name, "wb") as imagef:
                imagef.write(image_response.content)
            Utils.print(f'{img_name} downloaded')
        img_count += 1


# first stage for midland
def mid_retrieve_img_url():
    # <915
    # might need to change the counter when bug and re run from the number from then on
    # if bugged at 350, re run at 350
    # counter = 1
    counter = 768

    while counter <= 915:
        print(str(counter))
        mid_url_file = open('mid' + str(counter).zfill(3) + '.txt', 'w', encoding='utf8')
        mid_estate_raw_url = simple_get("https://www.midland.com.hk/zh-hk/estate/E00" + str(counter).zfill(3))
        mid_estate_url = BeautifulSoup(mid_estate_raw_url, 'html.parser')
        mid_pic_url_html_raw_array = repr(mid_estate_url.getText).split('floorplans')

        mid_pic_url_html_raw = mid_pic_url_html_raw_array[-1].split(';')[0]

        mid_pic_url_html_raw_array = mid_pic_url_html_raw.replace('{', '').replace('[', '').replace('}', '') \
            .replace('\"', '').replace(']', '').split(',')
        mid_pic_url_html_real = []

        for mid_pic_url_html_raw_array_item in mid_pic_url_html_raw_array:

            if 'wan_doc_path:' in mid_pic_url_html_raw_array_item:
                mid_pic_url_html_raw_array_item = mid_pic_url_html_raw_array_item.replace('\\u0026', '&') \
                    .replace('%3A', ':').replace('%2F', '/').replace('wan_doc_path:', '')
                mid_pic_url_html_real.append(mid_pic_url_html_raw_array_item)
                mid_url_file.write(mid_pic_url_html_raw_array_item)
                mid_url_file.write('\n')
        counter += 1
        mid_url_file.close()


# second stage stage for midland
def mid_retrieve_img_url_concat():
    counter = 1

    while counter <= 915:
        mid_url_file = open('mid' + str(counter).zfill(3) + '.txt', 'r', encoding='utf8')
        mid_url_array = mid_url_file.read().split('\n')
        mid_url_file.close()
        print(str(counter))
        del mid_url_array[-1]
        mid_retrieve_img_url_concat_file = open('mid000' + '.txt', 'a', encoding='utf8')
        for mid_url_array_item in mid_url_array:
            mid_retrieve_img_url_concat_file.write(mid_url_array_item)
            mid_retrieve_img_url_concat_file.write('\n')
        counter += 1


# final stage for midland
def mid_download_img():
    mid_url_file = open('mid000' + '.txt', 'r', encoding='utf8')
    mid_url_array = mid_url_file.read().split('\n')
    mid_url_file.close()
    del mid_url_array[-1]
    img_count = 27868
    timer = 30
    while len(mid_url_array) > img_count:
        mid_url_array_item = mid_url_array[img_count]
        try:
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}
            image_response = get(mid_url_array_item, headers=headers)
        except ConnectionResetError:
            time.sleep(timer)
            try:
                headers = {
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}
                image_response = get(mid_url_array_item, headers=headers)
            except ConnectionError:
                time.sleep(timer)
                try:
                    headers = {
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}
                    image_response = get(mid_url_array_item, headers=headers)
                except ConnectionError:
                    time.sleep(timer)
                    headers = {
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}
                    image_response = get(mid_url_array_item, headers=headers)
        except ConnectionError:
            time.sleep(timer)
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}
            image_response = get(mid_url_array_item, headers=headers)
        except IncompleteRead:
            time.sleep(timer)
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}
            image_response = get(mid_url_array_item, headers=headers)
        except OSError:
            time.sleep(timer)
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}
            image_response = get(mid_url_array_item, headers=headers)
        mid_img = open('mid_img' + str(img_count) + '.jpg', "wb")
        mid_img.write(image_response.content)
        mid_img.close()
        print('mid_img' + str(img_count) + '.jpg downloaded')
        img_count += 1


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


def lkk_retrieve_img_url():
    lkk_estate_raw_url = simple_get(
        "https://www.ricacorp.com/ricadata/ptest.aspx?type=2&code=SSPPWPPYPS&info=fp&code2=&page=8", secured=False)
    lkk_estate_url = BeautifulSoup(lkk_estate_raw_url, 'html.parser')
    lkk_estate_url_raw_array = repr(lkk_estate_url.getText).replace('</script>', '<script>').split('<script>')
    temp = []
    for lkk_estate_url_raw_array_item in lkk_estate_url_raw_array:
        if 'arrHK' in lkk_estate_url_raw_array_item and 'arrKL' in lkk_estate_url_raw_array_item:
            temp = lkk_estate_url_raw_array_item
    te = temp.replace(' ', '').replace('\n', '').replace('\'', '').replace(';', '').replace('\r', '').replace(' ', '') \
        .replace(')', ',').split(',')
    for temp_item in te:

        if 'ptest.aspx?' in temp_item:
            with open('lkk000.txt', 'a', encoding='utf8') as f:
                f.write("https://www.ricacorp.com/ricadata/" + temp_item)
                f.write('\n')

    with open('lkk000.txt', 'r', encoding='utf8') as fr:
        lkk_estate_url_array_fromtxt = fr.read().split('\n')

    del lkk_estate_url_array_fromtxt[-1]

    for lkk_estate_url_array_fromtxt_item in lkk_estate_url_array_fromtxt:
        lkk_estate_floorplan_code_raw_url = simple_get(lkk_estate_url_array_fromtxt_item, secured=False)
        lkk_estate_floorplan_code_url = BeautifulSoup(lkk_estate_floorplan_code_raw_url, 'html.parser')
        for contented in lkk_estate_floorplan_code_url.find_all('a'):
            content = repr(contented)
            if 'javascript:jsfreloadthis4' in content and 'fp' in content:

                temp2_array = content.replace('(', ')').split(')')
                temp3_array = temp2_array[1].replace('\'', '').split(',')
                lkk_estate_floorplan_getcode_raw_url = simple_get(
                    lkk_estate_url_array_fromtxt_item + '&info=' + temp3_array[2] + '&code2=&page=0', secured=False)
                lkk_estate_floorplan_getcode_url = BeautifulSoup(lkk_estate_floorplan_getcode_raw_url, 'html.parser')

                lkk_estate_floorplan_getcode_url_raw_array = repr(lkk_estate_floorplan_getcode_url.getText) \
                    .replace('</script>', '<script>').split('<script>')
                maxcode = 0
                for lkk_estate_floorplan_getcode_url_raw_array_item in lkk_estate_floorplan_getcode_url_raw_array:
                    if 'jsfnumofpage' in lkk_estate_floorplan_getcode_url_raw_array_item:
                        temp4_array = lkk_estate_floorplan_getcode_url_raw_array_item.split(';')
                        for item in temp4_array:
                            if 'jsfnumofpage' in item and '=' in item:
                                maxcode = item.replace('jsfnumofpage', '').replace(' ', '').replace('var', '') \
                                    .replace('=', '')

                counter = 0
                with open('lkk001.txt', 'a', encoding='utf8') as fr:
                    print('file opened')
                    while counter < int(maxcode):
                        fr.write(lkk_estate_url_array_fromtxt_item + '&info=' + temp3_array[2] + '&code2=&page='
                                 + str(counter))
                        fr.write('\n')
                        counter += 1


def lkk_retrieve_img_actual_url():
    with open('lkk001.txt', 'r', encoding='utf8') as fr:
        lkk_retrieve_img_url_array = fr.read().split('\n')

    del lkk_retrieve_img_url_array[-1]

    for lkk_retrieve_img_url_array_item in lkk_retrieve_img_url_array:
        lkk_retrieve_img_url_raw_html = simple_get(lkk_retrieve_img_url_array_item, secured=False)
        lkk_retrieve_img_url_html = BeautifulSoup(lkk_retrieve_img_url_raw_html, 'html.parser')
        for contented in lkk_retrieve_img_url_html.find_all('a'):
            content = repr(contented)
            if 'javascript:jsfwindowopen' in content and 'fpurl=' in content:

                temp = content.replace('fpurl=', '\');').split('\');')

                for temp_item in temp:
                    if 'http' in temp_item and 'img' in temp_item:
                        with open('lkk002.txt', 'a', encoding='utf8') as f:
                            f.write(temp_item.replace('amp;', ''))
                            f.write('\n')


def lkk_retrieve_img():
    with open('lkk002.txt', 'r', encoding='utf8') as fr:
        lkk_retrieve_img_url_array = fr.read().split('\n')

    del lkk_retrieve_img_url_array[-1]
    counter = 0
    for lkk_retrieve_img_url_array_item in lkk_retrieve_img_url_array:
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}
        lkk_retrieve_img_raw_url = get(lkk_retrieve_img_url_array_item, headers=headers)
        # lkk_retrieve_img_raw_url = simple_get_notsecured(lkk_retrieve_img_url_array_item)
        type = lkk_retrieve_img_raw_url.headers['content-type'].split(';')[0].replace('image/', '')
        # print(lkk_retrieve_img_raw_url.headers['content-type'])
        different_type = ['gif', 'jpeg']
        if type in different_type:
            with open('lkk_img' + str(counter) + '.' + type, 'wb') as fw:
                fw.write(lkk_retrieve_img_raw_url.content)

            print('lkk_img' + str(counter) + '.' + type + ' downloaded')
        counter += 1


# jsfnumofpage

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # lkk_retrieve_img()
    # mid_download_img()
    cent_main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
