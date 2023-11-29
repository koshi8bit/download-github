import concurrent.futures
import datetime
import os
import shutil
from threading import Timer, Thread
from pathlib import Path


class Utils:

    @staticmethod
    def dir_create(path: str):
        Path(path).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def dir_rm(_path: str):
        shutil.rmtree(_path)

    @staticmethod
    def dir_exist(_path: str):
        return os.path.isdir(_path)

    @staticmethod
    def dict_extend(_dict: dict, index, elem: list, add_duplicate=False) -> dict:
        import copy
        res = copy.deepcopy(_dict)

        for e in elem:
            res = Utils.dict_append(res, index, e, add_duplicate)

        return res

    @staticmethod
    def dict_append(_dict: dict, index, elem, add_duplicate=False) -> dict:
        import copy
        res = copy.deepcopy(_dict)
        if index in res:
            if add_duplicate:
                res[index].append(elem)
            else:
                if elem not in res[index]:
                    res[index].append(elem)
        else:
            res[index] = [elem]

        return res

    @staticmethod
    def json_get_val(_json, path, default_value=None):
        """
        Get value from JSON
        :param _json:
        :param path:
        :param default_value:
        :return: value. If not found - default_value
        """
        cur = _json
        for section in path:
            if section not in cur:
                return default_value
            cur = cur[section]
        return cur

    class ThreadPoolResult:
        def __init__(self, arg, result, exception):
            self.arg = arg
            self.result = result
            self.exception = exception

        def __str__(self):
            return f"arg='{self.arg}'; result='{self.result}'; exception='{self.exception}'"


    @staticmethod
    def start_thread_pool(f, args: list, threads=None):
        """
        Runs code in multiple threads
        :param f: function
        :param args: array of tuple
        :param threads: Count of threads. If None - same as len of args
        :return:
        """
        res = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            future_task = {}
            for arg1 in args:
                future_task[executor.submit(f, *arg1)] = arg1
                # print(f"{arg1=}")
                # print("!!", *arg1)
            # future_task = {executor.submit(f, *arg1): arg1 for arg1 in args}
            for future in concurrent.futures.as_completed(future_task):
                arg2 = future_task[future]
                try:
                    # res.append((arg2, future.result(), None))
                    res.append(Utils.ThreadPoolResult(arg2, future.result(), None))
                except Exception as exc:
                    print(f"start_thread_pool exception: {str(exc)}")
                    res.append(Utils.ThreadPoolResult(arg2, None, exc))
                    # res.append((arg2, None, exc))
        return res


class Format:
    separator_iso = 'T'
    separator_ui = '@'
    separator_file = '--'

    date_ui_format = '%Y-%m-%d'
    time_ui_format = '%H:%M:%S'
    time_ui_ms_format = time_ui_format + '.%f'

    date_file_format = date_ui_format
    time_file_format = '%H-%M-%S'
    time_file_ms_format = time_file_format + '-%f'

    @staticmethod
    def now(_format: str):
        return datetime.datetime.now().strftime(_format)

    @staticmethod
    def _format(dt: datetime.datetime, _format: str):
        if dt:
            return dt.strftime(_format)
        else:
            return Format.now(_format)

    # ui

    @staticmethod
    def date_ui(dt: datetime.datetime = None) -> str:
        return Format._format(dt, Format.date_ui_format)

    @staticmethod
    def time_ui(dt: datetime.datetime = None, show_ms=False) -> str:
        return Format._format(dt, Format.time_ui_ms_format if show_ms else Format.time_ui_format)

    @staticmethod
    def date_time_ui_format(show_ms=False, separator=separator_iso) -> str:
        return Format.date_ui_format + separator + (Format.time_ui_ms_format if show_ms else Format.time_ui_format)

    @staticmethod
    def date_time_ui(dt: datetime.datetime = None, show_ms=False, separator=separator_iso) -> str:
        f = Format.date_time_ui_format(show_ms, separator)
        return Format._format(dt, f)

    # file

    @staticmethod
    def date_file(dt: datetime.datetime = None) -> str:
        return Format._format(dt, Format.date_file_format)

    @staticmethod
    def time_file(dt: datetime.datetime = None, show_ms=False) -> str:
        return Format._format(dt, Format.time_file_ms_format if show_ms else Format.time_file_format)

    @staticmethod
    def date_time_file_format(show_ms=False, separator=separator_iso) -> str:
        return Format.date_file_format + separator + \
               (Format.time_file_ms_format if show_ms else Format.time_file_format)

    @staticmethod
    def date_time_file(dt: datetime.datetime = None, show_ms=False, separator=separator_iso) -> str:
        f = Format.date_time_file_format(show_ms, separator)
        return Format._format(dt, f)

    # double

    @staticmethod
    def double(value, precision=3, scientific_notation=False, comma_separator='.',
               thousands_separator: str = "") -> str:
        assert isinstance(value, (float, int))
        assert isinstance(precision, int)
        assert isinstance(scientific_notation, bool)
        assert isinstance(comma_separator, str)
        assert isinstance(thousands_separator, str)

        scientific_notation_letter = 'E' if scientific_notation else 'f'
        result = f"{value:,.{precision}{scientific_notation_letter}}"

        result = result.replace(",", thousands_separator)

        if comma_separator != '.':
            result = result.replace('.', ',')

        return result


###


class BackgroundWorker(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


