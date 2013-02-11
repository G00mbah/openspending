#!/usr/bin/env python
# encoding: utf-8
"""
converter.py

Created by Breyten Ernsting on 2013-02-11.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
"""

import sys
import getopt
import logging

help_message = '''
Converts amsterdam excel file with expenditure data
'''

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Runner(object):
    def __init__(self, spending_file):
        logger.debug('Initializing ...')
        self.spending_file = spending_file

    def run(self):
        logger.info('Running ...')


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "hi:", ["help", "input="])
        except getopt.error, msg:
            raise Usage(msg)

        verbose = False
        spendings_file = None
        # option processing
        for option, value in opts:
            if option in ("-h", "--help"):
                raise Usage(help_message)
            if option in ("-i", "--input"):
                spendings_file = value

        runner = Runner(spendings_file)
        runner.run()

    except Usage, err:
        print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
        print >> sys.stderr, "\t for help use --help"
        return 2


if __name__ == "__main__":
    sys.exit(main())
