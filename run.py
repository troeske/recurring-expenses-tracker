import gspread
from gspread.exceptions import SpreadsheetNotFound, GSpreadException, APIError
from google.oauth2.service_account import Credentials
import re

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


def intro_go_on():
    """
    Display the intro message
    """
    print("\nWelcome to the Recurring Expense Tracker - RET!\n")
    print("This program helps you keep track of your recurring expenses.")
    print("You can import your bank account and/or credit card transaction data.")
    print("This program will sort through all the transaction data and provide you with")
    print("a list of recurring expenses and subscriptions.\n")
    print("To provide an platform for you to manage your recurring expenses,")
    print("the RET will use Google Sheets to import your CSV files and provide the output for you as well.\n")
    print("To use a Google Spreadsheet that you already created please select option 2. below\n")
    print("Let's get started!\n\n")

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
                \n\nThen try again.")
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
    handles the import prompting of the user to import  the CSV file to the Google Sheet
    returns: the worksheet that the user imported the CSV file to
    """
    print(f"\nNow, please imnport your CSV file to the Google Sheet: '{spreadsheet.title}' RET just created or opened.")
    print("You can do this by clicking on the 'File' menu in the Google Sheet and selecting 'Import'.")
    
    wait_for_user("Have you imported the CSV file to the Google Sheet? (y/n): ")

    ws_name = input("Please enter the worksheet name where you imported the CSV file. \
    \nYou can do this by double-clicking on the Sheet Name in footer of the Spreadsheet\n")
    
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
    IMPORT_W_SHEET = get_imported_csv_wsheet(SHEET)
    print(f"Great! You have successfully imported the CSV file to the Google Sheet: {IMPORT_W_SHEET.title}.\n")
    

main()