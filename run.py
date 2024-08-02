import gspread
from gspread.exceptions import SpreadsheetNotFound, GSpreadException, APIError
from google.oauth2.service_account import Credentials
from datetime import datetime


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


def intro_go_on():
    """
    Display the intro message
    """
    print("\nWelcome to the Recurring Expense Tracker: RET!\n")
    print("You can import your bank account and/or credit card transaction data into RET.")
    print("RET will sort through all the transaction data and provide you with")
    print("a list of recurring expenses and subscriptions.\n")
    print("To provide a platform for you to manage your recurring expenses,")
    print("RET will use Google Sheets to let you import your CSV files and")
    print("provide the output for you as well.\n")
    print("If you like, RET can create a new Google Spreadsheet and share it with you.")
    print("If you already have one please select option 2. below.\n")
    print("Let's get started!\n")

    go_on = input("Do you want to continue? \
                  \nPress: \
                  \n1 to create a new Spreadsheet \
                  \n2 for re-using one previsously created (through RET or by you) \
                  \nAny other key to EXIT:\n")

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
   
    print("\n")

    user_email = input("Enter your email address: ")
    while not validate_email(user_email):
        print("The email address you entered is not a valid email address. Please try again.")
        user_email = input("Enter your email address:\n")

    return user_email

def validate_email(email):
    """
    Make sure that email is a valid email address. Function provided by Github Copilot
    """
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if re.match(pattern, email):
        return True
    else:
        return False

def create_spreadsheet(user_email):
    """
    Create a new worksheet for the user and share it with the user and RET
    Note: RET is owner and the user is editor. Later versions should make user owner
    Return: the Spreadsheet object that RET created for the user
    """

    print("\nRET is creating a new worksheet for you...")
    try:
        spreadsheet = GSPREAD_CLIENT.create(SHEET_NAME)
        spreadsheet.share(user_email, perm_type='user', role='writer')

    except Exception as e:
        print(f"An error occurred: {e}")
        #from https://docs.python.org/3/tutorial/errors.html:
        print(type(e))    # the exception type
        print("Please try again later.")
        return False
    
    return spreadsheet

def get_existing_spreadsheet():
    """
    Open an a spreadsheet that was created through RET
    Return: the Spreadsheet object that the user wants to open
    """
    existing_ssheet = input("Please enter the URL of the Spreadsheet you want to open: \n")
    
    #loop as long user entered empty string
    while existing_ssheet =="":
        existing_ssheet = input("Please enter the URL of the Spreadsheet you want to open: \n")
    
    #let's try to open the spreadsheet
    spreadsheet = open_existing_spreadsheet(existing_ssheet)
    while not spreadsheet:
        #seems user input isn't correct, so let's ask again
        existing_ssheet = input("Please enter the URL of the Spreadsheet you want to open: \n")
        spreadsheet = open_existing_spreadsheet(existing_ssheet)
    
    #all good now so let's return the worksheet
    return spreadsheet

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
        #requested help from Copilot
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
                \nYou can add RET as an editor to the spreadsheet.\
                \nClick Share on the upper right corner of the Google Sheet and add:\
                \n\n{CREDS.service_account_email}\
                \n\nPlease select 'Editor' and uncheck: 'Notify people'\
                \nThen try again.")
        return False

    except Exception as e:
        print(f"\nUnexpected  error occurred: \n")
        #from https://docs.python.org/3/tutorial/errors.html:
        print(type(e))    # the exception type
        
        return False
    
    return spreadsheet

def wait_for_user(display_text):
    """
    display text with y/n option
    Wait for the user until he/she presses 'y' 
    """
    response = input(f"\n{display_text}")

    while response == "n":
        response = input(f"{display_text}")
    
    print("\nGreat! Let's move on to the next step.\n")

def continue_RET():
    """
    ask user if she/he wants to continue or exit the program
    """
    response = input("\nDo you want to continue with this Recurring Expense Tracker? (y/n): ")
    if response == "y":
        return True
    else:
        print("Goodbye!")
        return False
    

def get_imported_csv_wsheet(spreadsheet):
    """
    prompts the user to import  the CSV file to a Google Worksheet and privde it's name
    returns: the worksheet that the user imported the CSV file to
    """
    print(f"\nNow, please imnport your CSV file to the Google Sheet: '{spreadsheet.title}' RET just created or opened.")
    print("You can do this by clicking on the 'File' menu in the Google Sheet and selecting 'Import'.")
    
    wait_for_user("Have you imported the CSV file to the Google Sheet? (y/n): ")

    ws_name = input("Please enter the worksheet name where you imported the CSV file. \
    \nYou can do this by double-clicking on the Sheet Name (e.g. 'Sheet1') in footer of the Spreadsheet\n")
    
    #loop as long user entered empty string
    while ws_name =="":
        ws_name = input("Please enter the worksheet name where you imported the CSV file: \n")
    
    #let's try to select the worksheet
    worksheet = select_imported_csv_wsheet(spreadsheet, ws_name)
    while not worksheet:
        #seems user input isn't correct, so let's ask again
        ws_name = input("Please enter the worksheet name where you imported the CSV file: \n")
        worksheet = select_imported_csv_wsheet(spreadsheet, ws_name)
    
    #all good now so let's return the worksheet
    return worksheet


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
        #from https://docs.python.org/3/tutorial/errors.html:
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
    Convert a spreadsheet column letter (e.g., 'A', 'B', 'Q') to its respective number value.
    Supports multi-letter columns (e.g., 'AA', 'AB').
    Returns: list of selected columns as numbers. Calling function must subtract 1 to get zero-based index.
    """

    #let's check if column_letter already is an integer
    try:
        column_number = int(column_letter)
    
    except ValueError:
        #Provided by Copilot:
        column_letter = column_letter.upper()
        column_number = 0
        for char in column_letter:
            column_number = column_number * 26 + (ord(char) - ord('A') + 1)

    #let's make some some common sense checking in the value could right 
    try:
        if column_number < 1:
            print(f"The column number is {str(column_number)}. It cannot be less than 1.")
            return False
        elif column_number > MAX_COL_NUMBER:
            print("The column number is {str(column_number)}. It cannot be higher then 50")
            return False
        else:
            #print(f"Column Number is: {str(column_number)}.")
            return column_number
    
    except Exception as e:
        print(f"\nUnexpected  error occurred: \n")
        #from https://docs.python.org/3/tutorial/errors.html:
        print(type(e))    # the exception type
        return False

def import_raw_data(raw_data_wsheet):
    """
    Import the raw transaction data from the worksheet where the user imported his/her CSV file into a list of lists
    Return: the list of lists with the raw transaction data 
    """

    #let's start with the row where the transaction data starts
    input_message = "\nPlease enter the row number \nwhere the transaction data starts (e.g. 1, 2, 3, etc.):\n"
    start_row = get_int(input_message)
    while not start_row:
        start_row = get_int(input_message)
    
    #now the columns for tx_date, tx_merchant, and tx_amount
    #let's start with the transaction date column
    message= "\nPlease enter the column letter where the \ntransaction date is located \n(e.g. A, B, C, etc.):\n"
    tx_date_col = column_letter_to_number(input(message))
    while not tx_date_col:
        tx_date_col = column_letter_to_number(input(message))
    
    #we need to subtract 1 to get the zero-based index
    tx_date_col -= 1

    #now the merchant column
    message= "\nPlease enter the column letter where the \nmerchant/recipient is located (e.g. A, B, C, etc.):\n"
    tx_merchant_col = column_letter_to_number(input(message))
    while not tx_merchant_col:
        tx_merchant_col = column_letter_to_number(input(message))
    
    #we need to subtract 1 to get the zero-based index
    tx_merchant_col -= 1

    # now the amount column
    message= "\nPlease enter the column letter where the \ntransaction amount is located (e.g. A, B, C, etc.):\n"
    tx_amount_col = column_letter_to_number(input(message))
    while not tx_amount_col:
        tx_amount_col = column_letter_to_number(input(message))
     
    #we need to subtract 1 to get the zero-based index
    tx_amount_col -= 1


    print(f"\nTHANK YOU!\nRET is now importing your raw transaction data from the worksheet: \n{raw_data_wsheet.title}.\n")
    print("This may take a few seconds depending on the size of the data.\n")
    print("Please wait...\n")

    raw_tx_data = raw_data_wsheet.get_all_values()
    
    #we need to loop through the list of lists and extract the rows and columns that the user specified and create a list of dfictionaries
    selected_tx_data = []

    for i in range(int(start_row)-1, len(raw_tx_data)):
        #check if any cell is empty
        if raw_tx_data[i][tx_date_col].strip() == "" or raw_tx_data[i][tx_merchant_col].strip() == "" or raw_tx_data[i][tx_amount_col].strip() == "":
            continue

        new_row = {
                    ROW_KEY: i, 
                    TX_DATE_KEY: raw_tx_data[i][tx_date_col], 
                    TX_MERCHANT_KEY: raw_tx_data[i][tx_merchant_col],
                    TX_AMOUNT_KEY: raw_tx_data[i][tx_amount_col] 
                    } 

        selected_tx_data.append(new_row)

    return selected_tx_data

def do_you_want_to_continue(message):
    """
    Ask the user if she/he wants to continue
    """
    response = input(message)
    
    if response == "y":
        return True
    else:
        return False
    
def sort_key(d):
    """
    Return the key for sorting the data
    """
    return (d['tx_merchant'], datetime.strptime(d['tx_date'], '%d.%m.%Y'))
    
class TxData:
    """
    Class to handle all aspects of the transaction data incl: clean_up and analysis
    Input: list of dictionaries: selected_raw_tx_data
    Return: Class object
    """

    def __init__(self, selected_raw_tx_data):
        self.selected_raw_tx_data = selected_raw_tx_data

        self.sorted_selected_raw_data = []
    
    def sort_data(self):
        """
        Sort the transaction data
        Creates sorted_selected_raw_tx_data
        """
        #sort the data by merchant and date, learned from GeeksforGeeks
        self.sorted_selected_raw_data = sorted(
            self.selected_raw_tx_data,
            key=lambda x: (x[TX_MERCHANT_KEY], x[TX_DATE_KEY])
            )

        
    def print_data(self, number_of_rows, sorted):
        """
        Print the first number_of_rows of the transaction data
        If sorted use the sorted data, otherwise use the selected_raw_data
        """
        for i in range(number_of_rows):
            if sorted:
                print(self.sorted_selected_raw_data[i])
            elif not sorted:
                print(self.selected_raw_tx_data[i])


    def analyze_data(self):
        """
        Analyze the transaction data
        """


def main():
    """
    Run the main program
    """
    mode = intro_go_on()

    if not mode:
        print("Goodbye!")
        return
    
    elif mode == 1:    
        user_email = get_user_email()
        print(user_email)

        SHEET = create_spreadsheet(user_email)
        print(f"\nSuccessfully created Google Spreadsheet: {SHEET.title}\n")
        print("You can access your worksheet at the following link:\n")
        print(SHEET.url)

    elif mode == 2:
        SHEET = get_existing_spreadsheet()
        print(f"Great! We have successfully opened the Google Spreadsheet: {SHEET.title}.\n")

    
    # regardless if user created a new sheet or re-used on, we  we are now ready to ask the user to import the CSV file    
    RAW_DATA_WSHEET = get_imported_csv_wsheet(SHEET)
    print(f"Great! RET connected to your Google Worksheet: {RAW_DATA_WSHEET.title}.\n")

    #import raw transaction data from the worksheet
    selected_raw_tx_data = []
    selected_raw_tx_data = import_raw_data(RAW_DATA_WSHEET)
    print("The raw transaction data has been successfully imported.\n")
    
    #let's start the data analysis
    #instantiate the class
    tx_data = TxData(selected_raw_tx_data)

    print("Here are the first 5 records:\n")
    tx_data.print_data(5, False)
    
    message = "\nDoes the data look right and doyou want to continue? (y/n):\n"
    if not do_you_want_to_continue(message):
        print("Goodbye!")
        return
    
    #sort the raw data
    tx_data.sort_data()
    tx_data.print_data(50, True)





main()