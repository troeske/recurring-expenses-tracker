import gspread
from gspread.exceptions import SpreadsheetNotFound, GSpreadException, APIError
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil import parser
import re
import os



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
INPUT_DATA_ERROR_TOLERANCE = 0.1


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
    print(f"\nNow, please imnport your CSV file to the Google Sheet: '{spreadsheet.title}', RET just created or opened.")
    print("You can do this by clicking on the 'File' menu in the Google Sheet and selecting 'Import'.")
    
    wait_for_user("Have you imported the CSV file to the Google Sheet? (y/n): ")

    ws_name = input("Please enter the worksheet name where you imported the CSV file.\
    You can do this by double-clicking on the Sheet Name (e.g. 'Sheet1') in footer of the Spreadsheet\n")
    
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


    print(f"\nTHANK YOU! RET is now importing your raw transaction data from the worksheet: \n{raw_data_wsheet.title}.")
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

def clean_console():
    """
    cleans the console window.
    copied from: https://www.sololearn.com/en/Discuss/3220821/how-how-to-delete-printed-text
    """

    os.system('cls' if os.name == 'nt' else 'clear')

def upload_data_to_worksheet(spreadsheet, worksheet_name, data):
    """
    create a new worksheet with worksheet_name in spreadsheet and
    upload the data to the selected worksheet
    """
    print("starting the data upload to Google Sheets...")

    try:
        print("creating new worksheet...")
        # creating the worksheet
        ws_output = spreadsheet.add_worksheet(title=worksheet_name, rows=1, cols=10)
        
        print("uploading the data...")
        # filling in the data

        # first the headings
        ws_output.insert_row(["Original Row",TX_DATE_KEY, TX_MERCHANT_KEY, TX_AMOUNT_KEY], 1)

        # then the data
        for row in data:
            ws_output.append_row([row[ROW_KEY], row[TX_DATE_KEY], row[TX_MERCHANT_KEY], row[TX_AMOUNT_KEY]])
        
        
        print(f"The data has been successfully uploaded to:\nSpreadsheet: {spreadsheet.title} worksheet: {worksheet_name}.")
    
    except APIError as e:
        if e.response.status_code == 400:
            print(f"\nA worksheet with the name '{worksheet_name}' already exists in the spreadsheet: {spreadsheet.title}.")
            
        else:
            print(f"\nAn API error occurred: {e}")
        print(f"\nAn API error occurred: {e}")
        print(f"Status Code: {e.response.status_code}")
        print(f"Error Message: {e.response.text}")
        return False
    
    except GSpreadException as e:
        print(f"\nAn error occurred trying to access the spreadsheet: {e}")
        return
    
    except Exception as e:
        print(f"\nUnexpected  error occurred: \n")
        #from https://docs.python.org/3/tutorial/errors.html:
        print(type(e))    # the exception type
        return False

#################################################################
# CLASS TxData                                                  #
#################################################################
class TxData:
    """
    Class to handle all aspects of the transaction data incl: clean_up and analysis
    Input: list of dictionaries: selected_raw_tx_data
    """

    def __init__(self, selected_raw_tx_data):
        self.selected_raw_tx_data = selected_raw_tx_data

        self.sorted_clean_data = []
        self.clean_tx_data = []
        #self.selected_raw_tx_data = []
    
    def clean_date(self, date_str):
        """
        cleans the date string 
        Return: datetime object, False in case of any error
        Inspired by: https://blog.finxter.com/5-effective-ways-to-check-if-a-string-can-be-converted-to-a-datetime-in-python/
        """
        try:
            clean_date = parser.parse(date_str)
            return clean_date
            
        
        except ValueError:
            print(f"{date_str} is not in the right format.")
            return False

    def clean_amount(self, amount_str):
        """
        cleans the amount string
        Return: float, False in case of any error
        Inspired by ChatGPT
        """
        try:
            # Remove spaces
            amount_str = amount_str.replace(" ", "")
        
            # Remove thousands separators (commas or dots followed by exactly 3 digits)
            amount_str = re.sub(r'(?<=\d)[,\.](?=\d{3}(?:\D|$))', '', amount_str)
            
            # Replace comma with dot if it's likely a decimal separator (based on format)
            if ',' in amount_str and '.' in amount_str:
                if amount_str.rfind(',') > amount_str.rfind('.'):
                    amount_str = amount_str.replace(',', '')  # Remove thousands separator
                else:
                    amount_str = amount_str.replace(',', '.')  # Change comma to dot for decimal separator
            elif ',' in amount_str:
                amount_str = amount_str.replace(',', '.')
            
            # Convert the cleaned string to float
            clean_amount = float(amount_str)
            
            return clean_amount
        
        except ValueError:
            print(f"{amount_str} is not in the right format.")
            return False
        
        except Exception as e:
            print(f"\nUnexpected  error occurred: \n")
            #from https://docs.python.org/3/tutorial/errors.html:
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
            print(f"{merchant_str} is not in the right format.")
            return False
        
        except Exception as e:
            print(f"\nUnexpected  error occurred: \n")
            #from https://docs.python.org/3/tutorial/errors.html:
            print(type(e))    # the exception type
            return False

    def clean_up_tx_data(self):
        """
        clean up each value row by row coverting date and value as needed
        Return: clean_tx_data
        """
        convert_error_count = 0
        num_rows = len(self.selected_raw_tx_data)
        for i in range(num_rows):
            #clean up the date
            date_str = self.selected_raw_tx_data[i][TX_DATE_KEY]
            clean_date = self.clean_date(date_str)
            convert_error_count += 1 if not clean_date else 0
      
            
            #clean up the amount
            amount_str = self.selected_raw_tx_data[i][TX_AMOUNT_KEY]
            clean_amount = self.clean_amount(amount_str)
            convert_error_count += 1 if not clean_amount else 0

            #clean up the merchant
            merchant_str = self.selected_raw_tx_data[i][TX_MERCHANT_KEY]
            clean_merchant = self.clean_merchant(merchant_str)
            convert_error_count += 1 if not clean_merchant else 0

            #let's check if we are within the error tolerance
            if convert_error_count < num_rows * INPUT_DATA_ERROR_TOLERANCE:
                new_row = {
                    ROW_KEY: i, 
                    TX_DATE_KEY: clean_date, 
                    TX_MERCHANT_KEY: clean_merchant,
                    TX_AMOUNT_KEY: clean_amount 
                    } 

                self.clean_tx_data.append(new_row)
            else:
                print(f"Too many errors in the data. Please check the data and try again.")
                return False


    
    def sort_data(self, data):
        """
        Sort the transaction data
        Creates sorted_selected_raw_tx_data
        """
        #sort the data by merchant and date, learned from GeeksforGeeks
        sorted_data = sorted(
            data,
            key=lambda x: (x[TX_MERCHANT_KEY], x[TX_DATE_KEY])
            )
        
        return sorted_data

        
    def print_data(self, number_of_rows, what_data, clean):
        """
        Print the provided number_of_rows of the data requested
        In case 0 is provided, print all rows
        What_data selects what to print: raw, clean, sorted
        """
        if clean: clean_console()
        
        print(f"Here is the {what_data} data:\n")
        
        try:
            if what_data == "raw":
                if number_of_rows == 0:
                    number_of_rows = len(self.selected_raw_tx_data)

            elif what_data == "clean":
                if number_of_rows == 0:
                    number_of_rows = len(self.clean_tx_data)
            
            elif what_data == "sorted":
                if number_of_rows == 0:
                    number_of_rows = len(self.sorted_clean_data)
            
            else:
                print("print mode not supported\n")
                return
        

            for i in range(number_of_rows):
                if what_data == "raw":
                    print(f"{self.selected_raw_tx_data[i][ROW_KEY]} | {self.selected_raw_tx_data[i][TX_DATE_KEY]} | {self.selected_raw_tx_data[i][TX_MERCHANT_KEY]} | {self.selected_raw_tx_data[i][TX_AMOUNT_KEY]}")

                elif what_data == "clean":
                    print(f"{self.clean_tx_data[i][TX_DATE_KEY]} | {self.clean_tx_data[i][TX_DATE_KEY].day} | {self.clean_tx_data[i][TX_MERCHANT_KEY]} | {self.clean_tx_data[i][TX_AMOUNT_KEY]}")
                
                elif what_data == "sorted":
                    print(f"{self.sorted_clean_data[i][TX_DATE_KEY]} | {self.sorted_clean_data[i][TX_DATE_KEY].day} | {self.sorted_clean_data[i][TX_MERCHANT_KEY]} | {self.sorted_clean_data[i][TX_AMOUNT_KEY]}")
        
        except Exception as e:
           print(f"\nUnexpected  error occurred: \n")
           #from https://docs.python.org/3/tutorial/errors.html:
           print(type(e))    # the exception type
           return False 


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

    clean_console()

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

    tx_data.print_data(10, "raw", True)
    message = "\nDoes the data look right and do you want to continue? (y/n):\n"
    if not do_you_want_to_continue(message):
        print("Goodbye!")
        return
    
    #clean up the tx data row by row
    print("Cleaning up the transaction data...")
    tx_data.clean_up_tx_data()

    #sort the raw data
    print("Sorting the transaction data...")
    tx_data.sorted_clean_data = tx_data.sort_data(tx_data.clean_tx_data)
    #tx_data.print_data(0, "sorted", True)

    #upload the data to the worksheet
    if not upload_data_to_worksheet(SHEET, "SORTED TX DATA", tx_data.sorted_clean_data):
        print("an error occurred while uploading the data to the Google Sheet.")
    







main()