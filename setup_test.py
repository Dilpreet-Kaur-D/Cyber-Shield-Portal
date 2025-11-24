from utils.db_utils import create_tables, add_user,create_attempts_table
from utils.db_utils import log_login_activity, create_login_log_table,create_otp_table


if __name__ == "__main__":
    #create_tables()
    #create_attempts_table()
    #create_login_log_table()
    # call once at app start
    create_otp_table()

    print("table created successfully!")

    # result = add_user("preetui456", "xyz@456", "staff", "CSE")

    # if result:
    #     print("User added ")
    # else:
    #     print("Username already exists ")
