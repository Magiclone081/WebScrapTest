import time
from contextlib import closing
from http import HTTPStatus
from typing import Set

from os import path
from requests import get
from requests.exceptions import RequestException
from requests.models import Response

# from CentMain import get_urls_from_centa_link
from util import Utils

timer = 30


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


def special_get(url: str, secured=True, count=0) -> bytes or None:
    if count <= 10:
        try:
            headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                     'Chrome/86.0.4240.75 Safari/537.36'}
            return get(url, stream=True, headers=headers, verify=secured)
        except:
            Utils.print('Failed (try again)')
            count += 1
            time.sleep(timer)
            special_get(url, secured, count)
    else:
        Utils.print('Failed too many time')
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


def write_file(file_name: str, urls: Set[str]):
    with open(file_name, 'a+', encoding='utf8') as f:
        for i in urls:
            f.write(f'{i}\n')


def download_image(image_response, img_name: str):
    possible_type = ['gif', 'jpeg']
    type = image_response.headers['content-type'].split(';')[0].replace('image/', '')
    if type in possible_type:
        img_name = f'{img_name}.{type}'
        if path.exists(img_name):
            Utils.print(f'{img_name} downloaded previously')
        else:
            with open(img_name, "wb") as imagef:
                imagef.write(image_response.content)

            Utils.print(f'{img_name} downloaded')
    elif not is_good_response(image_response):
        Utils.print(f'{img_name} error')