import os
from datetime import datetime


class Utils:
    @staticmethod
    def print(s: str, d: datetime = None) -> None:
        d = datetime.now() if d is None else d
        print(f'[{d.strftime("%Y-%m-%d %H:%M:%S.%f")}] {s}')

    @staticmethod
    def get_project_root(name: str = 'WebScrapTest', path: str = None) -> str:
        if path is None:
            path = os.getcwd()
        while os.path.basename(path) not in [name, '']:
            path = os.path.dirname(path)
        return path
