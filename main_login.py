# main_login.py

import customtkinter as ctk
from tkinter import messagebox
from utils.db_utils import check_user  # Function must accept (username, password, role)
import requests #to connect login form to db via flask
import jwt
from config.secret_config import SECRET_KEY

# Appearance settings
ctk.set_appearance_mode("light")            # Options: "light", "dark", "system"
ctk.set_default_color_theme("blue")         # Options: "blue", "green", "dark-blue", etc.

# Reusable Row Component
class DetailsRow(ctk.CTkFrame):
    def __init__(self, master, label_text, show=None):
        super().__init__(master)
        self.label_text = label_text
        self.label = ctk.CTkLabel(self, text=label_text, width=100, anchor="w")
        self.label.pack(side="left", padx=5)

        # Entry for Username/Password
        if label_text in ["Username", "Password"]:
            self.entry_var = ctk.StringVar()
            self.entry = ctk.CTkEntry(self, textvariable=self.entry_var, show=show)
            self.entry.pack(side="left", expand=True, fill="x", padx=5) 

            if label_text == "Password":
                self.showing = False
                self.toggle_btn = ctk.CTkButton(self, text="👁️", width=50, command=self.toggle_password)
                self.toggle_btn.pack(side="left", padx=5)

        # Role dropdown
        elif label_text == "Role":
            self.entry_var = ctk.StringVar(value="student")
            self.entry = ctk.CTkOptionMenu(self, variable=self.entry_var, values=["student", "staff", "admin"])
            self.entry.pack(side="left", expand=True, fill="x", padx=5)

    def toggle_password(self):
        if self.showing:#is the password currently visible =true
            self.entry.configure(show="*")#configure() is a method used to change the properties (also called "options") of a widget after it has already been created.
            self.toggle_btn.configure(text="👁️")#user can click to eye icon to view password
        else:
            self.entry.configure(show="")
            self.toggle_btn.configure(text="Hide")
        self.showing = not self.showing

    def get(self):
        return self.entry_var.get()


# Login Form Section
class LoginForm(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="white", corner_radius=8)
        self.label = ctk.CTkLabel(self, text="Login", font=("Helvetica", 18, "bold"))
        self.label.pack(pady=10)

        self.username_row = DetailsRow(self, "Username")
        self.username_row.pack(fill="x", pady=5)

        self.password_row = DetailsRow(self, "Password", show="*")
        self.password_row.pack(fill="x", pady=5)

        self.role_row = DetailsRow(self, "Role")
        self.role_row.pack(fill="x", pady=5)

        self.login_btn = ctk.CTkButton(self, text="Login", command=self.verify_login)
        self.login_btn.pack(pady=10)

        #Register link
        self.register_link=ctk.CTkButton(self,text="Don't have an account? Register",fg_color="transparent",text_color="blue",command=self.open_register)
        self.register_link.pack(pady=15)

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#gets called when the user want to register by clicking .

    def open_register(self):
        self.winfo_toplevel().destroy()  # Safely destroy entire root window before opening the next screen
        from main_register import RegistrationApp
        app = RegistrationApp()
        app.mainloop()

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#gets called when the Login button is clicked.

    def verify_login(self):

        username = self.username_row.get()
        password = self.password_row.get()
        role = self.role_row.get()

        if username == "" or password == "" or role == "":
            messagebox.showwarning("Warning", "Please fill all fields.")
            return
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  # IF TKINTER IS LINKED WITH DATABASE DIRECTLY    
        # user = check_user(username, password, role)

        # if user:#If the user exists, a success message is shown with a greeting.
        #     messagebox.showinfo("Success", f"Welcome {username}!")
            
        # else:
        #     messagebox.showerror("Error", "Invalid credentials.")

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        try:
            response = requests.post(
            "http://127.0.0.1:5000/login",  # Flask login route
            json={
                "username": username,
                "password": password,
                "role": role})
            print("Server raw response:", response.text)  # This shows what Flask actually returned
            result = response.json()  # Convert JSON response → Python dictionary
            # This will crash if the response isn't valid JSON

            if response.status_code == 200:
                # 1) Did the server ask for OTP?
                if result.get("status") == "otp_required":
                    messagebox.showinfo( "Two‑Factor",
                        result.get("message", "OTP required – check your phone / e‑mail.") )
        # ➜ open the small popup you added earlier
                    self.show_otp_popup(username)
                    return                     # stop here – wait for OTP flow
                
                # Decode token to get username and department
                token = result["token"]
                # Store token and user info globally so feedback form can access it
                import main_feedback
                main_feedback.USER_TOKEN = result["token"]

                # Decode token to extract user info
                decoded = jwt.decode(result["token"], SECRET_KEY, algorithms=["HS256"])
                main_feedback.LOGGED_IN_USERNAME = decoded.get("username", "")
                main_feedback.LOGGED_IN_DEPARTMENT = decoded.get("department", "")

                

                

                
                role = self.role_row.get().lower()#it fetches the role selected and ensure this is in lowercase
                self.username_row.entry.delete(0, "end")
                self.password_row.entry.delete(0, "end")
                self.winfo_toplevel().destroy()#Close the current login window

                #  Route based on role
                if role == "student":
                    from main_feedback import FeedbackApp
                    app = FeedbackApp()
                    app.mainloop()

                
                elif role == "staff":
                    from main_staff import StaffApp  
                    app = StaffApp(username=main_feedback.LOGGED_IN_USERNAME)
                    app.mainloop()   

                elif role == "admin":
                    from main_admin import AdminApp  
                    app = AdminApp()
                    app.mainloop()
                
            else:
                msg = result.get("message", "Login failed.")
                if result.get("status") == "locked":
                    messagebox.showerror("Account Locked", msg)
                else:
                    messagebox.showwarning("Login Failed", msg)
                    
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Server Error", "Flask server is not running.")
        except Exception as e:
            messagebox.showerror("Unexpected Error", str(e))

    def show_otp_popup(self, username):
        otp_window = ctk.CTkToplevel(self)
        otp_window.title("Enter OTP")
        otp_window.geometry("300x180")

        otp_window.lift()                     # bring on top
        otp_window.attributes("-topmost", True)  # force on top

        label = ctk.CTkLabel(otp_window, text="Enter the OTP sent to you:")
        label.pack(pady=10)

        otp_var = ctk.StringVar()
        otp_entry = ctk.CTkEntry(otp_window, textvariable=otp_var)
        otp_entry.pack(pady=10)

        def verify():
            otp = otp_var.get()
            try:
                response = requests.post("http://127.0.0.1:5000/verify-otp", data={
                "username": username,
                "otp": otp            })
                result = response.json()

                if response.status_code == 200 and result["status"] == "success":
                    token = result.get("token")

                    import main_feedback
                    main_feedback.USER_TOKEN = token

                    decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                    main_feedback.LOGGED_IN_USERNAME = decoded.get("username", "")
                    main_feedback.LOGGED_IN_DEPARTMENT = decoded.get("department", "")

                    messagebox.showinfo("Success", "OTP Verified. Login successful!")
                    otp_window.destroy()
                    self.winfo_toplevel().destroy()

                    role = self.role_row.get().lower()
                    if role == "student":
                        from main_feedback import FeedbackApp
                        FeedbackApp().mainloop()
                    elif role == "staff":
                        from main_staff import StaffApp
                        StaffApp(username=main_feedback.LOGGED_IN_USERNAME).mainloop()
                    elif role == "admin":
                        from main_admin import AdminApp
                        AdminApp().mainloop()

                else:
                    messagebox.showerror("Error", result.get("message", "Invalid OTP."))

            except Exception as e:
                messagebox.showerror("Error", f"Failed to verify OTP:\n{e}")

        verify_btn = ctk.CTkButton(otp_window, text="Verify", command=verify)
        verify_btn.pack(pady=10)


# Center Section
class MiddleSection(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(expand=True, fill="both", pady=10, padx=10)
        self.form = LoginForm(self)
        self.form.place(relx=0.5, rely=0.5, anchor="center")


# Reusable Header/Footer
class HeaderAndFooter(ctk.CTkFrame):
    def __init__(self, master, text, side="top", bg_color="#003366"):
        super().__init__(master, height=70, fg_color=bg_color)
        self.pack(side=side, fill="x")
        self.pack_propagate(False)

        label = ctk.CTkLabel(self, text=text, font=("Helvetica", 16, "bold"), text_color="white")
        label.pack(pady=20)


# Main Login App
class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CyberShield Portal - Login")
        self.geometry("900x600")
        self.resizable(True, True)

        HeaderAndFooter(self, "CyberShield Login", bg_color="#004080")  # Dark blue header
        MiddleSection(self)
        HeaderAndFooter(self, "© Dilpreet Kaur | Login Portal 2025", side="bottom", bg_color="#002147")  # Navy footer


# Run app
if __name__ == "__main__":
    app = LoginApp()
    app.mainloop()
