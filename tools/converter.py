#!/usr/bin/env python
# encoding: utf-8
"""
converter.py

Created by Breyten Ernsting on 2013-02-11.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
"""

import os
import sys
import re
import getopt
import logging
import codecs

from xlrd import open_workbook

help_message = '''
Converts amsterdam excel file with expenditure data
'''

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def cleanup(text):
    return re.compile("\s+", re.U).sub(u' ', text)

def format_string(value):
    return "\"%s\"" % (value,)

class Runner(object):
    def __init__(self, spending_file):
        logger.debug('Initializing ...')
        self.spending_file = spending_file

    def _process_sheet(self, wb, ws, csv_file):
        if (re.compile('baten', re.U).search(ws.name) is not None):
            entry_type = u'baten'
        else:
            entry_type = u'lasten'

        # CSV format is this:
        csv_file.write(
            u','.join(['hoofdfunctie','hoofdfunctie_code','categorie','categorie_code','type','time', 'amount']) + "\n"
        )

        logger.debug('Starting to process sheet %s', ws.name)
        in_details = False
        for row in range(ws.nrows):
            skip_row = False
            first_cell = ws.cell(row, 0)

            if not in_details and (first_cell.value is not None):
                try:
                    in_details = (re.compile('Hoofdfunctie', re.U).match(unicode(first_cell.value)) is not None)
                    skip_row = in_details
                except UnicodeEncodeError, e:
                    in_details = False
            if in_details and (first_cell.value is not None):
                in_details = not (re.compile('Totaal hoofdfunctie', re.U).match(unicode(first_cell.value)) is not None)

            if not in_details or skip_row:
                continue                

            hoofdfunctie_code = unicode(int(first_cell.value))
            hoofdfunctie = unicode(ws.cell(row, 1).value)
            for col in range(ws.ncols):
                if col < 2:
                    continue
                categorie_code = unicode(ws.cell(0, col).value)
                categorie = unicode(ws.cell(1, col).value)
                if re.compile('Totaal').match(categorie) is not None:
                    continue
                raw_value = ws.cell(row, col).value 
                if raw_value is not None and (unicode(raw_value) != u''):
                    value = unicode(float(raw_value) * 1000)
                else:
                    value = u'0.0'
                csv_file.write(
                    u','.join([
                        format_string(cleanup(hoofdfunctie)),
                        format_string(hoofdfunctie_code),
                        format_string(cleanup(categorie)),
                        format_string(categorie_code),
                        format_string(entry_type),
                        u"2013",
                        value
                    ])  + "\n"
                )

    def run(self):
        logger.info('Running ...')
        wb = open_workbook(self.spending_file)
        logger.debug('Opened file ...')

        csv_file = codecs.open('output.csv', 'w', 'utf-8')
        for s in wb.sheets():
            if re.compile('Verdelingsmatrix', re.U).search(s.name):
                self._process_sheet(wb, s, csv_file)
        csv_file.close()

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
