from datetime import datetime


class Utils:
    @staticmethod
    def print(s: str, d: datetime = None) -> None:
        d = datetime.now() if d is None else d
        print(f'[{d.strftime("%Y-%m-%d %H:%M:%S.%f")}] {s}')
