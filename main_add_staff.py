import customtkinter as ctk
from tkinter import messagebox
import requests

# Reusable row
class DetailsRow(ctk.CTkFrame):
    def __init__(self, master, label_text, show=None):
        super().__init__(master)
        self.label_text = label_text
        self.label = ctk.CTkLabel(self, text=label_text, width=100, anchor="w")
        self.label.pack(side="left", padx=5)

        if label_text == "Password":
            self.entry_var = ctk.StringVar()
            self.entry = ctk.CTkEntry(self, textvariable=self.entry_var, show=show)
            self.entry.pack(side="left", expand=True, fill="x", padx=5)
            self.showing = False
            self.toggle_btn = ctk.CTkButton(self, text="👁️", width=50, command=self.toggle_password)
            self.toggle_btn.pack(side="left", padx=5)

        elif label_text == "Department":
            self.entry_var = ctk.StringVar(value="CSE")
            self.entry = ctk.CTkOptionMenu(self, variable=self.entry_var,
                                           values=["CSE", "ECE", "Mechanical", "Civil", "Physics", "Chemistry", "English", "Punjabi", "Law", "Commerce", "Maths", "Biotech"])
            self.entry.pack(side="left", expand=True, fill="x", padx=5)

        else:
            self.entry_var = ctk.StringVar()
            self.entry = ctk.CTkEntry(self, textvariable=self.entry_var)
            self.entry.pack(side="left", expand=True, fill="x", padx=5)

    def toggle_password(self):
        if self.showing:
            self.entry.configure(show="*")
            self.toggle_btn.configure(text="👁️")
        else:
            self.entry.configure(show="")
            self.toggle_btn.configure(text="Hide")
        self.showing = not self.showing

    def get(self):
        return self.entry_var.get()


# Main AddStaffForm window
class AddStaffForm(ctk.CTkToplevel):
    def __init__(self, master=None, token=None):
        super().__init__(master)
        self.token = token
        self.title("Add Staff Member")
        self.geometry("800x600")
        self.resizable(True, True)

        # Outer frame to center form inside window
        self.middle_frame = ctk.CTkFrame(self)
        self.middle_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Inner form
        self.form_frame = ctk.CTkFrame(self.middle_frame, fg_color="white", corner_radius=10)
        self.form_frame.place(relx=0.5, rely=0.5, anchor="center")  # 🟢 Centered always

        title = ctk.CTkLabel(self.form_frame, text="Add New Staff", font=("Helvetica", 18, "bold"))
        title.pack(pady=(20, 10))

        self.username_row = DetailsRow(self.form_frame, "Username")
        self.username_row.pack(fill="x", pady=10, padx=20)

        self.password_row = DetailsRow(self.form_frame, "Password", show="*")
        self.password_row.pack(fill="x", pady=10, padx=20)

        self.dept_row = DetailsRow(self.form_frame, "Department")
        self.dept_row.pack(fill="x", pady=10, padx=20)

        self.submit_btn = ctk.CTkButton(self.form_frame, text="Add Staff", command=self.submit_staff)
        self.submit_btn.pack(pady=20)

    def submit_staff(self):
        username = self.username_row.get()
        password = self.password_row.get()
        department = self.dept_row.get()

        if not username or not password:
            messagebox.showwarning("Missing Data", "Username and password are required.")
            return

        try:
            res = requests.post(
                "http://127.0.0.1:5000/add_staff",
                json={"username": username, "password": password, "department": department},
                headers={"Authorization":f"{ self.token}"}
            )

            print("Status Code:", res.status_code)
            print("Raw Response:", res.text)

            if res.status_code == 200:
                try:
                    result = res.json()
                    messagebox.showinfo("Success", result.get("message", "Staff added successfully."))
                    self.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Response not JSON: {str(e)}\nRaw: {res.text}")
            else:
                messagebox.showerror("Failed", f"Status {res.status_code}: {res.text}")

        except requests.exceptions.ConnectionError:
            messagebox.showerror("Server Error", "Flask server is not running.")
