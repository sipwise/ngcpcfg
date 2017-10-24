#!/usr/bin/env python3

import os
import csv
import tempfile
import openpyxl
import openpyxl.utils


def read(filepath):
    """Read CSV file `filepath` with delimiter ``|``.
    Write data into a ``openpyxl.Workbook`` in memory.
    Finally write the binary spreadsheet in a
    ``tempfile.TemporaryFile`` and return its file
    descriptor at seek position 0.

    :return:        tmp file descriptor containing spreadsheet data
    :type:          file descriptor
    """
    dst_fd = tempfile.TemporaryFile()
    book = openpyxl.Workbook()
    sheet = book.active

    with open(filepath) as src_fd:
        reader = csv.reader(src_fd, delimiter='|', quoting=csv.QUOTE_MINIMAL)
        for rowid, line in enumerate(reader):
            for colid, val in enumerate(line):
                c = openpyxl.utils.get_column_letter(colid + 1)
                r = str(rowid + 1)
                val = val.strip()

                if val == "":
                    val = None
                sheet[c + r] = val

    book.save(dst_fd)
    dst_fd.seek(0, os.SEEK_SET)
    return dst_fd
