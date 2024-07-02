import gspread
from src.utils.load_config import load_config
from src.utils.utils import get_todays_date

config = load_config('conf/base/config.yaml')
api_creds_filename = config['api_credentials']['filename']
doc_name = config['google_sheets']['seniors_update_doc_name']

gc  = gspread.service_account(filename=api_creds_filename)
file = gc.open(doc_name)

def get_befriending_seniors_list():
    """
    Returns List of Befriending Seniors
    """
    sheet_name = config['google_sheets']['befriending_seniors_update_sheet_name']
    spreadsheet = file.worksheet(sheet_name)
    seniors = spreadsheet.col_values(1)
    return list(filter(lambda string: string.strip() != "", seniors))

def get_frail_seniors_list():
    """
    Returns List of Frail Seniors
    """
    sheet_name = config['google_sheets']['frail_seniors_update_sheet_name']
    spreadsheet = file.worksheet(sheet_name)
    seniors = spreadsheet.col_values(1)
    return list(filter(lambda string: string.strip() != "", seniors))

def get_columns(sheet_name=""):
    """
    Returns the list of columns
    """
    if sheet_name == "":
        raise Exception("Sheet Name Empty!")

    spreadsheet = file.worksheet(sheet_name)
    cols = spreadsheet.row_values(1)
    return cols

def find_cell_to_update(senior:str, sheet_name=""):
    if sheet_name == "":
        raise Exception("Sheet Name Empty!")

    spreadsheet = file.worksheet(sheet_name)
    today = get_todays_date()
    if today not in get_columns(sheet_name=sheet_name):
        spreadsheet.insert_cols(values=[[today]], col=2)
        target_col = 2
    else:
        target_col = spreadsheet.find(today, in_row=1).col
    target_row = spreadsheet.find(senior, in_column=1).row
    return (target_row, target_col)

def update_cell_with_msg(cell_coords , message="", sheet_name=""):
    if sheet_name == "":
        raise Exception("Sheet Name Empty!")
    
    row, col = cell_coords
    spreadsheet = file.worksheet(sheet_name)
    spreadsheet.update_cell(row, col, message)

def get_cell_contents(cell_coords, sheet_name=""):
    if sheet_name == "":
        raise Exception("Sheet Name Empty!")
    
    row, col = cell_coords
    spreadsheet = file.worksheet(sheet_name)
    return spreadsheet.cell(row,col).value



