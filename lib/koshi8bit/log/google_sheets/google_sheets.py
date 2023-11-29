# https://habr.com/ru/post/483302/
import googleapiclient
from oauth2client.service_account import ServiceAccountCredentials
import httplib2
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
import re
import validators
import ssl


class GoogleSheets:
    service = None
    spreadsheet_id = None

    def __init__(self, creds_json: str, full_link: str):
        self.creds_json = creds_json
        self.full_link = full_link
        self.init()


    def init(self):
        # self.check_cred_file(creds_json)
        self.credentials_file = self.creds_json
        try:
            self.connect()

        except FileNotFoundError as e:
            raise e

        except Exception:
            raise self.InvalidCred

        if validators.url(self.full_link):
            self.spreadsheet_id = self.parsing_id_from_table_link(self.full_link)
        elif self.full_link is None:
            raise ValueError("Id of the table is None. Perhaps you forgot to pass the required full_link parameter")
        else:
            self.spreadsheet_id = self.full_link

    class InvalidCred(Exception):
        def __str__(self):
            return "Credentials file is invalid"

    class InvalidSpreadsheetURLorId(Exception):
        def __str__(self):
            return "Spreadsheet URL or ID is invalid"

    class InvalidRange(Exception):
        def __init__(self, range_: str):
            self.range = range_

        def __str__(self):
            return f"Range is invalid ({self.range})"

    class AppendUnsuccessful(Exception):
        def __str__(self):
            return "Append to spreadsheet is unsuccessful"

    class WriteUnsuccessful(Exception):
        def __str__(self):
            return "Write to spreadsheet is unsuccessful"

    class ClearUnsuccessful(Exception):
        def __str__(self):
            return "Clear in spreadsheet is unsuccessful"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    @staticmethod
    def check_cred_file(file_name: str):
        if not os.path.isfile(file_name):
            raise ValueError("Cred file does not exist")

    def parsing_id_from_table_link(self, full_link: str):
        full_link = full_link.rstrip("/")
        sheet_id = re.search(r"https://docs\.google\.com/spreadsheets/d/(.+)", full_link)
        if sheet_id is None:
            raise self.InvalidSpreadsheetURLorId

        sheet_id = sheet_id.group(1)
        if sheet_id is None:
            raise self.InvalidSpreadsheetURLorId

        return sheet_id

    def connect(self):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self.credentials_file,
            ['https://www.googleapis.com/auth/spreadsheets',
             'https://www.googleapis.com/auth/drive'])
        http_auth = credentials.authorize(httplib2.Http())
        self.service = build('sheets', 'v4', http=http_auth)

    def disconnect(self):
        self.service.close()

    def process_ex(self, e: Exception, range_: str):
        if 'Details: "Requested entity was not found."' in str(e):
            raise self.InvalidSpreadsheetURLorId
        if 'Details: "Unable to parse range: ' in str(e):
            raise self.InvalidRange(range_)
        raise e

    def _read(self, range_: str):
        try:
            result_input = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id,
                                                                    range=range_).execute()
            return result_input.get('values', [])

        except Exception as e:
            self.process_ex(e, range_)

    def read(self, sheet: str, pos: str):
        range_ = f'{sheet}!{pos}'
        return self._read(range_)

    def read_cell(self, sheet: str, pos: str):
        range_ = f'{sheet}!{pos}:{pos}'
        values_input = self._read(range_)

        if not values_input:
            return None

        return values_input[0][0]

    def append(self, sheet: str, pos: str, data):
        range_ = f'{sheet}!{pos}'
        try_more_times = True
        while try_more_times:
            try:
                res = self.service.spreadsheets().values().append(
                    spreadsheetId=self.spreadsheet_id,
                    range=range_, valueInputOption="USER_ENTERED",
                    insertDataOption="INSERT_ROWS", body={"values": data}
                ).execute()

                is_ok = isinstance(res, dict) and 'spreadsheetId' in res and res['spreadsheetId'] == self.spreadsheet_id

                if not is_ok:
                    raise self.AppendUnsuccessful
                try_more_times = False
                return res

            except ssl.SSLEOFError as e:
                logging.warning(f"ssl.SSLEOFError detected: {str(e)}")
                print(f"ssl.SSLEOFError detected: {str(e)}")
                self.init()

            except Exception as e:
                try_more_times = False
                self.process_ex(e, range_)

    def write(self, sheet: str, pos: str, data):
        range_ = f'{sheet}!{pos}'
        try:
            res = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_, valueInputOption="USER_ENTERED", body={"values": data}
            ).execute()

            is_ok = isinstance(res, dict) and 'spreadsheetId' in res and res['spreadsheetId'] == self.spreadsheet_id

            if not is_ok:
                raise self.WriteUnsuccessful
            return res

        except Exception as e:
            self.process_ex(e, range_)

    def clear(self, sheet: str, pos: str):
        range_ = f'{sheet}!{pos}'
        try:
            body = {}
            res = self.service.spreadsheets().values().clear(
                spreadsheetId=self.spreadsheet_id, range=range_, body=body
            ).execute()

            is_ok = isinstance(res, dict) and 'spreadsheetId' in res and res['spreadsheetId'] == self.spreadsheet_id

            if not is_ok:
                raise self.ClearUnsuccessful
            return res

        except Exception as e:
            self.process_ex(e, range_)

    # def __del__(self):
    #     self.disconnect()
