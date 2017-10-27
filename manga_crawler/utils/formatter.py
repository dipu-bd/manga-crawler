# -*- conding: utf-8 -*-
import json
import bleach
from urllib.parse import parse_qsl

def parseJson(val):
    return json.loads(val)
# end def

def parseQuery(val):
    return dict(parse_qsl(val.decode("utf-8")))
# end def

def parseInt(val):
    return int('0' + str(val))
# end def

def parseFloat(val):
    return float('0' + str(val))
# end def

def parseOrdinal(val):
    return parseInt(''.join(filter(str.isdigit, str(val))))
# end def

def cleanStr(val):
    return bleach.clean(str(val), tags=[], strip=True).replace('\x00', '').strip()
# end def

def splitStr(val, sep):
    return [s.strip() for s in str(val).split(sep)]
# end def
