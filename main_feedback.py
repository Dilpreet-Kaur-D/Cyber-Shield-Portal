# main_feedback.py
import customtkinter as ctk
from tkinter import messagebox
from utils.db_utils import save_feedback
import requests #to connect your Tkinter GUI ↔ Flask API


# Global token (set this from login window when user logs in)
USER_TOKEN = None#It will hold the JWT token (which proves a user is logged in).
LOGGED_IN_USERNAME = ""
LOGGED_IN_DEPARTMENT = ""


# Set appearance and theme
ctk.set_appearance_mode("system")  # Match system theme (Light/Dark)
ctk.set_default_color_theme("green")  # Use green color theme

# Reusable row for username or suggestion
class InputRow(ctk.CTkFrame):
    def __init__(self, master, label_text, text_var):
        super().__init__(master)
        self.label = ctk.CTkLabel(self, text=label_text + ":", width=120, anchor="w")
        self.label.pack(side="left", padx=5)
        self.entry = ctk.CTkEntry(self, textvariable=text_var)
        self.entry.pack(side="left", expand=True, fill="x", padx=5)

# Reusable row for dropdown ratings
class RatingRow(ctk.CTkFrame):
    def __init__(self, master, label_text, variable):
        super().__init__(master)
        self.label = ctk.CTkLabel(self, text=label_text + ":", width=130, anchor="w")
        self.label.pack(side="left", padx=5)
        self.dropdown = ctk.CTkOptionMenu(self, variable=variable, values=["1", "2", "3", "4", "5"])
        self.dropdown.pack(side="left", padx=5)

# Reusable row for department dropdown
class DepartmentRow(ctk.CTkFrame):
    def __init__(self, master, variable):
        super().__init__(master)
        self.label = ctk.CTkLabel(self, text="Department:", width=130, anchor="w")
        self.label.pack(side="left", padx=5)

        self.dropdown = ctk.CTkOptionMenu( self,variable=variable, values=[ "CSE", "ECE", "Mechanical", "Civil", "Physics", "Chemistry", "English", "Punjabi", "Law", "Commerce", "Maths", "Biotech"  ] )
        self.dropdown.pack(side="left", padx=5)


# Full Feedback Form section
class FeedbackForm(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="white", corner_radius=8)

        # Form Heading
        heading = ctk.CTkLabel(self, text="Student Feedback Form", font=("Helvetica", 18, "bold"))
        heading.pack(pady=10)

        # Variables
        self.username_var = ctk.StringVar()
        self.department_var = ctk.StringVar(value="CSE")
        self.teaching_var = ctk.StringVar(value="3")
        self.internet_var = ctk.StringVar(value="3")
        self.lab_var = ctk.StringVar(value="3")
        self.infra_var = ctk.StringVar(value="3")
        self.suggestion_var = ctk.StringVar()
        
        # Input rows
        from main_feedback import LOGGED_IN_USERNAME, LOGGED_IN_DEPARTMENT

# Create and lock username row
        username_row = InputRow(self, "Username", self.username_var)
        username_row.pack(pady=5, fill="x", padx=20)
        self.username_var.set(LOGGED_IN_USERNAME)
        username_row.entry.configure(state="readonly")

# Create and lock department dropdown
        department_row = DepartmentRow(self, self.department_var)
        department_row.pack(pady=5, fill="x", padx=20)
        self.department_var.set(LOGGED_IN_DEPARTMENT)
        department_row.dropdown.configure(state="disabled")

        RatingRow(self, "Teaching Quality", self.teaching_var).pack(pady=5, fill="x", padx=20)
        RatingRow(self, "Internet Speed", self.internet_var).pack(pady=5, fill="x", padx=20)
        RatingRow(self, "Lab Facilities", self.lab_var).pack(pady=5, fill="x", padx=20)
        RatingRow(self, "Infrastructure", self.infra_var).pack(pady=5, fill="x", padx=20)
        InputRow(self, "Suggestions", self.suggestion_var).pack(pady=5, fill="x", padx=20)

        # Submit button
        submit_btn = ctk.CTkButton(self, text="Submit Feedback", command=self.submit_feedback)
        submit_btn.pack(pady=20)

    # On click of Submit
    def submit_feedback(self):
        username = self.username_var.get()
        department = self.department_var.get()
        teaching = self.teaching_var.get()
        internet = self.internet_var.get()
        lab = self.lab_var.get()
        infra = self.infra_var.get()
        suggestion = self.suggestion_var.get()
        


        if username == "":
            messagebox.showwarning("Warning", "Please enter your username.")
            return
#-----------------------------------------------------------------------------------------------------------------
#IF TKINTER DIRECTLY LINK TO DATABASE
        # save_feedback(username, teaching, internet, lab, infra, suggestion)
        # messagebox.showinfo("Thank You", "Your feedback has been submitted!")
#-----------------------------------------------------------------------------------------------------------------
        if not USER_TOKEN:
            messagebox.showerror("Unauthorized", "Missing login token. Please login again.")
            return
        headers = {
            "Authorization": f"Bearer {USER_TOKEN}"
        }

        try:
            response = requests.post(
            "http://127.0.0.1:5000/feedback",  # Flask route
            json={
                "username": username,
                "department": department,
                "teaching": teaching,
                "internet": internet,
                "lab": lab,
                "infra": infra,
                "suggestion": suggestion,
                
            },headers=headers)

            result = response.json()

            # if response.status_code == 200:
            #     messagebox.showinfo("Success", result["message"])
            #     self.master.destroy()# close feedback window
            #     from main_login import LoginApp  # Moved import here
            #     LoginApp().mainloop()# reopen login
            #     return  # prevents any code after this...VERY IMPORTANT to prevent crashing on destroyed widget
            
            import subprocess#Python module used to start new processes (like running another .py file).
            import sys#sys.executable gives you the full path to the Python interpreter 

            if response.status_code == 200:
                messagebox.showinfo("Success", result["message"])
                self.master.destroy()
                subprocess.Popen([sys.executable, "main_login.py"])#This is like closing one app and opening another, cleanly.
                return

            else:
               messagebox.showerror("Error", result["message"])

        except requests.exceptions.ConnectionError:
            messagebox.showerror("Server Error", "Flask server is not running.")
        except Exception as e:
            messagebox.showerror("Unexpected Error", str(e))

        self.clear_form()
         

    # Clear form after submit
    def clear_form(self):
        self.username_var.set("")
        self.department_var.set("CSE")
        self.teaching_var.set("3")
        self.internet_var.set("3")
        self.lab_var.set("3")
        self.infra_var.set("3")
        self.suggestion_var.set("")
        


# Centered Form in Middle Section
class MiddleSection(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(expand=True, fill="both", padx=10, pady=10)
        form = FeedbackForm(self)
        form.place(relx=0.5, rely=0.5, anchor="center")

# Header and Footer
class HeaderAndFooter(ctk.CTkFrame):
    def __init__(self, master, text, side="top"):
        super().__init__(master, height=70)
        self.pack(side=side, fill="x")
        self.pack_propagate(False)
        label = ctk.CTkLabel(self, text=text, font=("Helvetica", 16, "bold"))
        label.pack(pady=20)

# Main App Window
class FeedbackApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CyberShield - Feedback")
        self.geometry("800x600")
        self.resizable(True, True)

        HeaderAndFooter(self, "CyberShield Feedback")
        MiddleSection(self)
        HeaderAndFooter(self, "© Dilpreet Kaur | CyberShield Portal 2025", side="bottom")

# Run the GUI
if __name__ == "__main__":
    app = FeedbackApp()
    app.mainloop()
    