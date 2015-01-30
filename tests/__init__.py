"""
Unittests for newlinejson
"""

import json
try:
    from io import StringIO
except ImportError:
    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO

try:
    import simplejson
except ImportError:
    simplejson = None
try:
    import ujson
except ImportError:
    ujson = None
try:
    import yajl
except ImportError:
    yajl = None

from . import *


JSON_LIBRARIES = [lib for lib in (json, ujson, simplejson, yajl) if lib is not None]
