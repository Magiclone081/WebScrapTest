# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import urllib
from http.client import IncompleteRead

from bs4 import BeautifulSoup

from requests import get
from requests.exceptions import RequestException
from contextlib import closing

import time


def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/86.0.4240.75 Safari/537.36'}
        with closing(get(url, stream=True, headers=headers)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None

def simple_get_notsecured(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/86.0.4240.75 Safari/537.36'}
        with closing(get(url, stream=True, headers=headers, verify=False)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None

def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors.
    This function just prints them, but you can
    make it do anything.
    """
    print(e)


def get_url(html, constrain):
    url_scraped = []
    for a_area_url in html.find_all('a', href=True):
        temp = a_area_url['href']

        if 'javascript:common.redirect(' in temp:

            temp2 = temp.replace('javascript:common.redirect(', '').replace(');', '').replace('"', '').split(',')
            # print(temp2)
            if len(temp2) > 1 and temp2[2] == 'CD2_Detail_Nav':
                temp_area_url = 'http://hk.centadata.com/Floorplan.aspx?type=' + temp2[0] + '&code=' + temp2[
                    1] + '&ref=' + temp2[2]
                if temp_area_url not in constrain:
                    url_scraped.append(temp_area_url)
    return url_scraped


# download cent
def cent_main():
    raw_html = simple_get('http://hk.centadata.com/Floorplan.aspx?type=22&code=102&ref=CD2_Detail_Nav')
    html = BeautifulSoup(raw_html, 'html.parser')
    area_url = get_url(html, [])
    del area_url[-1]
    # print(area_url)
    fe = open('s00' + '0' + '.txt', 'w', encoding='utf8')
    for area_url_stuff in area_url:
        fe.write(area_url_stuff)
        fe.write('\n')
    fe.close()
    fea = open('s00' + '1' + '.txt', 'w', encoding='utf8')
    for scraping_url in area_url:
        raw_scraping_html = simple_get(scraping_url)
        scraping_html = BeautifulSoup(raw_scraping_html, 'html.parser')
        place_array = get_url(scraping_html, area_url)
        for place in place_array:
            fea.write(place)
            fea.write("\n")
    fea.close()
    feac = open('s00' + '1' + '.txt', 'r', encoding='utf8')
    feaca = feac.read().split('\n')
    del feaca[-1]
    area_count = 2
    f = open('s00' + '2' + '.txt', 'w', encoding='utf8')
    for place_array_item in feaca:
        pic_url_raw_html = simple_get(place_array_item)
        pic_url_html = BeautifulSoup(pic_url_raw_html, 'html.parser')

        # fe = open('s00' + '2' + '.txt', 'w', encoding='utf8')
        pic_url_html_array = repr(pic_url_html.getText).split(';')
        real_pic_url_html = ''
        for pic_url_html_array_item in pic_url_html_array:
            if 'config.imgUrl = [' in pic_url_html_array_item:
                real_pic_url_html = pic_url_html_array_item
        real_pic_url_html_array = real_pic_url_html.replace('\n', '').replace('\r', '').replace(" ", "").replace(
            'config.imgUrl=[', '').replace('\'', '').replace('{', '').replace('"', '').replace(
            'url:', '').replace('name:', '}').replace(']', '').replace(',', '').split('}')
        # for ca in real_pic_url_html_array:
        #    fe.write(ca)
        #    fe.write('\n')
        # fe.close()
        print(str(area_count))
        count = 0
        while count < len(real_pic_url_html_array) - 1:

            if '規劃圖' not in real_pic_url_html_array[count + 1] and '傳單' not in real_pic_url_html_array[count + 1] \
                    and '設施圖' not in real_pic_url_html_array[count + 1] and count % 2 == 0:
                f.write(real_pic_url_html_array[count])
                f.write('\n')
            count += 1
        print(str(count))
        area_count += 1
    f.close()
    url_file = open('s00' + '2' + '.txt', 'r', encoding='utf8')
    url_file_array = url_file.read().split('\n')
    del url_file_array[-1]
    imgcount = 0
    for url_file_array_item in url_file_array:
        image_response = get(url_file_array_item)
        imagef = open('cent_img' + str(imgcount) + '.png', "wb")
        imagef.write(image_response.content)
        imagef.close()
        print('cent_img' + str(imgcount) + '.png downloaded')
        imgcount += 1


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

    lkk_estate_raw_url = simple_get_notsecured(
        "https://www.ricacorp.com/ricadata/ptest.aspx?type=2&code=SSPPWPPYPS&info=fp&code2=&page=8")
    lkk_estate_url = BeautifulSoup(lkk_estate_raw_url, 'html.parser')
    lkk_estate_url_raw_array = repr(lkk_estate_url.getText).replace('</script>', '<script>').split('<script>')
    temp = []
    for lkk_estate_url_raw_array_item in lkk_estate_url_raw_array:
        if 'arrHK' in lkk_estate_url_raw_array_item and 'arrKL' in lkk_estate_url_raw_array_item:

            temp = lkk_estate_url_raw_array_item
    te = temp.replace(' ', '').replace('\n', '').replace('\'', '').replace(';', '').replace('\r', '').replace(' ', '')\
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
        lkk_estate_floorplan_code_raw_url = simple_get_notsecured(lkk_estate_url_array_fromtxt_item)
        lkk_estate_floorplan_code_url = BeautifulSoup(lkk_estate_floorplan_code_raw_url, 'html.parser')
        for contented in lkk_estate_floorplan_code_url.find_all('a'):
            content = repr(contented)
            if 'javascript:jsfreloadthis4' in content and 'fp' in content:

                temp2_array = content.replace('(', ')').split(')')
                temp3_array = temp2_array[1].replace('\'', '').split(',')
                lkk_estate_floorplan_getcode_raw_url = simple_get_notsecured(lkk_estate_url_array_fromtxt_item + '&info='
                                                                  + temp3_array[2] + '&code2=&page=0')
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
        lkk_retrieve_img_url_raw_html = simple_get_notsecured(lkk_retrieve_img_url_array_item)
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
        #print(lkk_retrieve_img_raw_url.headers['content-type'])
        different_type = ['gif', 'jpeg']
        if type in different_type:
            with open('lkk_img' + str(counter) + '.' + type, 'wb') as fw:
                fw.write(lkk_retrieve_img_raw_url.content)

            print('lkk_img' + str(counter) + '.' + type + ' downloaded')
        counter += 1







# jsfnumofpage

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    lkk_retrieve_img()
    # mid_download_img()
    # cent_main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
