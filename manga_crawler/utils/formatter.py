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
    return int('0' + cleanStr(val))
# end def

def parseFloat(val):
    return float('0' + cleanStr(val))
# end def

def parseOrdinal(val):
    return parseInt(''.join(filter(str.isdigit, val)))
# end def

def cleanStr(val):
    return bleach.clean(str(val), tags=[], strip=True).strip()
# end def

def splitStr(val, sep):
    return [s.strip() for s in cleanStr(val).split(sep)]
# end def