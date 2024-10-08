import gspread
from gspread_formatting import format_cell_range, CellFormat, TextFormat
from gspread.exceptions import SpreadsheetNotFound, GSpreadException, APIError
from google.oauth2.service_account import Credentials
from datetime import datetime
import re
import os
import calendar
from termcolor import colored, cprint


# love sandwiches example used as baseline
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET_NAME = 'Recurring Expense Tracker'
MAX_COL_NUMBER = 50
ROW_KEY = "row"
TX_DATE_KEY = "tx_date"
TX_MERCHANT_KEY = "tx_merchant"
TX_AMOUNT_KEY = "tx_amount"
ERROR_TOLERANCE = 0.1
# number of days the tx_date can vary due to weekends, bankholidays etc
SUBS_DAY_FLEX = 4
# in case the amount of the subscription various
SUBS_AMOUNT_FLEX = 1


def intro_go_on():
    """
    Display the intro message
    """
    clean_console()

    cprint("Welcome to the Recurring Expense Tracker: RET!\n", 'red')
    print("You can import your bank account and/or credit card\
          \ntransaction data into RET.")
    print("RET will sort through all the transaction\
          \ndata and provide you with a list of recurring expenses\
          \nand subscriptions. To provide a platform for you to\
          \nmanage your recurring expenses,")
    print("RET will use Google Sheets to let you import your\
          \nCSV files and provide the output for you as well.\n")
    print("If you like, RET can create a new Google Spreadsheet and\
          \nshare it with you.")
    print("If you already have one please select option 2. below.\n")

    cprint("How do you want to continue?\n\
        \nPress\
        \n1: to create a new Spreadsheet\
        \n2: for re-using one previsously created (through RET or by you)\
        \nAny other key to EXIT:", 'red')

    go_on = input("\n")

    if go_on == "1":
        return 1
    elif go_on == "2":
        return 2
    else:
        return False


def get_user_email():
    """
    Get user email from the user
    """
    user_email = input("Enter your email address: ")
    while not validate_email(user_email):
        print("The email address you entered is not a \
            \nvalid email address. Please try again.")
        user_email = input("Enter your email address:\n")

    return user_email


def validate_email(email):
    """
    Make sure that email is a valid email address. Function
    provided by Github Copilot
    """
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if re.match(pattern, email):
        return True
    else:
        return False


def create_spreadsheet(user_email):
    """
    Create a new worksheet for the user and share it
    with the user and RET
    Note: RET is owner and the user is editor.
    Later versions should make user owner
    Return: the Spreadsheet object created
    """

    print("\nRET is creating a new worksheet for you...")
    try:
        spreadsheet = GSPREAD_CLIENT.create(SHEET_NAME)
        spreadsheet.share(user_email, perm_type='user', role='writer')

    except Exception as e:
        print(f"An error occurred: {e}")
        # from https://docs.python.org/3/tutorial/errors.html:
        print(type(e))    # the exception type
        print("Please try again later.")
        return False

    return spreadsheet


def get_existing_spreadsheet():
    """
    Open an a spreadsheet that was created through RET
    Return: the Spreadsheet object that the user wants to open
    """
    try:
        cprint("IMPORTANT! Please use right mouse click and \
               \ncopy/past from there!\n", 'light_cyan')
        existing_s_sheet = input("Please paste the URL of the Spreadsheet \
                                 \nyou want to open:\n")

        # loop as long user entered empty string
        while existing_s_sheet == "":
            existing_s_sheet = input("Please paste the URL of the Spreadsheet \
                                     \nyou want to open:\n")

        # let's try to open the spreadsheet
        spreadsheet = open_existing_spreadsheet(existing_s_sheet)
        while not spreadsheet:
            # seems user input isn't correct, so let's ask again
            existing_s_sheet = input("Please paste the URL of the Spreadsheet \
                                     \nyou want to open:\n")
            spreadsheet = open_existing_spreadsheet(existing_s_sheet)

        # all good now so let's return the worksheet
        return spreadsheet

    except KeyboardInterrupt:
        cprint("IMPORTANT! Please use right mouse click and copy/past \
               \nfrom there!\n", 'light_cyan')
        existing_ssheet = get_existing_spreadsheet()
        return existing_ssheet

    except Exception as e:
        print(f"An error occurred: {e}")
        # from https://docs.python.org/3/tutorial/errors.html:
        print(type(e))    # the exception type
        print("Please try again.")


def open_existing_spreadsheet(existing_ssheet):
    """
    Open an a spreadsheet that was created through RET
    """

    try:
        spreadsheet = GSPREAD_CLIENT.open_by_url(existing_ssheet.strip())

    except SpreadsheetNotFound as e:
        print(f"\nRET couldn't find your spreadsheet: {e}")
        return False

    except APIError as e:
        # requested help from Copilot
        if e.response.status_code == 403:
            print(f"\nYou do not have access to this spreadsheet: {e}")
        else:
            print(f"\nAn API error occurred: {e}")
        return False

    except GSpreadException as e:
        print(f"\nAn error occurred trying to access the spreadsheet: {e}")
        return

    except PermissionError:
        print(f"\nRET does not have permission to access this spreadsheet. \
                \nYou can add RET as an editor to the spreadsheet.")
        print(f"\
              \nClick Share on the upper right corner of the Google \
              \nSheet and add:")
        print(f"\n\n{CREDS.service_account_email}")
        cprint("\nKEEP IN MIND: always use right mouse click to copy/paste!",
               'light_cyan')
        print("\n\nPlease select 'Editor' and uncheck: 'Notify people'\
                \nThen try again.\n\n")
        return False

    except Exception as e:
        print(f"\nUnexpected  error occurred: \n")
        # from https://docs.python.org/3/tutorial/errors.html:
        print(type(e))    # the exception type

        return False

    return spreadsheet


def wait_for_user(display_text):
    """
    display text with y/n option
    Wait for the user until he/she presses 'y'
    """
    response = input(f"\n{display_text}\n")

    while response == "n":
        response = input(f"{display_text}\n")


def continue_RET():
    """
    ask user if she/he wants to continue or exit the program
    """
    response = input("\nDo you want to continue with this \
                     Recurring Expense Tracker? (y/n):\n")
    if response == "y":
        return True
    else:
        print("Goodbye!")
        return False


def get_imported_csv_wsheet(spreadsheet):
    """
    prompts the user to import  the CSV file to a
    Google Worksheet and privde it's name
    returns: the worksheet that the user imported
    the CSV file to
    """
    print(f"Now, please imnport your CSV file to the Google Sheet: \
          \n'{spreadsheet.title}', RET just created or opened.")
    print("You can do this by clicking on the 'File' menu in the \
          \nGoogle Sheet and selecting 'Import'.")

    wait_for_user("Have you imported the CSV file to the \
                  \nGoogle Sheet? (y/n): ")

    clean_console()

    try:
        print(f"You are working with the Google Sheet: '{spreadsheet.title}'")

        print("\nPlease enter the worksheet name where you \
              \nimported the CSV file.")
        print("\nYou can do this by double-clicking on the \
              \nSheet Name (e.g. 'Sheet1') in footer of the Spreadsheet.")
        cprint("KEEP IN MIND: always use right mouse click \
               \nto copy/paste!\n", 'light_cyan')
        ws_name = input("Sheet name:\n")

        # loop as long user entered empty string
        while ws_name == "":
            ws_name = input("Please enter the worksheet name \
                            \nwhere you imported the CSV file:\n")

        # let's try to select the worksheet
        worksheet = select_imported_csv_wsheet(spreadsheet, ws_name)
        while not worksheet:
            # seems user input isn't correct, so let's ask again
            ws_name = input("Please enter the worksheet name where \
                            \nyou imported the CSV file:\n")
            worksheet = select_imported_csv_wsheet(spreadsheet, ws_name)

        # all good now so let's return the worksheet
        return worksheet

    except Exception as e:
        print(f"\nUnexpected error occurred in get_imported_csv_wsheet(): \n")
        print("Please keep in mind to not use keyboad shortcuts")
        print("use right mouse click menue instead")
        # from https://docs.python.org/3/tutorial/errors.html:
        print(type(e))    # the exception type
        get_imported_csv_wsheet(spreadsheet)


def select_imported_csv_wsheet(spreadsheet, ws_name):
    """
    try to select worksheet ws_name
    return valid worksheet or False
    """
    try:
        worksheet = spreadsheet.worksheet(ws_name)

    except gspread.exceptions.WorksheetNotFound as e:
        print(f"\nRET couldn't find your worksheet: {e}")
        return False

    except Exception as e:
        print(f"\nUnexpected  error occurred: \n")
        # from https://docs.python.org/3/tutorial/errors.html:
        print(type(e))    # the exception type
        return False

    return worksheet


def get_int(message):
    """
    Check if the value is an integer
    """
    try:
        int_value = int(input(message))

    except ValueError:
        int_value = input(message)
        return False

    return int_value


def column_letter_to_number(column_letter):
    """
    Convert a spreadsheet column letter (e.g., 'A', 'B', 'Q')
    to its respective number value.
    Supports multi-letter columns (e.g., 'AA', 'AB').
    Returns: list of selected columns as numbers. Calling
    function must subtract 1 to get zero-based index.
    """

    # let's check if column_letter already is an integer
    try:
        column_number = int(column_letter)

    except ValueError:
        # Provided by Copilot:
        column_letter = column_letter.upper()
        column_number = 0
        for char in column_letter:
            column_number = column_number * 26 + (ord(char) - ord('A') + 1)

    # let's make some some common sense checking in the value could right
    try:
        if column_number < 1:
            print(f"The column number is {str(column_number)}. \
                  It cannot be less than 1.")
            return False
        elif column_number > MAX_COL_NUMBER:
            print("The column number is {str(column_number)}. \
                  It cannot be higher then 50")
            return False
        else:
            return column_number

    except Exception as e:
        print(f"\nUnexpected  error occurred: \n")
        # from https://docs.python.org/3/tutorial/errors.html:
        print(type(e))    # the exception type
        return False


def import_raw_data(raw_data_wsheet):
    """
    Import the raw transaction data from the worksheet
    where the user imported his/her CSV file into a list of lists
    Return: the list of lists with the raw transaction data
    """

    # let's start with the row where the transaction data starts
    input_message = "\nPlease enter the row number where the \
        \ntransaction data starts (e.g. 1, 2, 3, etc.):\n"
    start_row = get_int(input_message)
    while not start_row:
        start_row = get_int(input_message)

    # now the columns for tx_date, tx_merchant, and tx_amount
    # let's start with the transaction date column
    message = "\nPlease enter the column letter where the\
        \ntransaction date is located \n(e.g. A, B, C, etc.):\n"
    tx_date_col = column_letter_to_number(input(message))
    while not tx_date_col:
        tx_date_col = column_letter_to_number(input(message))

    # we need to subtract 1 to get the zero-based index
    tx_date_col -= 1

    # now the merchant column
    message = "\nPlease enter the column letter where the \nmerchant\
        \nor recipient is located (e.g. A, B, C, etc.):\n"
    tx_merchant_col = column_letter_to_number(input(message))
    while not tx_merchant_col:
        tx_merchant_col = column_letter_to_number(input(message))

    # we need to subtract 1 to get the zero-based index
    tx_merchant_col -= 1

    # now the amount column
    message = "\nPlease enter the column letter where the \ntransaction \
        \namount is located (e.g. A, B, C, etc.):\n"
    tx_amount_col = column_letter_to_number(input(message))
    while not tx_amount_col:
        tx_amount_col = column_letter_to_number(input(message))

    # we need to subtract 1 to get the zero-based index
    tx_amount_col -= 1

    print(f"\nRET is now importing your raw transaction data \
          \nfrom the worksheet: {raw_data_wsheet.title}.")
    print("This may take a few seconds depending on the \
          \nsize of the data.\n")
    print("Please wait...\n")

    raw_tx_data = raw_data_wsheet.get_all_values()

    # we need to loop through the list of lists and
    # extract the rows and columns that the user specified
    # and create a list of dfictionaries
    selected_tx_data = []

    for i in range(int(start_row)-1, len(raw_tx_data)-1):
        # check if any cell is empty
        if raw_tx_data[i][tx_date_col].strip() == "" or \
           raw_tx_data[i][tx_merchant_col].strip() == "" or \
           raw_tx_data[i][tx_amount_col].strip() == "":
            continue

        new_row = {
                    ROW_KEY: i+1,
                    TX_DATE_KEY: raw_tx_data[i][tx_date_col],
                    TX_MERCHANT_KEY: raw_tx_data[i][tx_merchant_col],
                    TX_AMOUNT_KEY: raw_tx_data[i][tx_amount_col]
                    }

        selected_tx_data.append(new_row)

    return selected_tx_data


def sort_key(d):
    """
    Return the key for sorting the data
    """
    return (d['tx_merchant'], datetime.strptime(d['tx_date'], '%d.%m.%Y'))


def clean_console():
    """
    cleans the console window.
    """
    # copied from:
    # https://www.sololearn.com/en/Discuss/3220821/how-how-to-delete-printed-text
    os.system('cls' if os.name == 'nt' else 'clear')


def convert_datetime_object_to_str(tx_date):
    """
    Convert tx_date into a string using the local setting.
    """
    local_date = tx_date.strftime('%d.%m.%Y')

    return local_date


def format_row_in_worksheet(worksheet, row, type):
    """
    formatting a row in worksheet
    outline provided by ChatGPT
    """
    # Define the range of the last row (e.g., A10:D10 for 4 columns)
    cell_range = f"A{row}:K{row}"

    if type == "bold":
        # Apply bold formatting to the row
        format_cell_range(worksheet, cell_range,
                          CellFormat(textFormat=TextFormat(bold=True)))

    if type == "normal":
        # Apply bold formatting to the row
        format_cell_range(worksheet, cell_range,
                          CellFormat(textFormat=TextFormat(bold=False)))


def append_and_format_row(ws_output, row_data, format_type):
    """
    Append a new row to the worksheet and format it
    """
    # Seems there is a bug in gspread when trying to a
    # dd an empty row. Let's try this:
    if not row_data or row_data == [""]:
        row_data = ["-"]

    ws_output.append_row(row_data)
    # Get the row count after appending the new row
    new_row_index = len(ws_output.get_all_values())
    format_row_in_worksheet(ws_output, new_row_index, format_type)


def append_dataset1_headings(ws_output):
    """
    Append the headings of the dataset to the worksheet
    """
    keys_list = [
        TX_MERCHANT_KEY,
        "subs_day",
        TX_AMOUNT_KEY,
        "subs_start_date",
        "subs_end_date",
        "subs_frequency",
        "subs_merchant_sum",
        "num_subs_tx",
        "active"
        ]
    append_and_format_row(ws_output, keys_list, "bold")


def append_dataset2_headings(ws_output):
    """
    Append the headings of the dataset to the worksheet
    """
    keys_list = [
        TX_MERCHANT_KEY,
        "last_tx_date",
        "first_tx_date",
        "last_tx_amount",
        "merchant_sum",
        "num_tx"
        ]
    append_and_format_row(ws_output, keys_list, "bold")


def append_sorted_headings(ws_output):
    """
    Append the headings of the dataset to the worksheet
    """
    keys_list = [
        TX_DATE_KEY,
        TX_MERCHANT_KEY,
        TX_AMOUNT_KEY,
        ]
    append_and_format_row(ws_output, keys_list, "bold")


def append_dataset1_rows(ws_output, dataset):
    """
    Append the rows of dataset1 to the worksheet
    """
    for row in dataset:
        ws_output.append_row([
            row[TX_MERCHANT_KEY],
            row["subs_day"],
            row[TX_AMOUNT_KEY],
            convert_datetime_object_to_str(row["subs_start_date"]),
            convert_datetime_object_to_str(row["subs_end_date"]),
            row["subs_frequency"],
            row["subs_merchant_sum"],
            row["num_subs_tx"],
            str(row["active"])
        ], value_input_option='USER_ENTERED')

        new_row_index = len(ws_output.get_all_values())
        format_row_in_worksheet(ws_output, new_row_index, "normal")


def append_dataset2_rows(ws_output, dataset):
    """
    Append the rows of dataset2 to the worksheet
    """
    for row in dataset:
        ws_output.append_row([
            row[TX_MERCHANT_KEY],
            convert_datetime_object_to_str(row["last_tx_date"]),
            convert_datetime_object_to_str(row["first_tx_date"]),
            row["last_tx_amount"],
            row["merchant_sum"],
            row["num_tx"]
        ], value_input_option='USER_ENTERED')

        new_row_index = len(ws_output.get_all_values())
        format_row_in_worksheet(ws_output, new_row_index, "normal")


def append_sorted_rows(ws_output, dataset):
    """
    Append the rows of sorted_clean data to the worksheet
    """
    for row in dataset:
        ws_output.append_row([
            convert_datetime_object_to_str(row[TX_DATE_KEY]),
            row[TX_MERCHANT_KEY],
            row[TX_AMOUNT_KEY],
        ], value_input_option='USER_ENTERED')

        new_row_index = len(ws_output.get_all_values())
        format_row_in_worksheet(ws_output, new_row_index, "normal")


def upload_results_to_worksheet(spreadsheet, worksheet_name,
                                heading_dataset1, dataset1,
                                heading_dataset2, dataset2,
                                start_date, end_date):
    """
    create a new worksheet with worksheet_name in spreadsheet and
    upload the data to the selected worksheet
    function can handle max two datasets. Each one is optional
    """
    print("\nStarting the results upload to Google Sheets...")

    try:
        print("Creating a new worksheet...")
        # creating the worksheet
        ws_output = spreadsheet.add_worksheet(
            title=worksheet_name, rows=1, cols=10)

        print("Uploading the data...")
        print("NOTE: this may take a while\
              \nplease be patient!...")

        # filling in the data
        if dataset1:
            # Insert heading for dataset1
            append_and_format_row(ws_output, [heading_dataset1], "bold")
            append_and_format_row(ws_output, [
                "Start-Date", convert_datetime_object_to_str(start_date)],
                "normal")
            append_and_format_row(ws_output, [
                "End-Date", convert_datetime_object_to_str(end_date)],
                "normal")
            append_and_format_row(ws_output, [], "normal")

            # Append dataset headings
            append_dataset1_headings(ws_output)

            # Append dataset rows
            append_dataset1_rows(ws_output, dataset1)

        if dataset2:
            # Insert heading for dataset2
            append_and_format_row(ws_output, [], "normal")
            append_and_format_row(ws_output, [heading_dataset2], "bold")
            append_and_format_row(ws_output, [
                "Start-Date", convert_datetime_object_to_str(start_date)],
                "normal")
            append_and_format_row(ws_output, [
                "End-Date", convert_datetime_object_to_str(end_date)],
                "normal")
            append_and_format_row(ws_output, [], "normal")

            # Append dataset headings
            append_dataset2_headings(ws_output)

            # Append dataset rows
            append_dataset2_rows(ws_output, dataset2)

        print(f"\nThe data has been successfully uploaded to Spreadsheet: \
                \n'{spreadsheet.title}' | worksheet: '{worksheet_name}'")
        print(f"\nStart date: {convert_datetime_object_to_str(start_date)}\
                \nEnd date: {convert_datetime_object_to_str(end_date)}\n")
        return True

    except APIError as e:
        if e.response.status_code == 400:
            print(f"\nA worksheet with the name '{worksheet_name}' \
                  \nalready exists in the spreadsheet: '{spreadsheet.title}'.")
            new_worksheet_name = input("Please enter a different name \
                                       \nfor the worksheet:\n")
            # let's call this function recursively to get things done with
            # a new name for the worksheet
            if upload_results_to_worksheet(spreadsheet, new_worksheet_name,
                                           heading_dataset1, dataset1,
                                           heading_dataset2, dataset2,
                                           start_date, end_date):
                return True
            else:
                return False

        else:
            print(f"\nAn API error occurred: {e}")
            print(f"Status Code: {e.response.status_code}")
            print(f"Error Message: {e.response.text}")
            return False

    except GSpreadException as e:
        print(f"\nAn error occurred trying to access the spreadsheet: {e}")
        return

    except Exception as e:
        print(f"\nUnexpected  error occurred: \n")
        # from https://docs.python.org/3/tutorial/errors.html:
        print(type(e))    # the exception type
        return False


def upload_sorted_to_worksheet(spreadsheet, worksheet_name,
                               heading_dataset1, dataset1,
                               start_date, end_date):
    """
    create a new worksheet with worksheet_name in spreadsheet and
    upload the data to the selected worksheet
    """
    print("\nStarting the data upload to Google Sheets...")

    try:
        print("Creating new worksheet...")
        # creating the worksheet
        ws_output = spreadsheet.add_worksheet(
            title=worksheet_name, rows=1, cols=10)

        print("Uploading the data. NOTE: this may \
              take a while - please be patient!...")

        # filling in the data
        if dataset1:
            # Insert heading for dataset1
            append_and_format_row(ws_output, [heading_dataset1],
                                  "bold")
            append_and_format_row(ws_output, ["Start-Date",
                                              convert_datetime_object_to_str
                                              (start_date)], "normal")
            append_and_format_row(ws_output, ["End-Date",
                                              convert_datetime_object_to_str
                                              (end_date)], "normal")
            append_and_format_row(ws_output, [], "normal")

            # Append dataset headings
            append_sorted_headings(ws_output)

            # Append dataset rows
            append_sorted_rows(ws_output, dataset1)

        print(f"\nThe data has been successfully uploaded to Spreadsheet: \n\
              {spreadsheet.title} | worksheet: {worksheet_name}.")
        print(f"\nStart date of the dataset: \
              {convert_datetime_object_to_str(start_date)} \
                \n| End date: {convert_datetime_object_to_str(end_date)}\n")
        return True

    except APIError as e:
        if e.response.status_code == 400:
            print(f"\nA worksheet with the name '{worksheet_name}' \
                  \nalready exists in the spreadsheet: '{spreadsheet.title}'.")
            new_worksheet_name = input("Please enter a different name for \
                                       \nthe worksheet:\n")
            # let's call this function recursively to get things done
            # with a new name for the worksheet
            if upload_results_to_worksheet(spreadsheet, new_worksheet_name,
                                           heading_dataset1, dataset1,
                                           start_date, end_date):
                return True
            else:
                return False

        else:
            print(f"\nAn API error occurred: {e}")
            print(f"Status Code: {e.response.status_code}")
            print(f"Error Message: {e.response.text}")
            return False

    except GSpreadException as e:
        print(f"\nAn error occurred trying to access the spreadsheet: {e}")
        return

    except Exception as e:
        print(f"\nUnexpected  error occurred: \n")
        # from https://docs.python.org/3/tutorial/errors.html:
        print(type(e))    # the exception type
        return False


def print_data(number_of_rows, data, clean):
    """
    Print the provided number_of_rows of the data requested

    Paramaters:
    number_of_rows: number_of_rows to be printed. 0: print all rows
    data: dataset
    clean: True -> clean the console windows before output
    """
    if clean:
        clean_console()

    print(f"Here is the raw data:\n")

    try:
        if number_of_rows == 0:
            number_of_rows = len(data)

        print(f"{'Row:':<5} | "
              f"{'Date:':<11} | "
              f"{'Merchant/Recepient:':<30} | "
              f"{'Amount:':<10}\n")

        for i in range(number_of_rows):
            r = data[i][ROW_KEY]
            d = data[i][TX_DATE_KEY]
            m = data[i][TX_MERCHANT_KEY]
            a = data[i][TX_AMOUNT_KEY]
            print(f"{r:<5} | "
                  f"{d:<11} | "
                  f"{m:<30} | "
                  f"{a:<10}")

    except Exception as e:
        print(f"\nUnexpected  error occurred in \
                print_data(): \n")
        # from https://docs.python.org/3/tutorial/errors.html:
        print(type(e))    # the exception type
        return False


def check_import_raw_data(sheet, tx_data):
    """
    Check the raw data for any errors and import
    """
    # setting the message to a default value
    message = "An error occurred while cleaning the transaction data.\
        \nDo you want to try again selecting the data from the worksheet?"

    try:
        selected_raw_tx_data = []
        is_data_clean = False

        while not is_data_clean:
            # import raw transaction data from the worksheet
            selected_raw_tx_data = import_raw_data(sheet)

            print_data(10, selected_raw_tx_data, True)
            raw_data_ok = input("\nDo you want to continue with the data? \
                    \n(y/n):\n")

            raw_data_ok = raw_data_ok.strip().lower()
            if raw_data_ok == "n":
                is_data_clean = False

            else:
                # let's check the date format of the input data
                tx_data.check_date_format(selected_raw_tx_data)

                # clean up the tx data row by row
                print("Cleaning up the imported transaction data...")
                clean_data = tx_data.clean_up_tx_data(selected_raw_tx_data)
                if not clean_data:
                    cprint(message, 'red')
                    try_again = input("(y/n):\n")
                    try_again = try_again.strip().lower()
                    if try_again == "n":
                        return False
                    else:
                        is_data_clean = False

                else:
                    is_data_clean = True

        print("The raw transaction data has been successfully imported.\n")
        tx_data.clean_tx_data = clean_data
        tx_data.selected_raw_tx_data = selected_raw_tx_data
        return True

    except Exception as e:
        print(f"\nUnexpected  error occurred in check_inport_raw_data: \n")
        # from https://docs.python.org/3/tutorial/errors.html:
        print(type(e))  # the exception type
        return False


#################################################################
# CLASS TxData                                                  #
#################################################################
class TxData:
    """
    Class to handle all aspects of the transaction data incl:
    clean_up and analysis
    Input: list of dictionaries: selected_raw_tx_data
    """
    # we need some class constants for the date format as this
    # seems to be quite messy
    DATE_FORMAT_DAY_FIRST = True
    ANALYSIS_START_DATE = datetime(2000, 1, 1)
    ANALYSIS_END_DATE = datetime.today()

    subscriptions_data = []
    recurring_merchants_data = []

    def __init__(self):
        self.sorted_clean_data = []
        self.clean_tx_data = []

    def check_date_format(self, data):
        """
        Check the date format manually as parser.parse is trying convert
        the date and if the month value is to high because it is a day
        then it just switches and takes the smaler value as the month
        Sets the class constant DATE_FORMAT_DAY_FIRST to True or False
        """
        print("\nChecking the date format of the input data...\n")

        for row in data:
            date_str = row[TX_DATE_KEY]

            try:
                # let's check if we can deconstruct the date string
                # Regular expression to match dates with '.', '/', or
                # '-' provided by ChatGPT
                match = re.match(r'(\d{1,2})[./-](\d{1,2})[./-](\d{4})',
                                 date_str)

                if not match:
                    print(f"'{date_str}' is not allowed as date.")
                    return False

                # Extract day, month, and year from the matched groups
                # provided by ChatGPT
                day, month, year = map(int, match.groups())

                if month > 12 and month <= 31:
                    # seems the date format is not day first but
                    # month first, so let's # set the class constant
                    # and exit
                    self.DATE_FORMAT_DAY_FIRST = False
                    print("\nSWITCHING DATE FORMAT TO MONTH FIRST\n")
                    return True

                else:
                    return False

            except ValueError:
                print(f"'{date_str}' is not allowed as date.")
                return False

            except Exception as e:
                print(f"\nUnexpected  error occurred: \n")
                # from https://docs.python.org/3/tutorial/errors.html:
                print(type(e))    # the exception type
                return False

    def clean_date(self, date_str):
        """
        cleans the date string
        Return: datetime object, False in case of any error
        """
        # let's deconstruct the date string
        # The followeing regular expression to match dates with '.', '/',
        #  or '-' was provided by ChatGPT
        match = re.match(r'(\d{1,2})[./-](\d{1,2})[./-](\d{4})', date_str)

        if not match:
            print(f"'{date_str}' is not allowed as date.")
            return False

        # Extract day, month, and year from the matched groups provided by
        # ChatGPT depending on the date format
        if self.DATE_FORMAT_DAY_FIRST:
            day, month, year = map(int, match.groups())
        elif not self.DATE_FORMAT_DAY_FIRST:
            month, day, year = map(int, match.groups())

        try:
            clean_date = datetime(year, month, day)
            return clean_date

        except ValueError:
            print(f"'{date_str}' is not allowed as date.")
            return False

    def clean_amount(self, amount_str):
        """
        cleans the amount string
        Return: float, False in case of any error
        """
        # provided by ChatGPT

        try:
            # Remove spaces
            amount_str = amount_str.replace(" ", "")

            # Remove thousands separators (commas or dots followed by
            # exactly 3 digits)
            amount_str = re.sub(r'(?<=\d)[,\.](?=\d{3}(?:\D|$))', '',
                                amount_str)

            # Replace comma with dot if it's likely a decimal
            # separator (based on format)
            if ',' in amount_str and '.' in amount_str:
                if amount_str.rfind(',') > amount_str.rfind('.'):
                    # Remove thousands separator
                    amount_str = amount_str.replace(',', '')
                else:
                    # Change comma to dot for decimal separator
                    amount_str = amount_str.replace(',', '.')
            elif ',' in amount_str:
                amount_str = amount_str.replace(',', '.')

            # Convert the cleaned string to float
            clean_amount = float(amount_str)

            return clean_amount

        except ValueError:
            print(f"'{amount_str}' is not allowed as amount.")
            return False

        except Exception as e:
            print(f"\nUnexpected  error occurred: \n")
            # from https://docs.python.org/3/tutorial/errors.html:
            print(type(e))    # the exception type
            return False

    def clean_merchant(self, merchant_str):
        """
        cleans the merchant string
        Return: clean string, False in case of any error
        """
        try:
            clean_merchant = merchant_str.strip()
            clean_merchant = clean_merchant.lower()
            clean_merchant = clean_merchant.split(",")[0]
            clean_merchant = clean_merchant.split(";")[0]

            return clean_merchant

        except ValueError:
            print(f"'{merchant_str}' is not allowed as Merchant.")
            return False

        except Exception as e:
            print(f"\nUnexpected  error occurred: \n")
            # from https://docs.python.org/3/tutorial/errors.html:
            print(type(e))    # the exception type
            return False

    def sort_data(self, data, mode):
        """
        Sort the transaction data
        Creates class attribute (list of dictionaries)
        sorted_selected_raw_tx_data
        """
        if mode == "merch_date":
            # sort the data by merchant and date in reverse order
            # learned from GeeksforGeeks/w3 schools
            sorted_data = sorted(
                data,
                key=lambda x: (x[TX_MERCHANT_KEY], x[TX_DATE_KEY]),
                reverse=True
                )
        elif mode == "date":
            # sort the data date in normal order
            # learned from GeeksforGeeks/w3 schools
            sorted_data = sorted(
                data,
                key=lambda x: (x[TX_DATE_KEY]),
                reverse=False
                )

        return sorted_data

    def clean_up_tx_data(self, selected_raw_tx_data):
        """
        clean up each value row by row coverting date and value as needed
        Return: clean_tx_data
        """
        convert_error_count = 0
        clean_tx_data = []

        num_rows = len(selected_raw_tx_data)-1
        for i in range(num_rows):
            # let's check if we are within the error tolerance
            if convert_error_count >= num_rows * ERROR_TOLERANCE:
                m = f"\nMore than {ERROR_TOLERANCE*100}% errors in the data.\
                        \nPlease check the data and try again.\n"
                cprint(m, 'red')
                return False

            try:
                # clean up the date
                date_str = selected_raw_tx_data[i][TX_DATE_KEY]
                clean_date = self.clean_date(date_str)
                if not clean_date:
                    convert_error_count += 1
                    # cannot have wrong data in dates so let's
                    # skip this row
                    continue

                # clean up the amount
                amount_str = selected_raw_tx_data[i][TX_AMOUNT_KEY]
                clean_amount = self.clean_amount(amount_str)
                if not clean_amount:
                    convert_error_count += 1
                    # cannot have wrong data in amount so let's
                    # skip this row
                    continue

                # clean up the merchant
                merchant_str = selected_raw_tx_data[i][TX_MERCHANT_KEY]
                clean_merchant = self.clean_merchant(merchant_str)
                if not clean_merchant:
                    convert_error_count += 1
                    # cannot have wrong data in Merchant so let's
                    # skip this row
                    continue

                # if we end up here all data was cleaned correctly and
                # we can add it to the clean_tx_data list
                new_row = {
                    ROW_KEY: i,
                    TX_DATE_KEY: clean_date,
                    TX_MERCHANT_KEY: clean_merchant,
                    TX_AMOUNT_KEY: clean_amount
                    }

                clean_tx_data.append(new_row)

            except Exception as e:
                print(f"\nUnexpected error occurred in clean_up_tx_data: \n")
                # from https://docs.python.org/3/tutorial/errors.html:
                print(type(e))    # the exception type
                return False

        return clean_tx_data

    def get_analysis_time_frame(self, dataset):
        """
        Finds the date of the first and last transaction in the data set
        Sets class attribute ANALYSIS_START_DATE and ANALYSIS_END_DATE
        """
        sorted_dataset = self.sort_data(dataset, "date")
        dlen = len(self.clean_tx_data)-1
        self.ANALYSIS_END_DATE = sorted_dataset[dlen][TX_DATE_KEY]
        self.ANALYSIS_START_DATE = sorted_dataset[0][TX_DATE_KEY]

    def merchant_in_list(self, data_list, tx_merchant):
        """
        checks the subscription_data list to see if we already have
        an entry for this merchant. As the list works like a stack
        with LIFO and given the base list ist sorted by merchant,
        the last enry is the only relevant so we can use pop method
        to check
        Returns:
          'True' if merchant is not in the list + -1
          'False'if merchant is in the list + index of tx_merchant
          in list
        """

        try:
            tx_merchant_index = len(data_list)-1

            # let's check if the data_list is empty
            if tx_merchant_index >= 0:
                # inspiration:
                # https://docs.python.org/3/tutorial/datastructures.html
                # 5.1.1.
                last_entry_in_list = data_list[-1]
                last_merchant_in_list = last_entry_in_list[TX_MERCHANT_KEY]

                if last_merchant_in_list == tx_merchant:
                    # let's tell the calling method that we found it and what
                    # index is the last
                    return True, tx_merchant_index
                else:
                    return False, -1
            else:
                return False, -1

        except Exception as e:
            print(f"\nUnexpected  error occurred in merchant_in_list: \n")
            # from https://docs.python.org/3/tutorial/errors.html:
            print(type(e))    # the exception type
            return False, -1

    def is_subscription(self, curr_tx_date, prev_tx_date, curr_tx_amount,
                        prev_tx_amount):
        """
        checks if the recurring transaction at a merchant is to be
        considered a subscription. Subscriptions happen on or close
        to the same day +- SUBS_DAY_FLEX AND the amount is +-
        SUBS_AMOUNT_FLEX the same

        Returns:
        True: if it is a subscription
        False: if it is a another purchase at the same merchant
        """
        subs_frequency = ""

        try:
            # let's make sure we stay in the same months when comparing
            # the dates from:
            # https://www.askpython.com/python/examples/find-number-of-days-in-month
            prev_day = prev_tx_date.day
            num_days = calendar.monthrange(prev_tx_date.year,
                                           prev_tx_date.month)[1]

            if prev_day - SUBS_DAY_FLEX <= 0:
                prev_day = 1
            elif prev_day + SUBS_DAY_FLEX >= num_days:
                prev_day = num_days

            amount_within_flex = \
                (curr_tx_amount >= prev_tx_amount - SUBS_AMOUNT_FLEX) and \
                (curr_tx_amount <= prev_tx_amount + SUBS_AMOUNT_FLEX)

            day_within_flex = \
                (curr_tx_date.day >= prev_day - SUBS_DAY_FLEX) and \
                (curr_tx_date.day <= prev_day + SUBS_DAY_FLEX)

            if amount_within_flex and day_within_flex:
                days_between_tx = prev_tx_date - curr_tx_date
                monthly_within_flex = \
                    (days_between_tx.days >= 30 - SUBS_DAY_FLEX) and \
                    (days_between_tx.days <= 30 + SUBS_DAY_FLEX)

                quarterly_within_flex = \
                    (days_between_tx.days >= 91 - SUBS_DAY_FLEX) and \
                    (days_between_tx.days <= 91 + SUBS_DAY_FLEX)

                yearly_within_flex = \
                    (days_between_tx.days >= 365 - SUBS_DAY_FLEX) and \
                    (days_between_tx.days <= 365 + SUBS_DAY_FLEX)

                if monthly_within_flex:
                    subs_frequency = "monthly"

                elif quarterly_within_flex:
                    subs_frequency = "quartely"

                elif yearly_within_flex:
                    subs_frequency = "yearly"

                return True, subs_frequency
            else:
                return False, subs_frequency

        except Exception as e:
            print(f"\nUnexpected  error occurred in merchant_not_in_list: \n")
            # from https://docs.python.org/3/tutorial/errors.html:
            print(type(e))    # the exception type
            return False, -1

    def is_subs_active(self, sub_end_date):
        """
        check if the current subs is active or ended in the past
        returns: true or false
        """
        try:
            if sub_end_date.day > self.ANALYSIS_END_DATE.day:
                # if the sub_end_date day is later in the month than the
                # ANALYSIS_END_DATE need to check if the subs tx
                # happened last month
                if sub_end_date.month == self.ANALYSIS_END_DATE.month - 1:
                    return True
                else:
                    return False

            elif sub_end_date.day <= self.ANALYSIS_END_DATE.day:
                # ok if the subs was active it should have happened on or
                # before the ANALYSIS_END_DATE
                if sub_end_date.month == self.ANALYSIS_END_DATE.month:
                    return True
                else:
                    return False

        except Exception as e:
            print(f"\nUnexpected  error occurred in is_subs_active: \n")
            # from https://docs.python.org/3/tutorial/errors.html:
            print(type(e))    # the exception type
            return

    def analyze_data(self):
        """
        Analyze the transaction data
        Expects sorted list by merchant and date in reverse order
        Uses: self.sorted_clean_data as dataset
        Returns: list of dictionaries subscription_data
        """
        try:
            new_subs_list_entry = []

            # setting the baseline for the first loop. These values will be
            # updated as we go through the list and are working backwards
            # in time:
            prev_tx_merchant = self.sorted_clean_data[0][TX_MERCHANT_KEY]
            prev_tx_date = self.sorted_clean_data[0][TX_DATE_KEY]
            prev_tx_amount = round(self.sorted_clean_data[0][TX_AMOUNT_KEY], 2)
            total_sum = round(self.sorted_clean_data[0][TX_AMOUNT_KEY], 2)
            merchant_sum = round(self.sorted_clean_data[0][TX_AMOUNT_KEY], 2)
            merchant_last_amount_paid = round(self.sorted_clean_data[0]
                                              [TX_AMOUNT_KEY], 2)

            subs_active = False
            num_merchant_tx = 1

            for i in range(1, len(self.sorted_clean_data)-1):
                # let's make this loop as easy readable as possible by setting
                # readable var names
                curr_tx_merchant = self.sorted_clean_data[i][TX_MERCHANT_KEY]
                curr_tx_date = self.sorted_clean_data[i][TX_DATE_KEY]
                curr_tx_amount = self.sorted_clean_data[i][TX_AMOUNT_KEY]

                total_sum += curr_tx_amount

                # check if it is still the same merchant
                if prev_tx_merchant.lower() == curr_tx_merchant.lower():
                    # let's count how many times we shopped at that merchant
                    merchant_sum += curr_tx_amount
                    # updating the total sum for this merchant
                    num_merchant_tx += 1

                    if i == 41:
                        print("23")

                    # let's check if this merchant already exists in the
                    # subscription_data list
                    merchant_in_subs, x = self.merchant_in_list(
                        self.subscriptions_data, curr_tx_merchant)

                    is_tx_subscription, subs_frequency = self.is_subscription(
                        curr_tx_date, prev_tx_date, curr_tx_amount,
                        prev_tx_amount)
                    if is_tx_subscription:
                        # EUREKA we have ourselves a subscritpion

                        if not merchant_in_subs:
                            # ok, it's a subscription but we do not have
                            # the merchant in the subs list yet, so
                            # let's build a new entry to the subscriptions_data
                            # list

                            # let's check if the subscription was active at
                            # the end of the period of the dataset
                            subs_active = self.is_subs_active(prev_tx_date)

                            new_subs_list_entry = {
                                TX_MERCHANT_KEY: curr_tx_merchant,
                                # subscriptions should happen around
                                # same day so let's save curent tx
                                # date and update further as we work
                                # backwords in time
                                "subs_day": curr_tx_date.day,
                                # as the entries in the list get older
                                # this is the last amount paid and will
                                # not get updated
                                TX_AMOUNT_KEY: merchant_last_amount_paid,
                                # will be updated further as we work
                                # backwords in time
                                "subs_start_date": curr_tx_date,
                                # as this is the second pass at this merchant
                                # we need to take the previous tx_date as
                                # last date
                                "subs_end_date": prev_tx_date,
                                "subs_frequency": subs_frequency,
                                "subs_merchant_sum": merchant_sum,
                                "num_subs_tx": num_merchant_tx,
                                "active": subs_active
                                }
                            # let's add the merchant to the list
                            self.subscriptions_data.append(new_subs_list_entry)

                        else:
                            # merchant has already been saved to the list
                            # previously, so let's update the appropriate
                            # dictionary entry in the list with the new
                            # values. As the tx_dates get older let's
                            # update the start_date to what we know
                            # in this loop
                            self.subscriptions_data[x]["subs_start_date"] = \
                                curr_tx_date
                            # update further as we work backwords in time
                            self.subscriptions_data[x]["subs_day"] = \
                                curr_tx_date.day
                            self.subscriptions_data[x]["subs_merchant_sum"] = \
                                merchant_sum
                            self.subscriptions_data[x]["subs_frequency"] = \
                                subs_frequency
                            self.subscriptions_data[x]["num_subs_tx"] = \
                                num_merchant_tx

                    else:
                        if merchant_in_subs:
                            # ok this merchant is in subscriptions but
                            # the subscription amount has changed more
                            # then SUBS_AMOUNT_FLEX allows let's treat
                            # this as a new subscription and make a
                            # new entry in the list

                            # restartiung the  total sum for this new
                            # subscription at the merchant
                            merchant_sum = curr_tx_amount

                            # let's restart the count how many times
                            # we shopped at that merchant
                            num_merchant_tx = 1

                            new_subs_list_entry = {
                                TX_MERCHANT_KEY: curr_tx_merchant,
                                # subscriptions should happen around the
                                # same day so let's save curent tx date
                                # and update further as we work backwords
                                # in time
                                "subs_day": curr_tx_date.day,
                                # as the entries in the list get older
                                # this is the last amount paid and will
                                # not get updated
                                TX_AMOUNT_KEY: curr_tx_amount,
                                # will be updated further as we work
                                # backwords in time
                                "subs_start_date": curr_tx_date,
                                # when this entry is created we set the
                                # current date as the end-date as we go
                                # back in time through the list this will
                                # not be updated
                                "subs_end_date": curr_tx_date,
                                "subs_frequency": subs_frequency,
                                "subs_merchant_sum": merchant_sum,
                                "num_subs_tx": num_merchant_tx,
                                # as we only end up here if the subscription
                                # has changed and since we are going back in
                                # time the sub cannot be active
                                "active": False
                                    }
                            # let's add the merchant to the list
                            self.subscriptions_data.append(new_subs_list_entry)

                        else:
                            # if it is not a subscription and the current
                            # merchant is not in the subscription_data
                            # list then the merchant is recurring but
                            # not on the same/simlar day and the
                            # amounts are not the same/similar

                            # let's check if this merchant already
                            # exists in the recurring_merchant list
                            merchant_in_rec, ri = self.merchant_in_list(
                                self.recurring_merchants_data,
                                curr_tx_merchant)
                            if not merchant_in_rec:
                                # build a new entry to the subscriptions_data
                                # list
                                new_merchands_list_entry = {
                                    TX_MERCHANT_KEY: curr_tx_merchant,
                                    # as this is the second pass at this
                                    # merchant we need to take the previous
                                    # tx_date as last date
                                    "last_tx_date": prev_tx_date,
                                    "first_tx_date": curr_tx_date,
                                    "last_tx_amount":
                                    merchant_last_amount_paid,
                                    "merchant_sum": merchant_sum,
                                    "num_tx": num_merchant_tx
                                    }

                                # let's add the merchant to the list
                                self.recurring_merchants_data.append(
                                    new_merchands_list_entry)

                            else:
                                # merchant has already been saved to the
                                # list previously, so let's update the
                                # appropriate entry in the list with the
                                # new values as we go back in time.
                                f_date = "first_tx_date"
                                self.recurring_merchants_data[ri][f_date] = \
                                    curr_tx_date
                                m_sum = "merchant_sum"
                                self.recurring_merchants_data[ri][m_sum] = \
                                    merchant_sum
                                self.recurring_merchants_data[ri]["num_tx"] = \
                                    num_merchant_tx

                else:
                    # new merchant
                    # let's reset the counters
                    merchant_sum = curr_tx_amount
                    num_merchant_tx = 1
                    merchant_last_amount_paid = round(
                        self.sorted_clean_data[i][TX_AMOUNT_KEY], 2)

                    # let's reset merchant_in_subs as the current murchant
                    # was in rec
                    merchant_in_subs = False

                # Let's make the current the previous before the next loop
                prev_tx_merchant = curr_tx_merchant
                prev_tx_amount = curr_tx_amount
                prev_tx_date = curr_tx_date

            return self.subscriptions_data, self.recurring_merchants_data

        except Exception as e:
            print(f"\nUnexpected  error occurred in analyze_data: \n")
            # from https://docs.python.org/3/tutorial/errors.html:
            print(type(e))  # the exception type
            return


def main():
    """
    Run the main program
    """
    mode = intro_go_on()

    if not mode:
        print("Goodbye!")
        return

    elif mode == 1:
        clean_console()

        user_email = get_user_email()
        print(user_email)

        SHEET = create_spreadsheet(user_email)
        print(f"\nSuccessfully created Google Spreadsheet: '{SHEET.title}'\n")
        print("Google has sent you a link the Spreadsheet. Alternativly,\n")
        print("you can access your worksheet at the following link:\n")
        print(SHEET.url)
        cprint("\nIMPORTANT! Please use right mouse click and \
               \ncopy/past from there!\n", 'light_cyan')

        wait_for_user("Have you opened the Google Sheet? (y/n): ")

    elif mode == 2:
        clean_console()

        SHEET = get_existing_spreadsheet()
        print(f"RET has successfully opened the Google \
              Spreadsheet: {SHEET.title}.\n")

    clean_console()

    # regardless if user created a new sheet or re-used on, we  we are now
    # ready to ask the user to import the CSV file
    RAW_DATA_WSHEET = get_imported_csv_wsheet(SHEET)
    print(f"\nRET succesfully connected to your Google Worksheet: \
          \n{RAW_DATA_WSHEET.title}.\n")

    # let's instantiate the class as we need it's methods now
    tx_data = TxData()

    clean_data = check_import_raw_data(RAW_DATA_WSHEET, tx_data)
    if not clean_data:
        cprint("Transaction Data you provided could not be processed. \
               \nGoood buy!", 'red')
        return

    clean_console()

    # sort the cleaned data
    print("Sorting the cleaned transaction data...")
    tx_data.sorted_clean_data = tx_data.sort_data(tx_data.clean_tx_data,
                                                  "merch_date")

    # finding start and end date of dataset
    tx_data.get_analysis_time_frame(tx_data.clean_tx_data)

    (tx_data.subscriptions_data,
        tx_data.recurring_merchants_data) = tx_data.analyze_data()

    # upload the analysis result data to a new worksheet
    if not upload_results_to_worksheet(SHEET, "ANALYSIS RESULTS",
                                       "SUBSCRIPTIONS",
                                       tx_data.subscriptions_data,
                                       "MERCHANT WITH MULTIPLE PURCHASES",
                                       tx_data.recurring_merchants_data,
                                       tx_data.ANALYSIS_START_DATE,
                                       tx_data.ANALYSIS_END_DATE):
        print("\nan error occurred while uploading the data to the \
              \nGoogle Sheet.")


main()
