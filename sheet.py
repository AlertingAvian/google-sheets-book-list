import gspread
import gspread_formatting

from models import BookData

gc = gspread.oauth()


def create_sheet() -> (gspread.Spreadsheet, gspread.Worksheet):
    sheet = gc.create("Book Tracker")
    w = sheet.add_worksheet(title="Book Tracker", cols=7, rows=1)
    w.update('A1:K1', [["Title", "Author(s)", "Year", "Publisher", "Description", "ISBN", "Notes"]])
    sheet.del_worksheet(sheet.get_worksheet(0))
    return sheet, w


def open_or_create_sheet() -> (gspread.Spreadsheet, gspread.Worksheet):
    try:
        sheet = gc.open("Book Tracker")
    except gspread.exceptions.SpreadsheetNotFound:
        return create_sheet()
    else:
        w = sheet.worksheet("Book Tracker")
        return sheet, w


def add_book(worksheet: gspread.Worksheet, data: BookData, notes: str = "") -> None:
    response = worksheet.append_row([data.Title, ", ".join(data.Authors), data.Year,
                                     data.Publisher, data.Description, data.ISBN, notes],
                                    value_input_option='RAW', insert_data_option='INSERT_ROWS')

    updated_range = response['updates']['updatedRange'].split('!')[1]
    gspread_formatting.set_row_height(worksheet, updated_range[::-1][0], 21)
