'''
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from google_sheets import get_entries_in_range
from datetime import datetime
import threading
from config import DATE_FORMAT, SHEET_IDS
from custom_exceptions import GoogleSheetsAPIError, DataValidationError, ReportGenerationError
from log_config import logger
from dates import parse_date
from report_generator import ReportGenerator

class ReportApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Report Generator")
        self.root.geometry("700x500")
        self.root.minsize(700, 500)  # Set a minimum size to prevent UI breaking
        
        self.sheet_ids = SHEET_IDS
        self.current_entries = []
        
        self.create_widgets()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Top control panel
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill="x", pady=5)
        
        control_frame = ttk.LabelFrame(top_frame, text="Select Date Range")
        control_frame.pack(side="left", padx=5, pady=5, fill="both", expand=False)
        
        ttk.Label(control_frame, text="From:").pack(side="left", padx=5)
        self.start_date = DateEntry(control_frame, date_pattern=DATE_FORMAT.replace("%", ""), enforce_date=True, width=12)
        self.start_date.set_date(datetime.now())
        self.start_date.pack(side="left", padx=5)
        
        ttk.Label(control_frame, text="To:").pack(side="left", padx=5)
        self.end_date = DateEntry(control_frame, date_pattern=DATE_FORMAT.replace("%", ""), enforce_date=True, width=12)
        self.end_date.set_date(datetime.now())
        self.end_date.pack(side="left", padx=5)
        
        self.btn_generate = ttk.Button(control_frame, text="View", command=self.generate_report_threaded)
        self.btn_generate.pack(side="left", padx=10, pady=5)
        
        # Export button outside the date range box
        self.btn_export = ttk.Button(top_frame, text="Export", command=self.export_report)
        self.btn_export.pack(side="right", padx=10, pady=5)
        
        # Results panel
        results_frame = ttk.LabelFrame(main_frame, text="Results")
        results_frame.pack(fill="both", expand=True, pady=5)
        
        self.tree = ttk.Treeview(results_frame, columns=("Agent", "VIP", "Crit 50", "Crit 50 Type", "Crit 100", "Crit 100 Type"), show="headings", selectmode="extended")
        
        vsb = ttk.Scrollbar(results_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        
        columns = {"Agent": {"width": 100, "anchor": "w"}, "VIP": {"width": 100, "anchor": "w"}, "Crit 50": {"width": 80, "anchor": "center"}, "Crit 50 Type": {"width": 100, "anchor": "center"}, "Crit 100": {"width": 80, "anchor": "center"}, "Crit 100 Type": {"width": 100, "anchor": "center"}}
        
        for col, settings in columns.items():
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, **settings)
        
        self.tree.pack(fill="both", expand=True)
    
    def generate_report_threaded(self):
        threading.Thread(target=self.generate_report, daemon=True).start()
    
    def generate_report(self):
        try:
            self.current_entries = []
            self.start_date_str = self.start_date.get_date().strftime(DATE_FORMAT)
            self.end_date_str = self.end_date.get_date().strftime(DATE_FORMAT)
            
            if parse_date(self.start_date_str) > parse_date(self.end_date_str):
                messagebox.showerror("Error", "End date cannot be before start date")
                return
            
            for sheet_id in self.sheet_ids:
                try:
                    entries = get_entries_in_range(sheet_id, self.start_date_str, self.end_date_str)
                    self.current_entries.extend(entries)
                except (GoogleSheetsAPIError, DataValidationError) as e:
                    logger.error(f"Error fetching data: {str(e)}")
                    messagebox.showerror("Data Fetch Error", str(e))
                    return
            
            if not self.current_entries:
                messagebox.showinfo("No Entries", "No entries found for selected criteria")
                return
            
            self.update_display()
            
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            messagebox.showerror("Error", "An unexpected error occurred")
    
    def update_display(self):
        self.tree.delete(*self.tree.get_children())
        for idx, entry in enumerate(self.current_entries):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.tree.insert("", "end", values=(
                entry['agent'],
                entry['VIP'],
                entry['crit_50'] or '',
                entry['crit_50_type'],
                entry['crit_100'] or '',
                entry['crit_100_type']
            ), tags=(tag,))
        
        logger.info("Report successfully updated in UI")
    
    def export_report(self):
        try:
            report_path = ReportGenerator.generate_csv_report(self.current_entries, self.start_date_str, self.end_date_str)
            messagebox.showinfo("Export Success", f"Report saved to: {report_path}")
        except Exception as e:
            logger.error(f"Error exporting report: {str(e)}")
            messagebox.showerror("Export Error", str(e))
'''
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
import threading
from config import DATE_FORMAT, SHEET_IDS
from custom_exceptions import GoogleSheetsAPIError, DataValidationError
from log_config import logger
from dates import parse_date
from google_sheets import get_entries_in_range
from report_generator import ReportGenerator

class ReportApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Report Generator")
        self.root.geometry("300x100")
        self.root.resizable(False, False)

        self.sheet_ids = SHEET_IDS
        self.current_entries = []

        self.create_widgets()
    
    def create_widgets(self):
        # Date Range Frame
        control_frame = ttk.LabelFrame(self.root, text="Date Range")
        control_frame.pack(fill="both", padx=5, pady=5)

        # Start Date
        ttk.Label(control_frame, text="From:").pack(side="left", padx=5)
        self.start_date = DateEntry(control_frame, date_pattern=DATE_FORMAT.replace("%", ""), width=12)
        self.start_date.set_date(datetime.now())
        self.start_date.pack(side="left", padx=5)

        # End Date
        ttk.Label(control_frame, text="To:").pack(side="left", padx=5)
        self.end_date = DateEntry(control_frame, date_pattern=DATE_FORMAT.replace("%", ""), width=12)
        self.end_date.set_date(datetime.now())
        self.end_date.pack(side="left", padx=5)

        # Export Button
        self.btn_export = ttk.Button(self.root, text="Export", command=self.generate_report_threaded)
        self.btn_export.pack(pady=5)

    def generate_report_threaded(self):
        """Runs report generation in a separate thread."""
        threading.Thread(target=self.generate_report, daemon=True).start()

    def generate_report(self):
        """Fetches data and exports the report."""
        try:
            self.current_entries = []
            self.start_date_str = self.start_date.get_date().strftime(DATE_FORMAT)
            self.end_date_str = self.end_date.get_date().strftime(DATE_FORMAT)

            if parse_date(self.start_date_str) > parse_date(self.end_date_str):
                messagebox.showerror("Error", "End date cannot be before start date")
                return

            for sheet_id in self.sheet_ids:
                try:
                    entries = get_entries_in_range(sheet_id, self.start_date_str, self.end_date_str)
                    self.current_entries.extend(entries)
                except (GoogleSheetsAPIError, DataValidationError) as e:
                    logger.error(f"Error fetching data: {str(e)}")
                    messagebox.showerror("Data Fetch Error", str(e))
                    return

            if not self.current_entries:
                messagebox.showinfo("No Entries", "No entries found for selected criteria")
                return

            self.export_report()
            
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            messagebox.showerror("Error", "An unexpected error occurred")

    def export_report(self):
        """Exports the fetched data to a CSV report."""
        try:
            report_path = ReportGenerator.generate_csv_report(self.current_entries, self.start_date_str, self.end_date_str)
            messagebox.showinfo("Export Success", f"Report saved to: {report_path}")
        except Exception as e:
            logger.error(f"Error exporting report: {str(e)}")
            messagebox.showerror("Export Error", str(e))

# Run the Application
if __name__ == "__main__":
    root = tk.Tk()
    app = ReportApp(root)
    root.mainloop()