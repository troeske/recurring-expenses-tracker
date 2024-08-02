import gspread
from google.oauth2.service_account import Credentials
import re


SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

# love sandwiches example used as baseline
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
    print("Let's get started!\n\n")

    go_on = input("Do you want to continue? \
                  \nPress: \
                  \n1 to create a new Spreadsheet \
                  \n2 for re-using one previsously created through RET \
                  \n\nAny other key to EXIT:\n")

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

def create_worksheet(user_email):
    """
    Create a new worksheet for the user and share it with the user and RET
    Note: RET is owner and the user is editor. Later versions should make user owner
    """

    print("\nRET is creating a new worksheet for you...")
    try:
        SHEET = GSPREAD_CLIENT.create(SHEET_NAME)
        SHEET.share(user_email, perm_type='user', role='writer')

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please try again later.")
        return
    
    print("Worksheet created successfully!\n")
    print("You can access your worksheet at the following link:\n")
    print(SHEET.url)

def open_existing_worksheet():
    """
    Open an a worksheet that was created through RET
    """

    existing_ws = input("Please enter the URL of the worksheet you want to open: \n")

    try:
        SHEET = GSPREAD_CLIENT.open_by_url(existing_ws.strip())

    except Exception as e:
        print(f"\nAn error occurred: {e}")
        return False
    
    print(f"\nSuccessfully accessed Google Sheet: {SHEET.title}")
    return True


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

        create_worksheet(user_email)
        # we need to handle error case if worksheet is not created

    elif mode == 2:
        
        while not open_existing_worksheet():
            print("The URL you entered is not a valid Google Sheet. Please try again.\n")
        
        


    else:
        return
        
    

main()