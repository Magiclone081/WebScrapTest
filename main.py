# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from bs4 import BeautifulSoup

from requests import get
from requests.exceptions import RequestException
from contextlib import closing


def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
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
        imagef = open('img' + str(imgcount) + '.png', "wb")
        imagef.write(image_response.content)
        imagef.close()
        print('img' + str(imgcount) + '.png downloaded')
        imgcount += 1






# and a_area_url.parent in parents_area


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    cent_main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
