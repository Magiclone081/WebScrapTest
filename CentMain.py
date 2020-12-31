import re
from enum import Enum


class CentData(Enum):
    CENTADATA_JS_STR = '^javascript:common.redirect\\(([0-9]+),"([0-9A-Za-z]+)","(CD2_Detail_Nav)","/Floorplan.aspx"\\);$'
    CENTADATA_JS_REGEX = re.compile(CENTADATA_JS_STR)
    CENTADATA_AREA_FILE = 's000.txt'
    CENTADATA_PLACE_FILE = 's001.txt'
    CENTADATA_PIC_FILE = 's002.txt'

CentData.CENTADATA_JS_REGEX