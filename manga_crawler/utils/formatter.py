# -*- conding: utf-8 -*-
import json
import bleach
import dateparser
from urllib.parse import parse_qsl

def parseJson(val):
    """Parse JSON string and returns a python dictionary"""
    return json.loads(val)
# end def

def parseQuery(val):
    """Parse query from encoded byte data and returns fields"""
    return dict(parse_qsl(val.decode("utf-8")))
# end def

def parseInt(val):
    """Parse integer from given string"""
    return int('0' + str(val))
# end def

def parseFloat(val):
    """Parse float from given string"""
    return float('0' + str(val))
# end def

def parseOrdinal(val):
    """Parse the ordinal number and return an integer"""
    return parseInt(''.join(filter(str.isdigit, str(val))))
# end def

def parseDate(val):
    """Parse any date and returns a datetime object"""
    return dateparser.parse(val)
# end def

def cleanStr(val):
    """Clear string of any illegal objecets"""
    return bleach.clean(str(val), tags=[], strip=True).replace('\x00', '').strip()
# end def

def splitStr(val, sep):
    """Split strings by given separator and returns an array"""
    return [s.strip() for s in str(val).split(sep)]
# end def
