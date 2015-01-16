#!/usr/bin/python

import sys
import os

from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook


def save_xlsx_as_data(rows, title):
    wb = Workbook()
    ws = wb.worksheets[0]
    ws.title = title

    for row_idx, row_items in enumerate(rows):
        ws.append(row_items)

    return save_virtual_workbook(wb)


def test():
    from ical import get_events_from_stream
    with open("../test_ics/test.ics", 'r') as f:
        events = get_events_from_stream(f)

    rows = [ev.as_tuple() for ev in events]

    filename = "file.xlsx"

    if os.path.exists(filename):
        print "File \"%s\" already exists" % filename
        print "Deleting:", filename
        os.remove(filename)
    with open(filename, 'wb') as f:
        f.write(save_xlsx_as_data(rows, title="Title"))
    print "File \"%s\" saved" % filename


if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8')
    test()
