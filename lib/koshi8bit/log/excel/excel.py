import lib.koshi8bit.easy_living as el
from datetime import datetime
import os
import numpy as np
from functools import reduce
import statistics


class Excel:

    def __init__(self, path: str, headers: list[str], precision=3, scientific_notation=True,
                 add_time=True, auto_commit_sec=1, auto_push_sec=60):
        # assert isinstance(path, str)
        # assert isinstance(headers, list)
        # assert isinstance(precision, int)
        # assert isinstance(scientific_notation, bool)
        # assert isinstance(add_time, bool)
        # assert isinstance(auto_commit_sec, int)
        # assert isinstance(auto_push_sec, int)

        self.precision = precision
        self.scientific_notation = scientific_notation
        self.add_time = add_time
        self._commit_buffer = []
        self.headers_without_time = headers

        f = el.Format.date_time_file(False)
        dt = datetime.now()
        file_name = f'{dt.strftime(f)}.xls'
        el.Utils.dir_create(path)
        self.file_name = os.path.join(path, file_name)

        self.element_delimiter = '\t'
        self.line_delimiter = '\n'

        if headers is None:
            self._buffer = ''
        else:
            if add_time:
                headers = ['time', 'datetime'] + headers
            self._buffer = self._prepare_line(headers)

        if auto_commit_sec > 0:
            self._bw_commit = el.BackgroundWorker(auto_commit_sec, self._commit_n_records)
        else:
            self._bw_commit = None
        if auto_push_sec > 0:
            self._bw_push = el.BackgroundWorker(auto_push_sec, self._push)
        else:
            self._bw_push = None

        self._push()

    @staticmethod
    def _calc_avg(arr):
        return float(statistics.mean(arr))

    def _prepare_n_records(self):
        assert isinstance(self._commit_buffer, list)
        changed_axes = list(np.swapaxes(self._commit_buffer, 1, 0))
        self._commit_buffer = []

        avg = list(map(self._calc_avg, changed_axes))
        return avg

    def _commit_n_records(self):
        if not self._commit_buffer:
            # print('asdasd', len(self.headers), [0]*len(self.headers))
            self._commit_buffer = [[0]*len(self.headers_without_time)]

        # print(self._commit_buffer)
        # print(list(map(lambda x: len(x), self._commit_buffer)))
        avg = self._prepare_n_records()

        # print('2', type(avg))
        # print('2', type(avg[0]))

        tmp = self._format_data(avg)
        if self.add_time:
            a = []
            dt = datetime.now()
            a.append(dt.strftime(el.Format.time_ui(False, False)))
            a.append(dt.strftime(el.Format.date_time_ui(False, True)))
            tmp = a + tmp
        tmp = self._prepare_line(tmp)
        self._buffer = self._buffer + tmp

    def commit(self, data):
        assert isinstance(data, list)
        if len(self.headers_without_time) != len(data):
            raise ValueError('len(self.headers_without_time) != len(data)')
        self._commit_buffer.append(data)

    def _push(self):
        with open(self.file_name, 'a') as file:
            file.write(self._buffer)
        self._buffer = ''

    def push(self):
        self._commit_n_records()
        self._push()

    def _format_data(self, data):
        assert isinstance(data, list)
        data_str = [el.Format.double(x, self.precision, self.scientific_notation, False, ',') for x in data]
        return data_str

    def _prepare_line(self, text_array):
        assert isinstance(text_array, list)
        line = self.element_delimiter.join(text_array)
        line = line + self.line_delimiter
        return line

    def close(self):
        if self._bw_commit:
            self._bw_commit.stop()

        if self._bw_push:
            self._bw_push.stop()
