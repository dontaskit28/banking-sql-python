import datetime
import mysql.connector

host = "localhost"
user = "root"
password = "q1w2e3r4"
database = "bank"

# Establish a connection to the MySQL database
cnx = mysql.connector.connect(host=host, user=user, passwd=password)

# Get a cursor object
cursor = cnx.cursor()


# Check if the database exists
def database_exists(name):
    cursor.execute("SHOW DATABASES")
    for x in cursor:
        if x[0] == name:
            return True
    return False


# Function to create a new database
def create_database():
    # if the database already exists, exit the function
    if database_exists("bank"):
        print("Database already exists!")
        return

    # Create a new database
    cursor.execute("CREATE DATABASE IF NOT EXISTS bank")
    cursor.execute("USE bank")

    # Create the Customers table
    create_customers_table_query = """
    CREATE TABLE Customers (
        customer_id INT PRIMARY KEY AUTO_INCREMENT,
        name VARCHAR(255) NOT NULL,
        date_of_birth DATE NOT NULL,
        address VARCHAR(255) NOT NULL,
        contact_number VARCHAR(20) NOT NULL,
        email VARCHAR(255) NOT NULL,
        occupation VARCHAR(255) NOT NULL
    )
    """
    cursor.execute(create_customers_table_query)

    # Create the Accounts table
    create_accounts_table_query = """
    CREATE TABLE Accounts (
        account_id INT PRIMARY KEY AUTO_INCREMENT,
        customer_id INT NOT NULL,
        account_type VARCHAR(50) NOT NULL,
        balance DECIMAL(10,2) NOT NULL,
        created_date DATE NOT NULL,
        last_transaction_date DATE NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES Customers (customer_id)
    )
    """
    cursor.execute(create_accounts_table_query)

    # Create the Transactions table
    create_transactions_table_query = """
    CREATE TABLE Transactions (
        transaction_id INT PRIMARY KEY AUTO_INCREMENT,
        account_id INT NOT NULL,
        transaction_type VARCHAR(50) NOT NULL,
        amount DECIMAL(10,2) NOT NULL,
        transaction_date DATE NOT NULL,
        description VARCHAR(255),
        FOREIGN KEY (account_id) REFERENCES Accounts (account_id)
    )
    """
    cursor.execute(create_transactions_table_query)

    # Create the Loans table
    create_loans_table_query = """
    CREATE TABLE Loans (
        loan_id INT PRIMARY KEY AUTO_INCREMENT,
        account_id INT NOT NULL,
        loan_amount DECIMAL(10,2) NOT NULL,
        interest_rate DECIMAL(5,2) NOT NULL,
        start_date DATE NOT NULL,
        end_date DATE NOT NULL,
        FOREIGN KEY (account_id) REFERENCES Accounts (account_id)
    )
    """
    cursor.execute(create_loans_table_query)

    # Create the Cards table
    create_cards_table_query = """
    CREATE TABLE Cards (
        card_id INT PRIMARY KEY AUTO_INCREMENT,
        account_id INT NOT NULL,
        card_number VARCHAR(16) NOT NULL,
        card_type VARCHAR(50) NOT NULL,
        expiration_date DATE NOT NULL,
        cvv VARCHAR(3) NOT NULL,
        FOREIGN KEY (account_id) REFERENCES Accounts (account_id)
    )
    """
    cursor.execute(create_cards_table_query)

    # Commit the changes to the database
    cnx.commit()

    print("Tables created successfully!")


# Function to create a new customer account
def create_customer_account(
    name, date_of_birth, address, contact_number, email, occupation
):
    cnx = mysql.connector.connect(
        host=host, user=user, passwd=password, database=database
    )
    cursor = cnx.cursor()

    # Insert a new record into the Customers table
    insert_customer_query = "INSERT INTO Customers (name, date_of_birth, address, contact_number, email, occupation) VALUES (%s, %s, %s, %s, %s, %s)"
    customer_data = (name, date_of_birth, address, contact_number, email, occupation)
    cursor.execute(insert_customer_query, customer_data)
    cnx.commit()

    # Retrieve the generated customer ID
    customer_id = cursor.lastrowid

    # Insert a new record into the Accounts table
    insert_account_query = "INSERT INTO Accounts (customer_id, account_type, balance,created_date,last_transaction_date) VALUES (%s, %s, %s, %s, %s)"
    # Check-in account with initial balance of $30
    account_data = (
        customer_id,
        "Checkin",
        30.0,
        datetime.date.today(),
        datetime.date.today(),
    )
    cursor.execute(insert_account_query, account_data)
    cnx.commit()

    # Retrieve the generated account ID
    account_id = cursor.lastrowid

    # Insert a new record into the Accounts table for Savings account
    # Savings account with initial balance of $30
    account_data = (
        customer_id,
        "Savings",
        30.0,
        datetime.date.today(),
        datetime.date.today(),
    )
    cursor.execute(insert_account_query, account_data)
    cnx.commit()

    # Confirmation message
    print("New customer account created successfully!")
    print("Customer ID:", customer_id)
    print("Account ID (Checkin):", account_id)
    print("Account ID (Savings):", cursor.lastrowid)

    # Close the connection
    cnx.close()


def make_withdrawal(account_id, withdrawal_amount):
    # Establish a connection to the MySQL server
    cnx = mysql.connector.connect(
        host=host, user=user, passwd=password, database=database
    )

    # Create a cursor object to execute SQL queries
    cursor = cnx.cursor()

    # Check the account balance
    balance_query = (
        "SELECT balance, account_type, customer_id FROM Accounts WHERE account_id = %s"
    )
    cursor.execute(balance_query, (account_id,))
    account_data = cursor.fetchone()

    if account_data is None:
        print("Account not found.")
    else:
        account_balance, account_type, customer_id = account_data

        if account_balance >= withdrawal_amount:
            # Sufficient balance in the account
            update_balance_query = (
                "UPDATE Accounts SET balance = balance - %s WHERE account_id = %s"
            )
            cursor.execute(update_balance_query, (withdrawal_amount, account_id))
            cnx.commit()
            insert_transaction_query = "INSERT INTO Transactions (account_id, transaction_type, amount,transaction_date) VALUES (%s, %s, %s,%s)"
            source_transaction_data = (
                account_id,
                "Withdrawal",
                -withdrawal_amount,
                datetime.datetime.today(),
            )
            cursor.execute(insert_transaction_query, source_transaction_data)
            cnx.commit()
            print(
                "Withdrawal successful. Your new balance is:",
                account_balance - withdrawal_amount,
            )
        elif account_type == "Checkin":
            # Insufficient balance in the check-in account, check the associated savings account
            savings_balance_query = "SELECT balance,account_id FROM Accounts WHERE account_type = 'Savings' AND customer_id = %s"
            cursor.execute(savings_balance_query, (customer_id,))
            savings_balance = cursor.fetchone()

            if savings_balance is None:
                print("Savings account not found.")
            elif savings_balance[0] >= withdrawal_amount:
                # Sufficient balance in the savings account
                update_savings_balance_query = (
                    "UPDATE Accounts SET balance = balance - %s WHERE account_id = %s"
                )

                cursor.execute(
                    update_savings_balance_query,
                    (withdrawal_amount, savings_balance[1]),
                )
                cnx.commit()
                insert_transaction_query = "INSERT INTO Transactions (account_id, transaction_type, amount,transaction_date) VALUES (%s, %s, %s,%s)"
                source_transaction_data = (
                    savings_balance[1],
                    "Withdrawal",
                    -withdrawal_amount,
                    datetime.datetime.today(),
                )
                cursor.execute(insert_transaction_query, source_transaction_data)
                cnx.commit()
                print(
                    "Withdrawal successful from the savings account. Your new balance is:",
                    savings_balance[0] - withdrawal_amount,
                )
            else:
                print(
                    "Insufficient funds in both the check-in and savings accounts. Withdrawal failed."
                )
        else:
            print("Insufficient funds in the account. Withdrawal failed.")

    # Close the cursor and database connection
    cursor.close()
    cnx.close()


# Function to check the account balance
def check_account_balance(account_id):
    cnx = mysql.connector.connect(
        host=host, user=user, passwd=password, database=database
    )
    cursor = cnx.cursor()

    # Retrieve the account balance from the Accounts table
    select_balance_query = "SELECT balance FROM Accounts WHERE account_id = %s"
    cursor.execute(select_balance_query, (account_id,))
    query_result = cursor.fetchone()
    if cursor.rowcount < 1:
        print("Account does not exist.")
        return
    else:
        balance = query_result[0]
        print("Account %d balance: %f" % (account_id, balance))

    # Close the connection
    cnx.close()


# Function to transfer money between accounts
def transfer_money(source_account_id, destination_account_id, transfer_amount):
    cnx = mysql.connector.connect(
        host=host, user=user, passwd=password, database=database
    )
    cursor = cnx.cursor()
    # Check the source account balance
    select_source_balance_query = "SELECT balance FROM Accounts WHERE account_id = %s"
    cursor.execute(select_source_balance_query, (source_account_id,))
    query_result = cursor.fetchone()
    # check if account exists
    if cursor.rowcount < 1:
        print("Source account does not exist.")
        return
    else:
        source_balance = query_result[0]

    # Check the destination account balance
    select_destination_balance_query = (
        "SELECT balance FROM Accounts WHERE account_id = %s"
    )
    cursor.execute(select_destination_balance_query, (destination_account_id,))
    query_result = cursor.fetchone()
    # check if account exists
    if cursor.rowcount < 1:
        print("Destination account does not exist.")
        return
    else:
        destination_balance = query_result[0]

    if source_balance >= transfer_amount:
        # Deduct the transfer amount from the source account
        updated_source_balance = source_balance - transfer_amount

        # Update the source account balance in the Accounts table
        update_source_balance_query = (
            "UPDATE Accounts SET balance = %s WHERE account_id = %s"
        )
        cursor.execute(
            update_source_balance_query, (updated_source_balance, source_account_id)
        )
        cnx.commit()

        # Add the transfer amount to the destination account
        updated_destination_balance = destination_balance + transfer_amount

        # Update the destination account balance in the Accounts table
        update_destination_balance_query = (
            "UPDATE Accounts SET balance = %s WHERE account_id = %s"
        )
        cursor.execute(
            update_destination_balance_query,
            (updated_destination_balance, destination_account_id),
        )
        cnx.commit()

        # Insert a new record into the Transactions table for both accounts
        insert_transaction_query = "INSERT INTO Transactions (account_id, transaction_type, amount,transaction_date) VALUES (%s, %s, %s,%s)"

        # Transaction record for the source account
        source_transaction_data = (
            source_account_id,
            "Transfer",
            -transfer_amount,
            datetime.datetime.today(),
        )
        cursor.execute(insert_transaction_query, source_transaction_data)
        cnx.commit()

        # Transaction record for the destination account
        destination_transaction_data = (
            destination_account_id,
            "Transfer",
            transfer_amount,
            datetime.datetime.today(),
        )
        cursor.execute(insert_transaction_query, destination_transaction_data)
        cnx.commit()

        print("Transfer successful!")
        print("Updated source account balance:", updated_source_balance)
        print("Updated destination account balance:", updated_destination_balance)
    else:
        print("Insufficient balance for transfer.")

    # Close the connection
    cnx.close()


# Function to apply for a loan
def apply_for_loan(account_id, loan_amount, interest_rate, start_date, end_date):
    cnx = mysql.connector.connect(
        host=host, user=user, passwd=password, database=database
    )
    cursor = cnx.cursor()
    # Check if the account exists
    select_account_query = "SELECT * FROM Accounts WHERE account_id = %s"
    cursor.execute(select_account_query, (account_id,))
    query_result = cursor.fetchone()
    if cursor.rowcount < 1:
        print("Account does not exist. Cannot apply for loan.")
        return

    # Perform necessary checks and calculations for loan eligibility, credit score, etc.
    # Determine loan eligibility and interest rate

    # If eligible, create a new record in the Loans table
    insert_loan_query = "INSERT INTO Loans (account_id, loan_amount, interest_rate, start_date, end_date) VALUES (%s, %s, %s, %s, %s)"
    loan_data = (account_id, loan_amount, interest_rate, start_date, end_date)
    cursor.execute(insert_loan_query, loan_data)
    cnx.commit()

    print("Loan application successful!")

    # Close the connection
    cnx.close()


# Function to apply for a credit card
def apply_for_credit_card(account_id):
    cnx = mysql.connector.connect(
        host=host, user=user, passwd=password, database=database
    )
    cursor = cnx.cursor()

    # Check if the account exists
    select_account_query = "SELECT * FROM Accounts WHERE account_id = %s"
    cursor.execute(select_account_query, (account_id,))
    query_result = cursor.fetchone()
    if cursor.rowcount < 1:
        print("Account does not exist. Cannot apply for credit card.")
        return

    # Perform necessary checks and calculations for credit card eligibility, credit score, etc.
    # Determine credit card eligibility

    # If eligible, create a new record in the Cards table
    insert_card_query = "INSERT INTO Cards (account_id, card_number, card_type, expiration_date, cvv) VALUES (%s, %s,%s, %s, %s)"
    card_data = (
        account_id,
        "1234567890123456",
        "Visa",
        datetime.datetime.strptime("2025-03-03", "%Y-%m-%d"),
        "237",
    )
    cursor.execute(insert_card_query, card_data)
    cnx.commit()

    print("Credit card application successful!")

    # Close the connection
    cnx.close()


# testing
# create_database()
# print("Creating New Customer Account")
# create_customer_account(
#     "Ram",
#     datetime.datetime.strptime("2002-05-28", "%Y-%m-%d"),
#     "156 Main St",
#     "9783867890",
#     "temp@gmail.com",
#     "Teacher",
# )
# print("-" * 30)
# print("Checking Account Balance")
# check_account_balance(1)
# check_account_balance(2)

# print("-" * 30)
# print("Making a Withdrawal")
# make_withdrawal(1, 5)
# print("-" * 30)
# print("Transfering Money")
# transfer_money(1, 2, 10)


# print("-" * 30)
# print("Applying for Loan")
# apply_for_loan(
#     2,
#     1000,
#     0.05,
#     datetime.datetime.today(),
#     datetime.datetime.strptime("2024-01-28", "%Y-%m-%d"),
# )


# print("-" * 30)
# print("Applying for Credit Card")
# apply_for_credit_card(1)
# print("-" * 30)
