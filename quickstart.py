import os.path

from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'credentials.json')

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1bhymydKnmcxvaJZa7P7s5ZhZsnHH_cTBI1D1_HYAVVc'

service = build('sheets', 'v4', credentials=credentials)

# Call the Sheets API
sheet = service.spreadsheets()


# for k, v in result.items():
#     print(f'{k} {v}')


def add_in_table(report: dict, list_name: str):
    global start, end
    # start: int
    # end: int
    range_values = f"{list_name}"
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=range_values).execute()

    # for k, v in result.items():
    #     line_count = len(v) + 1

    # line_count = int(line_count.day) + 2
    line_count = int(report.get('stuff_time_report').day) + 2
    col_count = int(report.get('stuff_time_report').month)

    if col_count in [1, 2, 3]:
        pass
    elif col_count in [4, 5, 6]:
        line_count += 34
    elif col_count in [7, 8, 9]:
        line_count += 34*2
    elif col_count in [10, 11, 12]:
        line_count += 34*3

    if col_count in [1, 4, 7, 10]:
        start = "A"
        end = "G"
    elif col_count in [2, 5, 8, 11]:
        start = "I"
        end = "O"
    elif col_count in [3, 6, 9, 12]:
        start = "Q"
        end = "W"
    service.spreadsheets().values().batchUpdate(spreadsheetId=SAMPLE_SPREADSHEET_ID, body={
        "valueInputOption": "USER_ENTERED",
        # Данные воспринимаются, как вводимые пользователем (считается значение формул)
        "data": [
            {"range": f"{range_values}!{start}{line_count}:{end}{line_count}",
             "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
             "values": [
                 [str(report.get('stuff_time_report')), report.get('standard'), report.get('premium'),
                  report.get('fruit'), report.get('service'), report.get('ID'),
                  str(report.get('real_time_report'))], # f"=(C{line_count}+D{line_count})*10 + E{line_count}*5"
             ]}
        ]
    }).execute()

# values = result.get('values', [])
# print(values)
