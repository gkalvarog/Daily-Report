from collections import defaultdict
import tkinter as tk
from tkinter import ttk, messagebox
from openpyxl import Workbook
import datetime
import os

# List to store agent data
data_entries = []

# Function to process VIP and Crit50
def process_data(data):
    vip_area = []
    crit50_area = []
    crit100_area = []
    
    
    for item in data:
        if item['type'] == 'VIP':
            # Process VIP items
            vip_area.append(item)
        elif item['type'] == 'Crit50':
            # Process Crit 50 items
            crit50_area.append(item)
        elif item['type'] == 'Crit100':
            # Process Crit 100 items
            crit100_area.append(item)
        else:
            print(f"Unrecognized type: {item['type']}")
    
    return vip_area, crit50_area, crit100_area

# Function to add entry
def add_entry():
    name = dropdown_name.get().strip()
    tool = dropdown_tool.get()
    server = dropdown_server.get().strip()
    vip = dropdown_vip.get().strip()
    crit_50 = entry_crit50.get().strip()
    crit_100 = entry_crit100.get().strip()
    note_crit50 = entry_note_crit50.get().strip()
    note_crit100 = entry_note_crit100.get().strip()
    general_note = entry_general_note.get().strip()

    if not name:
        messagebox.showerror("Invalid Input", "Please fill in at least Name and VIP required fields.")
        return

    # Prepare data for processing
    input_data = [
        {'type': 'VIP', 'value': vip},
        {'type': 'Crit50', 'value': crit_50},
        {'type': 'Crit100', 'value': crit_100}
    ]
    
    # Process VIP and Crit50
    vip_result, crit50_result, crit100_result = process_data(input_data)
    
    # Add data to the list
    new_entry = {
        'Name': name,
        'Tool': tool,
        'Server': server,
        'VIP': vip_result[0]['value'] if vip_result else vip,
        'Crit50': crit50_result[0]['value'] if crit50_result else crit_50,
        'Crit100': crit100_result[0]['value'] if crit100_result else crit_100,
        'NoteCrit50': note_crit50,
        'NoteCrit100': note_crit100,
        'GeneralNote': general_note
    }

    data_entries.append(new_entry)

    # Update the Treeview table
    tree.insert('', 'end', values=(
        name, new_entry['VIP'], new_entry['Crit50'], new_entry['Crit100']
    ))

    # Clear input fields (except for name, vip and server, as these shall repeat)
    entry_crit50.delete(0, tk.END)
    entry_crit100.delete(0, tk.END)
    entry_note_crit50.delete(0, tk.END)
    entry_note_crit100.delete(0, tk.END)
    entry_general_note.delete(0, tk.END)

# Function to edit selected entry
def edit_entry():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("No Selection", "Please select an entry to edit.")
        return

    item_id = selected_item[0]
    index = tree.index(item_id)
    selected_data = data_entries[index]

    # Populate fields with selected entry data
    dropdown_name.delete(0, tk.END)
    dropdown_name.insert(0, selected_data['Name'])
    dropdown_tool.set(selected_data['Tool'])
    dropdown_server.delete(0, tk.END)
    dropdown_server.insert(0, selected_data['Server'])
    dropdown_vip.delete(0, tk.END)
    dropdown_vip.insert(0, selected_data['VIP'])
    entry_crit50.delete(0, tk.END)
    entry_crit50.insert(0, selected_data['Crit50'])
    entry_crit100.delete(0, tk.END)
    entry_crit100.insert(0, selected_data['Crit100'])
    entry_note_crit50.delete(0, tk.END)
    entry_note_crit50.insert(0, selected_data['NoteCrit50'])
    entry_note_crit100.delete(0, tk.END)
    entry_note_crit100.insert(0, selected_data['NoteCrit100'])
    entry_general_note.delete(0, tk.END)
    entry_general_note.insert(0, selected_data['GeneralNote'])

    # Remove the old entry
    tree.delete(item_id)
    data_entries.pop(index)

# Function to delete selected entry
def delete_entry():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("No Selection", "Please select an entry to delete.")
        return

    for item in selected_item:
        index = tree.index(item)
        tree.delete(item)
        data_entries.pop(index)

# Function to generate report as .xlsx file
def generate_report():
    if not data_entries:
        messagebox.showwarning("No Data", "No data entered to generate a report.")
        return

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Daily Report"

    # Write headers
    headers = ["Name", "Tool", "Server", "VIP", "Crit50", "Crit100", "NoteCrit50", "NoteCrit100", "GeneralNote"]
    sheet.append(headers)

    # Write data entries
    for entry in data_entries:
        sheet.append([
            entry['Name'], entry['Tool'], entry['Server'], entry['VIP'],
            entry['Crit50'], entry['Crit100'], entry['NoteCrit50'], entry['NoteCrit100'], entry['GeneralNote']
        ])

    # Save file to Desktop
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    file_name = f"daily_report_{today}.xlsx"
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", file_name)
    workbook.save(desktop_path)

    messagebox.showinfo("Report Generated", f"Report successfully generated: {desktop_path}")

# Function to show dashboard
def show_dashboard():
    # Initialize a dictionary to store consolidated metrics
    dashboard_data = {}

    # Iterate over Treeview entries to calculate metrics
    for child in tree.get_children():
        entry = tree.item(child)['values']
        agent = entry[0]
        vip = entry[1]
        crit50 = entry[2]
        crit100 = entry[3]
        key = (agent, vip)
        
        if key not in dashboard_data:
            dashboard_data[key] = {'chats': 0, 'crit50': 0, 'crit100': 0}
        
        # Update metrics
        dashboard_data[key]['chats'] += 1
        if crit50:
            dashboard_data[key]['crit50'] += 1
        if crit100:
            dashboard_data[key]['crit100'] += 1
    
    # Display results in a table format
    dashboard_window = tk.Toplevel()
    dashboard_window.title("Dashboard")
    
    # Create a frame for Treeview and scrollbars
    frame = tk.Frame(dashboard_window)
    frame.pack(fill='both', expand=True)
    
    columns = ("Agent", "VIP", "Chats", "Crit 50", "Crit 100")
    dashboard_tree = ttk.Treeview(frame, columns=columns, show='headings')
    
    for col in columns:
        dashboard_tree.heading(col, text=col)
        dashboard_tree.column(col, width=150)
    
    for (agent, vip), metrics in dashboard_data.items():
        dashboard_tree.insert('', 'end', values=(agent, vip, metrics['chats'], metrics['crit50'], metrics['crit100']))
    
    # Add vertical scrollbar
    v_scroll = ttk.Scrollbar(frame, orient='vertical', command=dashboard_tree.yview)
    dashboard_tree.configure(yscroll=v_scroll.set)
    v_scroll.pack(side='right', fill='y')
    
    # Add horizontal scrollbar
    h_scroll = ttk.Scrollbar(frame, orient='horizontal', command=dashboard_tree.xview)
    dashboard_tree.configure(xscroll=h_scroll.set)
    h_scroll.pack(side='bottom', fill='x')
    
    dashboard_tree.pack(fill='both', expand=True)
    dashboard_window.mainloop()


# GUI Setup
root = tk.Tk()
root.title("Daily Evaluation System")
root.geometry("600x600")

# Configure grid weights for responsiveness
root.grid_rowconfigure(2, weight=1)
root.grid_columnconfigure(0, weight=1)

# Input Fields
frame = tk.Frame(root)
frame.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
frame.grid_columnconfigure(1, weight=1)

# Predefined names, VIPs and servers
predefined_names = ["Sandra", "Nicolau", "Amanda", "Vitor", "Ana", "Rossana ", "Siro Vandeste", "Ramon", "Babela", "Lopes", "Jotino Sebastião"]
predefined_vips = ["Marcia Chavito", "Jose Andre", "Augusta Cachinduco", "Joaquim Manuel", "Aguiar Julia", "Pires Hetaelva", "Tonisha Cristiane", "Juliana Lima", "Mauro Caianda", "Simão ", "Magda", "David Tenente", "Ariete", "Jose Alberto", "Lucas", "Antonio Capemba", "Gabriel Oliveira", "Luan", "Junior Paciencia", "Candido Coxi", "Iracena Vieira", "Kamille", "Alberto Muanha", "Kikas Manuel", "Fernandes Antonio", "Antonio Jesus Joao Saraiva", "Venancio Gomes", "Daniel Marcelino", "Renato Francisco", "Kuingo Sebastiao", "Ribeiro Filomeno", "Marcos Simiao", "Gomes Hermenio"]
predefined_servers = ["Qa_Burg1.4", "Live_Burg3.1", "Qa_Burg1.2", "Live_Burg3.2", "Qa_Burg1.3", "Live_Burg3.3", "Brazil_QA1.1", "Other"]

# Fields
fields = [
    ("Agent Name:", ttk.Combobox, "dropdown_name"),
    ("Tool:", ttk.Combobox, "dropdown_tool"),
    ("Server:", ttk.Combobox, "dropdown_server"),
    ("VIP:", ttk.Combobox, "dropdown_vip"),
    ("Crit 50:", tk.Entry, "entry_crit50"),
    ("Note for Crit 50:", tk.Entry, "entry_note_crit50"),
    ("Crit 100:", tk.Entry, "entry_crit100"),
    ("Note for Crit 100:", tk.Entry, "entry_note_crit100"),
    ("General Note:", tk.Entry, "entry_general_note")
]

variables = {}

for i, (label_text, widget_class, var_name) in enumerate(fields):
    tk.Label(frame, text=label_text).grid(row=i, column=0, sticky="w")
    widget = widget_class(frame)
    widget.grid(row=i, column=1, padx=10, pady=5, sticky="w")
    variables[var_name] = widget

# Assign variables
dropdown_name = variables['dropdown_name']
dropdown_tool = variables['dropdown_tool']
dropdown_server = variables['dropdown_server']
dropdown_vip = variables['dropdown_vip']
entry_crit50 = variables['entry_crit50']
entry_crit100 = variables['entry_crit100']
entry_note_crit50 = variables['entry_note_crit50']
entry_note_crit100 = variables['entry_note_crit100']
entry_general_note = variables['entry_general_note']

# Dropdown setup
dropdown_tool['values'] = ["Telegram", "WhatsApp"]
dropdown_name['values'] = predefined_names
dropdown_vip['values'] = predefined_vips
dropdown_server['values'] = predefined_servers

# Buttons
button_frame = tk.Frame(root)
button_frame.grid(row=1, column=0, pady=10, sticky="w")
button_frame.grid_columnconfigure(0, weight=1)

buttons = [
    ("Add Entry", add_entry),
    ("Edit Selected", edit_entry),
    ("Delete Selected", delete_entry),
    ("Generate Report", generate_report),
    ("Show Dashboard", show_dashboard)
]

for i, (btn_text, command) in enumerate(buttons):
    tk.Button(button_frame, text=btn_text, command=command).grid(row=0, column=i, padx=10, sticky='w')

# Treeview
tree_frame = tk.Frame(root)
tree_frame.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")

# Configure grid weights for Treeview
tree_frame.grid_rowconfigure(0, weight=1)
tree_frame.grid_columnconfigure(0, weight=1)

tree = ttk.Treeview(tree_frame, columns=["Name", "VIP", "Crit50", "Crit100"], show="headings")

for col in ["Name", "VIP", "Crit50", "Crit100"]:
    tree.heading(col, text=col)
    tree.column(col, width=50)

tree.pack(fill="both", expand=True)

# Run the App
root.mainloop()