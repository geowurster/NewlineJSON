#!/usr/bin/env python


"""
Profile NewlineJSON Reader/Writer against multiple JSON libraries
"""


import datetime
import gzip
import json
import os
import sys
import tempfile

try:
    import jsonlib2
except ImportError:
    jsonlib2 = None
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

import newlinejson


def main(infile):

    """
    Profile `newlinejson` against multiple JSON libraries.  If any of the
    following can be imported, they are profiled:

        - json
        - jsonlib2
        - simplejson
        - ujson
        - yajl

    By default a small-ish file from `sample-data` is used but the user can
    specify one with:

        $ ./utils/profile.py ${INFILE}
    """

    # Make sure the input file exists
    if not os.access(infile, os.R_OK):
        print("ERROR: Can't access infile: %s" % infile)
        return 1

    # Test against all found libraries
    for json_lib in (json, jsonlib2, simplejson, ujson, yajl):
        if json_lib is not None:
            newlinejson.JSON = json_lib

            # Update user
            start_time = datetime.datetime.now()
            print("")
            print("Profiling {libname} ...".format(libname=json_lib.__name__))
            print("  Start time: {stime}".format(stime=start_time.strftime('%H:%M:%S')))

            # Read and write all lines
            num_rows = 0
            with gzip.open(infile) if infile.endswith('gz') else open(infile) as i_f,\
                    tempfile.NamedTemporaryFile(mode='w') as o_f:
                reader = newlinejson.Reader(i_f)
                writer = newlinejson.Writer(o_f)
                for line in reader:
                    num_rows += 1
                    writer.write(line)

            # Update user
            end_time = datetime.datetime.now()
            print("  End time: {etime}".format(etime=end_time.strftime('%H:%M:%S')))
            print("  Elapsed secs: {sec}.{msec}".format(sec=(end_time - start_time).seconds, msec=(end_time - start_time).microseconds))
            print("  Num rows: {num_rows}".format(num_rows=num_rows))

    print("")
    return 0

if __name__ == '__main__':

    if len(sys.argv) > 2:
        print("ERROR: Too many arguments")
        sys.exit(1)
    elif len(sys.argv) is 1:
        infile = os.path.join('sample-data', '10k.json.gz')
    else:
        infile = sys.argv[1]
    sys.exit(main(infile))
