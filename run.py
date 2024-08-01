import gspread
from google.oauth2.service_account import Credentials


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
    print("the RET will use Google Sheets to import your CSV files and store the data.\n")
    print("Let's get started!\n\n")

    go_on = input("Do you want to continue? Press Enter to continue; anything else to abort...")
    if go_on == "":
        return True
    else:
        return False

def get_user_email():
    """
    Get user email from the user
    """
    user_email = input("Enter your email address: ")
    return user_email

def main():
    """
    Run the main program
    """
    if intro_go_on():
        user_email = get_user_email()
        print(user_email)
    else:
        print("Goodbye!")
        return

main()

#SHEET = GSPREAD_CLIENT.create(SHEET_NAME)