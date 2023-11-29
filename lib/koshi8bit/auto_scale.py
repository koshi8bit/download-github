
class AutoScale:

    @staticmethod
    def byte(size: int):
        text = ['B', 'kB', 'MB', 'GB', 'TB', 'PB']
        i = 0
        while True:
            if size < 1000:
                return f'{round(size, 1)} {text[i]}'

            size = size / 1000
            i = i + 1
