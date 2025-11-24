# main_staff.py

import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg#This lets us show charts directly inside the GUI window.
from tkinter import ttk#ttk.Treeview to display feedback in tabular form
from utils.db_utils import get_feedback_by_department, get_user_department#used it to fetch the department of logged-in staff
#get_feedback_by_department	Fetches only department-specific feedback from DB
# Set appearance
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("green")


# ----------------------------- HEADER + FOOTER -----------------------------
class HeaderAndFooter(ctk.CTkFrame):
    def __init__(self, master, text, side="top", bg_color="#004466"):
        super().__init__(master, height=70, fg_color=bg_color)
        self.pack(side=side, fill="x")
        self.pack_propagate(False)
        label = ctk.CTkLabel(self, text=text, font=("Helvetica", 16, "bold"), text_color="white")
        label.pack(pady=20)


# ----------------------------- STAFF DASHBOARD -----------------------------
class StaffDashboard(ctk.CTkFrame):
    def __init__(self, master, staff_username, department):
        super().__init__(master, fg_color="white", corner_radius=8)
        self.master = master  # to access the main window
        self.staff_username = staff_username
        self.department = department        
        self.pack(expand=True, fill="both", pady=20, padx=20)

        # Top Row with Welcome and Logout
        top_row = ctk.CTkFrame(self, fg_color="white")
        top_row.pack(fill="x", pady=10, padx=10)

        ctk.CTkLabel(top_row, text=f"Welcome, {self.staff_username} ({self.department})",
                     font=("Helvetica", 18, "bold"), text_color="black").pack(side="left")

        logout_btn = ctk.CTkButton(top_row, text="Logout", fg_color="#880000", hover_color="#aa0000",
                                   text_color="white", command=self.logout)
        logout_btn.pack(side="right", padx=10)
        
        # Fetch feedback data
        self.feedback_data = get_feedback_by_department(self.department)
        if not self.feedback_data:
            ctk.CTkLabel(self, text="No feedback data yet!", text_color="red").pack(pady=20)
        else:
            self.show_avg_chart()
            self.show_feedback_table()
    def logout(self):
        from tkinter import messagebox  # Ensure this is imported at the top

        if messagebox.askyesno("Confirm", "Are you sure you want to logout?"):
            self.master.destroy()  # Close current StaffApp window
            from main_login import LoginApp
            LoginApp().mainloop()  # Reopen login screen
        
    def show_avg_chart(self):
        teaching = [int(row[3]) for row in self.feedback_data]#self.feedback_data is a list of rows.
        internet = [int(row[4]) for row in self.feedback_data]#Each row contains 9 values (from database):
        cleanliness = [int(row[5]) for row in self.feedback_data]
        labs = [int(row[6]) for row in self.feedback_data]

        avg_values = [
            sum(teaching) / len(teaching),
            sum(internet) / len(internet),
            sum(cleanliness) / len(cleanliness),
            sum(labs) / len(labs)
        ]

        #sum(teaching) adds all scores like 4+5+3...
        #len(teaching) counts how many students gave feedback form

        categories = ["Teaching", "Internet", "Cleanliness", "Labs"]
        #contains the labels for each bar in the bar chart.

        fig, ax = plt.subplots(figsize=(5, 3))
        #plt.subplots() is a Matplotlib function that creates:
        #fig: the entire chart container (called Figure)
        #ax: the area inside the figure where we draw the bars (called Axes)
        #figsize=(5, 3) means:Width = 5 inches,Height = 3 inches

        ax.bar(categories, avg_values, color=["skyblue", "orange", "green", "violet"])
        #.bar(x, y, color=...) creates a bar chart where:
        # x = categories like ["Teaching", "Internet", ...]
        # y = avg_values like [4.5, 3.7, 4.2, 3.9]
        # color assigns a separate color to each bar

        ax.set_ylim(0, 5)#Sets the range of the y-axis.
        ax.set_title("Average Feedback (1 to 5)")#Adds a title to the chart above the bars.
        ax.set_ylabel("Avg. Score")#Adds a label to the y-axis.

        canvas = FigureCanvasTkAgg(fig, master=self)
        #Tkinter can’t directly show Matplotlib plots...FigureCanvasTkAgg wraps it in a way that Tkinter can handle.
        #master=self: Tells it to add the chart into the current frame (self = the staff dashboard).
        canvas.draw()#Without .draw(), the chart won’t appear
        canvas.get_tk_widget().pack(pady=10)
        #get_tk_widget() turns the canvas into a Tkinter widget (like a Label or Button)
        # .pack(pady=10) adds it to the layout with 10px padding on top and bottom

    def show_feedback_table(self):
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(pady=10, fill="both", expand=True)

        tree = ttk.Treeview(
            table_frame,
            columns=("username", "teaching", "internet", "cleanliness", "labs", "comment", "submitted"),
            show="headings"
        )
        tree.pack(fill="both", expand=True)
        #ttk.Treeview is the actual table.
        # table_frame is where it's placed.
        # columns=...: Defines the names of each column internally (not what’s shown on screen).
        # show="headings":  Hides the default left-side blank column and shows only the headings and rows.

        headings = ["Student", "Teaching", "Internet", "Cleanliness", "Labs", "Comment", "Submitted At"]
        #This is the list of visible headings shown to the user in the GUI 
        for col, head in zip(tree["columns"], headings):#zip(...) pairs each internal column name with the visible label:

            tree.heading(col, text=head)#Sets what text appears at the top of each column.
            tree.column(col, anchor="center", width=120)#Styles the column:

        for row in self.feedback_data:
            tree.insert("", "end", values=(row[1], row[3], row[4], row[5], row[6], row[7], row[8]))
            #tree.insert(parent, index, values=(...))
            #Adds one row to the table with values for each column.


# ----------------------------- MAIN STAFF APP -------------------------------------------------------------------------------------------------------------
class StaffApp(ctk.CTk):
    def __init__(self, username):
        super().__init__()
        self.title("CyberShield Staff Dashboard")
        self.geometry("1000x700")
        self.resizable(True, True)

        # Automatically fetch department using username
        department = get_user_department(username)
        if department:
            HeaderAndFooter(self, "CyberShield | Staff Portal", bg_color="#005580")
            StaffDashboard(self, staff_username=username, department=department)
            HeaderAndFooter(self, "© Dilpreet Kaur | Staff Dashboard 2025", side="bottom", bg_color="#003344")
        else:
            ctk.CTkLabel(self, text="Department not found for this user.", text_color="red").pack(pady=50)


# ----------------------------- TEST MODE (optional) ------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    # Test mode with a real staff username from  DB
    app = StaffApp(username="hari")
    app.mainloop()
