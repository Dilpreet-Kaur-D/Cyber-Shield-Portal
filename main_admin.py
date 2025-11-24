# main_admin.py

import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk, filedialog, messagebox
from utils.db_utils import get_all_feedback_averages
import csv
import main_feedback  # to clear token
from main_login import LoginApp  # to reopen login window
# Add this import at the top of your file
from main_add_staff import AddStaffForm


ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("green")

class HeaderAndFooter(ctk.CTkFrame):
    def __init__(self, master, text, side="top", bg_color="#333333"):
        super().__init__(master, height=70, fg_color=bg_color)
        self.pack(side=side, fill="x")
        self.pack_propagate(False)
        label = ctk.CTkLabel(self, text=text, font=("Helvetica", 16, "bold"), text_color="white")
        label.pack(pady=20)

class AdminDashboard(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="white", corner_radius=8)
        self.pack(expand=True, fill="both", padx=20, pady=10)

        # Top control panel
        control_frame = ctk.CTkFrame(self, fg_color="transparent")
        control_frame.pack(fill="x", pady=(10, 0), padx=10)

        # Export Button
        export_btn = ctk.CTkButton(control_frame, text="📁 Export CSV", command=self.export_to_csv, fg_color="#0077b6")
        export_btn.pack(side="left")

        #logout button
        logout_btn = ctk.CTkButton(control_frame, text="Logout", command=self.logout, fg_color="red", text_color="white")
        logout_btn.pack(side="right", padx=(10, 0))
        
        #add staff button
        add_staff_btn = ctk.CTkButton(control_frame, text="➕ Add Staff", fg_color="blue", text_color="white", command=self.open_add_staff_window)
        add_staff_btn.pack(side="left", padx=(10, 0))


        # Department Filter Dropdown
        #get_all_feedback_averages() returns a list of dictionaries. ..like{"department": "CSE", "teaching": 4.2, "internet": 3.5, ...}
        #[row["department"] for row in ...] → this is a list comprehension to extract the "department" name from each row.
        #simply adds "All" at the beginning of the list 
        self.dept_values = ["All"] + [row["department"] for row in get_all_feedback_averages()]
        self.dept_dropdown = ctk.CTkOptionMenu(control_frame, values=self.dept_values, command=self.filter_by_department)
        self.dept_dropdown.set("All")
        self.dept_dropdown.pack(side="right")

        # Title
        heading = ctk.CTkLabel(self, text="Admin Feedback Analysis", font=("Helvetica", 18, "bold"), text_color="black")
        heading.pack(pady=10)

        self.feedback_data = get_all_feedback_averages()#stores the original list of all feedback..[{"department": "CSE", "teaching": 4.5, "internet": 4.2, "labs": 4.1, "infra": 4.0},


        self.filtered_data = self.feedback_data.copy()#creates a copy of the data for filtering.

        if not self.feedback_data:
            ctk.CTkLabel(self, text="No feedback data available.", text_color="red").pack(pady=20)
        else:
            self.chart_frame = ctk.CTkFrame(self, fg_color="transparent")#A blank frame (container) to hold charts.
            self.chart_frame.pack()
            self.table_frame = ctk.CTkFrame(self, fg_color="transparent")#Another frame to hold the feedback summary table.
            self.table_frame.pack(fill="both", expand=False)

            self.show_charts(self.filtered_data)#draws bar charts based on the data.
            self.show_summary_table(self.filtered_data)#displays the department-wise feedback in tabular format.
    
    #used for department dropdown
    def filter_by_department(self, selected):
        if selected == "All":
            self.filtered_data = self.feedback_data
        else:
            self.filtered_data = [row for row in self.feedback_data if row["department"] == selected]

        for widget in self.chart_frame.winfo_children():
        #self.chart_frame is a container/frame where your charts are shown...
        # winfo_children() is a built-in method that returns all the child widgets inside that frame.
            widget.destroy()
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        self.show_charts(self.filtered_data)#draws a new chart using the filtered data 
        self.show_summary_table(self.filtered_data)

    def show_charts(self, data):
        #data is a list of dictionaries
        departments = [row["department"] for row in data]
        teaching = [row["teaching"] for row in data]
        internet = [row["internet"] for row in data]
        lab = [row["labs"] for row in data]
        infra = [row["infra"] for row in data]

        fig, ax = plt.subplots(figsize=(10, 4))
        #fig = the full figure (canvas)
        # ax = the plot area where bars will be drawn
        # figsize=(10, 4) makes it 10 inches wide and 4 inches tall


        x = range(len(departments))
        #x = range(3) → [0, 1, 2].. gives us X-axis base positions for each department.

        ax.bar(x, teaching, width=0.15, label="Teaching")
        #These are the first bars in each department group.
        ax.bar([i + 0.15 for i in x], internet, width=0.15, label="Internet")
        #shifts the bar to the right by 0.15 so it appears next to Teaching.
        ax.bar([i + 0.30 for i in x], lab, width=0.15, label="Labs")
        ax.bar([i + 0.45 for i in x], infra, width=0.15, label="Infrastructure")
#.bar() call creates one color-coded series:
        ax.set_xticks([i + 0.22 for i in x])
        #tells the chart where to place the department names on the X-axis...middle of this group is around 0.22.
        ax.set_xticklabels(departments, rotation=30, ha='right')
        # tells matplotlib what text to display at the X-tick position
        # horizontal alignment is right-aligned
        ax.set_ylim(0, 5)
        #sets the Y-axis scale between 0 and 5
        ax.set_title("Department-wise Average Feedback")
        ax.set_ylabel("Avg. Score")
        ax.legend()#Adds a color guide box

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)# connects the Matplotlib figure (fig) to the Tkinter frame (self.chart_frame)
        canvas.draw()#actually renders the chart, like pressing “print.”
        canvas.get_tk_widget().pack(pady=10)#places the chart widget inside your GUI window, with pady=10 giving vertical space.

    def show_summary_table(self, data):
        #ttk--themed tk
        tree = ttk.Treeview(
            self.table_frame,#parent frame
            columns=("Department", "Teaching", "Internet", "Labs", "Infrastructure"),
            show="headings"
        )
        tree.pack(fill="both", expand=True)

        for col in tree["columns"]:
            tree.heading(col, text=col)#Sets the text shown in the column heading (top of table)...For this column (e.g., 'Internet'), set the top label text to 'Internet'.
            tree.column(col, anchor="center", width=120)#Centers text inside the column and sets width.

        for row in data:
            #It adds data (one row at a time) into the table called tree
            #tree.insert("", "end", values=( ... ))
            #"" keeps the widget in “flat table”
            #"end" means: “Append the new row after any existing rows.”
            tree.insert("", "end", values=(
                row["department"],
                round(row["teaching"], 2),#Takes the teaching score and rounds it to 2 decimal places.
                round(row["internet"], 2),
                round(row["labs"], 2),
                round(row["infra"], 2)
            ))

    def export_to_csv(self):
        #Opens a “Save As” window so the admin can choose a location and filename to save the CSV.
        #If the user selects Desktop/feedback_summary.csv, file_path becomes that string.
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if file_path:
            try:
                with open(file_path, mode="w", newline="") as file:
                    writer = csv.writer(file)
                    #Creates a CSV writer object to help us write rows into the file using Python’s csv module.
                    writer.writerow(["Department", "Teaching", "Internet", "Labs", "Infrastructure"])
                    for row in self.filtered_data:
                        writer.writerow([
                            row["department"],
                            round(row["teaching"], 2),
                            round(row["internet"], 2),
                            round(row["labs"], 2),
                            round(row["infra"], 2)
                        ])
                messagebox.showinfo("Export Successful", f"Feedback exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export Failed", str(e))
    def open_add_staff_window(self):
        from main_feedback import USER_TOKEN
        from main_add_staff import AddStaffForm

        if not USER_TOKEN:
            messagebox.showerror("Error", "Not authorized. Please log in again.")
            return

        self.staff_window = AddStaffForm(self.master, token=USER_TOKEN)
        #token=USER_TOKEN: Passes the admin's token to the form to prove they are logged in.

        self.staff_window.grab_set()
        #the user must complete or close this window before going back to the main admin screen.

    def logout(self):
        confirm = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if confirm:
            # Clear login info
            main_feedback.USER_TOKEN = None
            main_feedback.LOGGED_IN_USERNAME = ""
            main_feedback.LOGGED_IN_DEPARTMENT = ""

            # Close current window
            self.master.destroy()
            

            # Reopen login window
            login_app = LoginApp()
            login_app.mainloop()


class AdminApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CyberShield Admin Dashboard")
        self.geometry("1100x720")
        self.resizable(True, True)

        HeaderAndFooter(self, "CyberShield | Admin Portal", bg_color="#222222")
        AdminDashboard(self)
        HeaderAndFooter(self, "\u00a9 Dilpreet Kaur | Admin Dashboard 2025", side="bottom", bg_color="#222222")

        

if __name__ == "__main__":
    app = AdminApp()
    app.mainloop()
