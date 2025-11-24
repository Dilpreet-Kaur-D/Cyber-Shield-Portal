# main.py (Registration Form)
import customtkinter as ctk
from tkinter import messagebox
from utils.db_utils import add_user
import requests #to connect your Tkinter GUI ↔ Flask API
from config.secret_config import ADMIN_SECRET_KEY  # Add at top of the file
import re #re stands for Regular Expressions — a powerful tool in Python used to search for patterns in text.
# Set appearance
# Set the appearance mode of the app to match the system theme (can be "Light", "Dark", or "System")
ctk.set_appearance_mode("System")

# Set the color theme of the widgets (predefined themes: "blue", "green", "dark-blue", etc.)
ctk.set_default_color_theme("green")


#  Reusable Row Component (Entry / OptionMenu)
class DetailsRow(ctk.CTkFrame):
    def __init__(self, master, label_text, show=None):
        super().__init__(master)
        self.label_text = label_text
        self.label = ctk.CTkLabel(self, text=label_text, width=100, anchor="w")
        self.label.pack(side="left", padx=5)

        # For Username or Password fields
        if label_text in ["Username", "Password"]:
            self.entry_var = ctk.StringVar()
            self.entry = ctk.CTkEntry(self, textvariable=self.entry_var, show=show)
            self.entry.pack(side="left", expand=True, fill="x", padx=5)

            if label_text == "Password":
                self.showing = False
                self.toggle_btn = ctk.CTkButton(self, text="Show", width=50, command=self.toggle_password)
                self.toggle_btn.pack(side="left", padx=5)

    #  Create widgets BEFORE using in check_password_strength
                self.strength_label = ctk.CTkLabel(self, text="", font=("Arial", 10))
                self.strength_label.pack(side="bottom", anchor="w", padx=5)

                self.strength_bar = ctk.CTkProgressBar(self, width=180)
                self.strength_bar.set(0)
                self.strength_bar.pack(side="bottom", anchor="w", padx=5, pady=(5, 0))

                self.length_label = ctk.CTkLabel(self, text="✖ At least 6 characters", font=("Arial", 10), text_color="red")
                self.length_label.pack(side="bottom", anchor="w", padx=5)

                self.digit_label = ctk.CTkLabel(self, text="✖ At least 1 digit", font=("Arial", 10), text_color="red")
                self.digit_label.pack(side="bottom", anchor="w", padx=5)

                self.upper_label = ctk.CTkLabel(self, text="✖ At least 1 uppercase", font=("Arial", 10), text_color="red")
                self.upper_label.pack(side="bottom", anchor="w", padx=5)

                self.symbol_label = ctk.CTkLabel(self, text="✖ At least 1 symbol", font=("Arial", 10), text_color="red")
                self.symbol_label.pack(side="bottom", anchor="w", padx=5)

    # Bind typing event to show updates live
            self.entry.bind("<KeyRelease>", self.check_password_strength)

        # For Role field
        elif label_text == "Role":
            self.entry_var = ctk.StringVar(value="student")
            self.entry = ctk.CTkOptionMenu(self, variable=self.entry_var, values=["student",  "admin"])
            self.entry.pack(side="left", expand=True, fill="x", padx=5)
        
        #foe department dropdown
        elif label_text == "Department":
            self.entry_var = ctk.StringVar(value="CSE")
            self.entry = ctk.CTkOptionMenu(self, variable=self.entry_var,  values=["None",  # Used for admin
                     "CSE", "ECE", "Mechanical", "Civil", "Physics", "Chemistry", "English", "Punjabi", "Law", "Commerce", "Maths", "Biotech"])
            self.entry.pack(side="left", expand=True, fill="x", padx=5)

        elif label_text == "Admin Key":
            self.entry_var = ctk.StringVar()
            self.showing = False  # or True depending on default state

            self.entry = ctk.CTkEntry(self, textvariable=self.entry_var, show="*")
            self.entry.pack(side="left", expand=True, fill="x", padx=(5, 0))

            self.toggle_btn = ctk.CTkButton(
            self, text="Show", width=50,command=self.toggle_password,  # call the same method!
            fg_color="grey", hover_color="darkgrey", text_color="black"    )
            self.toggle_btn.pack(side="right", padx=5)


        # 💡 Fallback: anything else you add later
        else:
            self.entry_var = ctk.StringVar()
            self.entry = ctk.CTkEntry(self, textvariable=self.entry_var)
            self.entry.pack(side="left", expand=True, fill="x", padx=5)
    #These are used to dynamically hide or show a row 
    def hide(self):
        self.pack_forget()

    def show(self):
        self.pack(fill="x", pady=5)


    # toggle Show/Hide Password
    def toggle_password(self):
        if self.showing:
            self.entry.configure(show="*")
            self.toggle_btn.configure(text="Show")
        else:
            self.entry.configure(show="")
            self.toggle_btn.configure(text="Hide")
        self.showing = not self.showing

    # Get value
    def get(self):
        return self.entry_var.get()
    
    def check_password_strength(self, event=None):
        # — event is unused but needed for <KeyRelease> binding
        if not hasattr(self, "strength_bar"):
            return
        password = self.entry_var.get()

    # ----- individual rules -----
        has_len    = len(password) >= 6
        has_digit  = bool(re.search(r"\d", password))
        has_upper  = bool(re.search(r"[A-Z]", password))
        has_symbol = bool(re.search(r"[^\w]", password))   # any non‑alphanum / underscore
    # ----------------------------

    # score out of 4
        score = sum([has_len, has_digit, has_upper, has_symbol])
        self.strength_bar.set(score / 4)

    # colour bar
        if score <= 1:
            self.strength_bar.configure(progress_color="red")
            strength_word, word_color = "Weak", "red"
        elif score in (2, 3):
            self.strength_bar.configure(progress_color="orange")
            strength_word, word_color = "Medium", "orange"
        else:
            self.strength_bar.configure(progress_color="green")
            strength_word, word_color = "Strong", "green"

    #  keep  old one‑liner summary label
        self.strength_label.configure(text=f"Strength: {strength_word}", text_color=word_color)

    # update checklist labels
        self.length_label.configure(text=("✔ At least 6 characters" if has_len else "✖ At least 6 characters"),
                                text_color=("green" if has_len else "red"))
        self.digit_label.configure(text=("✔ At least 1 digit"      if has_digit else "✖ At least 1 digit"),
                               text_color=("green" if has_digit else "red"))
        self.upper_label.configure(text=("✔ At least 1 uppercase"  if has_upper else "✖ At least 1 uppercase"),
                               text_color=("green" if has_upper else "red"))
        self.symbol_label.configure(text=("✔ At least 1 symbol"    if has_symbol else "✖ At least 1 symbol"),
                                text_color=("green" if has_symbol else "red"))

    # def check_password_strength(self, event=None):
    #     #event=None is there because this function is triggered when the user types in the password field
    #     password = self.entry_var.get()

    #     if len(password) < 6:
    #         strength = "Weak"
    #         color = "red"
    #     elif re.search(r"[A-Z]", password) and re.search(r"[^a-zA-Z0-9]", password):#Does the password have anything that is NOT a letter or number
    #         strength = "Strong"#[^...] is a negation pattern.
    #         color = "green"
    #     elif re.search(r"[0-9]", password):
    #         strength = "Medium"
    #         color = "orange"
    #     else:
    #         strength = "Weak"
    #         color = "red"

       # self.strength_label.configure(text=f"Strength: {strength}", text_color=color)

# Full Form Section
class FormSection(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="white", corner_radius=8)
        self.label = ctk.CTkLabel(self, text="Register", font=("Helvetica", 18, "bold"))
        self.label.pack(pady=10)

        self.username_row = DetailsRow(self, "Username")
        self.username_row.pack(fill="x", pady=5)

        self.dept_row = DetailsRow(self, "Department")
        self.dept_row.pack(fill="x", pady=5)


        self.password_row = DetailsRow(self, "Password", show="*")
        self.password_row.pack(fill="x", pady=5)
        


        self.role_row = DetailsRow(self, "Role")
        self.role_row.pack(fill="x", pady=5)
        self.role_row.entry.configure(command=self.handle_role_change_event)


        # Add Admin Secret Key field (hidden by default)
        self.admin_key_row = DetailsRow(self, "Admin Key")  # Reuse same component
        #self.admin_key_row.pack(fill="x", pady=5)
        #self.admin_key_row.hide()  # Hide initially


        self.submit_btn = ctk.CTkButton(self, text="Register", command=self.submit_form)
        self.submit_btn.pack(pady=10)
        
    # Handle role changes dynamically (triggered when a user selects a different role)
    def handle_role_change_event(self, selected_role):
        if selected_role.lower() == "admin":
            self.dept_row.hide()
            ## Internally set the department value to "None" so it doesn’t send a leftover value
            self.dept_row.entry_var.set("None")
            self.admin_key_row.pack(before=self.submit_btn, fill="x", pady=5)
        else:
            self.dept_row.show()
             # If the previous value was "None" (due to admin selection), reset it to a valid default
            if self.dept_row.entry_var.get() == "None":
                self.dept_row.entry_var.set("CSE")

            self.admin_key_row.pack_forget()  # Hide cleanly
            self.admin_key_row.entry_var.set("")  # Clear any old value
        
    


    #Logic when user clicks "Register"
    def submit_form(self):
        username = self.username_row.get()
        password = self.password_row.get()
        # Inside submit_form() method, after: password = self.password_row.get()

        has_len    = len(password) >= 6
        has_digit  = bool(re.search(r"\d", password))
        has_upper  = bool(re.search(r"[A-Z]", password))
        has_symbol = bool(re.search(r"[^\w]", password))

        score = sum([has_len, has_digit, has_upper, has_symbol])

        if score <= 1:
            messagebox.showwarning("Weak Password", "Your password is weak.\nIt's recommended to use:\n• At least 6 characters\n• 1 digit\n• 1 uppercase letter\n• 1 symbol\n\nYou can continue, but for better security, please improve it.")
        role = self.role_row.get()
        department = self.dept_row.get()
        admin_key_entered = self.admin_key_row.get()


        if username == "" or password == "":
            messagebox.showwarning("Warning", "Please fill all fields.")
            return
        
        # Security Check for Admin Role
        if role.lower() == "admin": 
            if admin_key_entered != ADMIN_SECRET_KEY:
                messagebox.showerror("Unauthorized", "Invalid admin secret key!")
                return
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------
#WHEN TKINTER DIRECTLY CONNECTED DATABASE
        # result = add_user(username, password, role)
        # if result:
        #     messagebox.showinfo("Success", "User registered successfully!")
        #     self.username_row.entry.delete(0, "end")
        #     self.password_row.entry.delete(0, "end")
        # else:
        #     messagebox.showerror("Error", "Username already exists.")
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------
#now tkinter communicate directly to flask..inside submit functtion
        try:
            #response is used to Send a POST request to my locally running Flask server at the route /register
            response=requests.post("http://127.0.0.1:5000/register",json={"username": username,"password": password,"role": role, "department": department})#Convert this dictionary into a JSON string.
            result = response.json()#Converts the Flask response (which is in JSON format) into a Python dictionary.
            #This response contains a "message" key (e.g., "User registered successfully").
            if response.status_code==200:
                # messagebox.showinfo("Success",result["message"])
                # self.username_row.entry.delete(0, "end")
                # self.password_row.entry.delete(0, "end")
                
                    messagebox.showinfo("Success", f"{result['message']}! Please login now with your credentials.")
                    self.winfo_toplevel().destroy()  # Safely destroy entire root window before opening the next screen
                    from main_login import LoginApp
                    app = LoginApp()
                    app.mainloop()
            else:
                messagebox.showerror("Error", result["message"])
                #messagebox.showinfo("Title", "Message to show")
        except requests.exceptions.ConnectionError:
                messagebox.showerror("Server Error", "Flask server is not running.")
        except Exception as e:
                messagebox.showerror("Unexpected Error", f"Something went wrong:\n{str(e)}")#e is actually an Exception object (not text)..it won’t work properly unless you convert it to a string.

        
# Centered Form in Middle
class MiddleSection(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(expand=True, fill="both", pady=10, padx=10)
        self.form = FormSection(self)
        self.form.place(relx=0.5, rely=0.5, anchor="center")


# Header/Footer Layout
class HeaderAndFooter(ctk.CTkFrame):
    def __init__(self, master, text, side="top"):
        super().__init__(master, height=70)
        self.pack(side=side, fill="x")
        self.pack_propagate(False)

        label = ctk.CTkLabel(self, text=text, font=("Helvetica", 16, "bold"))
        label.pack(pady=20)


# App Main Window
class RegistrationApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CyberShield Portal - Register")
        self.geometry("900x600")  # Bigger window size
        self.resizable(True, True)

        HeaderAndFooter(self, "CyberShield Registration")
        MiddleSection(self)
        HeaderAndFooter(self, "© Dilpreet Kaur | CyberShield Portal 2025", side="bottom")
        

if __name__ == "__main__":
    app = RegistrationApp()
    app.mainloop()
