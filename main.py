import logging
import os
import shutil
import sys
import zipfile
from typing import List
import urllib

from LlkMain import llk_main
from src.core.log_handler import LogHandler
from src.core.util import Utils
from src.google_drive.drive import Drive
from src.google_drive.file import File, MimeType

LOGS_FOLDER = os.path.join(Utils.get_project_root(), 'logs')
IMG_FOLDER = os.path.join(Utils.get_project_root(), 'img')
FLOOR_PLAN_IMAGES_FOLDER_ID = '1u1QpBbcumSra8StCwtaOZTdFDdtpXUU3'
RAW_IMAGES_FOLDER_ID = '1Of2lHAj2MO8laNdzE5qVM1oGlpfXRnoU'
PROCESSED_IMAGES_FOLDER_ID = '19BjKK-aPlt-R8NMYTNhSIQMZkVeg-Pni'
SAMPLE_IMAGE = '1FSMo0L0rZRcRSNbPUeYDLXMhoGSMyXkL'

logger: logging.Logger

START_ZIP_INDEX = 2
END_ZIP_INDEX = 2
START_FILE_INDEX = 2489


class DriveAccessor:
    @staticmethod
    def _exception_hook(exctype, exc, tb) -> None:
        logger.error("An unhandled exception occurred.", exc_info=(exctype, exc, tb))

    @staticmethod
    def init_logger() -> logging.Logger:
        sys.excepthook = DriveAccessor._exception_hook
        formatter = logging.Formatter(
            '%(levelname)s [%(asctime)s] [%(module)s.%(funcName)s] %(message)s')
        print(repr(Utils.get_project_root()))
        handler = LogHandler(formatter, os.path.join(LOGS_FOLDER, 'drive.log'))
        logging.basicConfig(**{'level': logging.INFO, 'handlers': [handler]})
        logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
        return logging.getLogger()

    @staticmethod
    def main():
        logger.info('==========================')
        logger.info('Program started')
        logger.info('==========================')
        llk_main()
        logger.info('Program done')


if __name__ == '__main__':
    logger = DriveAccessor.init_logger()
    DriveAccessor.main()


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
