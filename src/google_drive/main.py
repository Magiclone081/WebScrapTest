import logging
import os
import sys
from typing import List

from src.core.log_handler import LogHandler
from src.core.util import Utils
from src.google_drive.drive import Drive
from src.google_drive.file import File

LOGS_FOLDER = os.path.join(Utils.get_project_root(), 'logs')
IMG_FOLDER = os.path.join(Utils.get_project_root(), 'img')
RAW_IMAGES_FOLDER_ID = '1Of2lHAj2MO8laNdzE5qVM1oGlpfXRnoU'
PROCESSED_IMAGES_FOLDER_ID = '19BjKK-aPlt-R8NMYTNhSIQMZkVeg-Pni'
SAMPLE_IMAGE = '1FSMo0L0rZRcRSNbPUeYDLXMhoGSMyXkL'

logger: logging.Logger


class DriveAccessor:
    @staticmethod
    def _exception_hook(exctype, exc, tb) -> None:
        logger.error("An unhandled exception occurred.", exc_info=(exctype, exc, tb))

    @staticmethod
    def init_logger() -> logging.Logger:
        sys.excepthook = DriveAccessor._exception_hook
        formatter = logging.Formatter(
            '%(levelname)s [%(asctime)s] [%(module)s.%(funcName)s] %(message)s')
        handler = LogHandler(formatter, os.path.join(LOGS_FOLDER, 'drive.log'))
        logging.basicConfig(**{'level': logging.INFO, 'handlers': [handler]})
        logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
        return logging.getLogger()

    @staticmethod
    def main():
        logger.info('==========================')
        logger.info('Program started')
        logger.info('==========================')
        files: List[File] = Drive.list(RAW_IMAGES_FOLDER_ID, max_count=10)  # sys.maxsize for everything
        for i in range(min(len(files), 10)):
            logger.info(f'File {i + 1}/{len(files)}: {files[i]}')
        if len(files) > 10:
            logger.info('...')
        Drive.download(SAMPLE_IMAGE, IMG_FOLDER, False)
        Drive.upload(PROCESSED_IMAGES_FOLDER_ID, os.path.join(IMG_FOLDER, 'test.png'))
        logger.info('Program done')


if __name__ == '__main__':
    logger = DriveAccessor.init_logger()
    DriveAccessor.main()
