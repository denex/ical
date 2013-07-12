#!/usr/bin/python
#-*- coding: utf8 -*-

import sys
import os

from openpyxl import Workbook
from openpyxl.cell import get_column_letter
from openpyxl.style import Color, Fill
from openpyxl.reader.excel import load_workbook
from openpyxl.writer.excel import save_virtual_workbook

def save_xlsx(rows, title=''):
    wb = Workbook()#optimized_write=True)
    ws = wb.worksheets[0]
    ws.title = title

    for row_idx, row_items in enumerate(rows):
        # ws.append(row_items)
        for col_idx, cell_value in enumerate(row_items):
            cell = ws.cell('%s%s' % (get_column_letter(col_idx + 1), row_idx + 1))
            cell.value = cell_value
            # cell.value = "test"

    return save_virtual_workbook(wb)

def main():
    from ical import get_events_from_stream
    with open("/Users/denex/Downloads/SandDraw.ics", 'r') as f:
        events = get_events_from_stream(f)

    rows = [ev.as_row() for ev in events]

    filename = "file.xlsx"

    if os.path.exists(filename):
        print "File \"%s\" already exists" % filename
        print "Deleting:", filename
        os.remove(filename)
    with open(filename, 'wb') as f:
        f.write(save_xlsx(rows, title="Title"))
    print "File \"%s\" saved" % filename

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8')
    main()
