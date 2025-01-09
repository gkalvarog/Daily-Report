import tkinter as tk
from tkinter import ttk, messagebox
from report_generator import generate_report
from report_generator2 import generate_report2
from config import predefined_servers, predefined_agents, predefined_managers
from entry import add_entry, edit_entry, delete_entry


def run_app():
    SERVERS = predefined_servers
    TOOLS = ["Telegram", "WhatsApp"]
    AGENTS = predefined_agents
    MANAGERS = predefined_managers

    data_entries = []
    entry_vars = {}

    root = tk.Tk()
    root.title("Daily Evaluation")
    root.geometry("480x700")
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(3, weight=1)
    root.minsize(480, 700)
    root.maxsize(480, 700)


    # Dropdown Fields
    fields_frame = tk.Frame(root)
    fields_frame.grid(row=0, column=0, padx=10, pady=10, sticky='e')

    fields = [
        ("Agent:", AGENTS),
        ("Manager:", MANAGERS),
        # ("Tool:", TOOLS),
        ("Server:", SERVERS),
        ("Comment:", None),
        ("Crit50:", None),
        ("Crit50 Comment:", None),
        ("Crit100:", None),
        ("Crit100 Comment:", None)        
    ]

    left_frame = tk.Frame(fields_frame)
    left_frame.grid(row=0, column=0, sticky='nw')

    right_frame = tk.Frame(fields_frame)
    right_frame.grid(row=0, column=1, sticky='nw')
###
    for i, (label, values) in enumerate(fields[:4]):
        ttk.Label(left_frame, text=label, anchor='w', justify='left').grid(row=i, column=0, padx=5, pady=2, sticky='w')
        if values:
            var = ttk.Combobox(left_frame, values=values)
            if label == "Agent:":
                def filter_agents(event):
                    search_term = var.get().lower()
                    filtered_agents = [agent for agent in AGENTS if search_term in agent.lower()]
                    var['values'] = filtered_agents if filtered_agents else AGENTS

                var.bind("<KeyRelease>", filter_agents)
        else:
            var = tk.Entry(left_frame)
        var.grid(row=i, column=1, padx=5, pady=2, sticky='we')
        entry_vars[label] = var

###
    for i, (label, values) in enumerate(fields[4:]):
        ttk.Label(right_frame, text=label, anchor='w', justify='left').grid(row=i, column=0, padx=5, pady=2, sticky='w')
        if values:
            var = ttk.Combobox(right_frame, values=values)
        else:
            var = tk.Entry(right_frame)
        var.grid(row=i, column=1, padx=5, pady=2, sticky='we')
        entry_vars[label] = var

    left_frame.grid_columnconfigure(1, weight=1)
    right_frame.grid_columnconfigure(1, weight=1)

    # Buttons
    button_frame = tk.Frame(root)
    button_frame.grid(row=1, column=0, pady=5, sticky='ew')
    button_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

    # Add Button
    add_button = ttk.Button(button_frame, text="Add", command=lambda: add_entry(entry_vars, data_entries, tree, dashboard, edit_button))
    add_button.grid(row=0, column=0, padx=5, sticky='ew')

    # Edit Button
    edit_button = ttk.Button(button_frame, text="Edit", command=lambda: edit_entry(entry_vars, data_entries, tree, dashboard, edit_button))
    edit_button.grid(row=0, column=1, padx=5, sticky='ew')

    # Delete Button
    delete_button = ttk.Button(button_frame, text="Delete", command=lambda: delete_entry(data_entries, tree, dashboard))
    delete_button.grid(row=0, column=2, padx=5, sticky='ew')

    # Report Button
    report_button = ttk.Button(button_frame, text="Report", command=lambda: messagebox.showinfo(
        "Info", [generate_report(data_entries), generate_report2(data_entries)]))
    
    report_button.grid(row=0, column=3, padx=5, sticky='ew')


    # TreeView
    tree_frame = tk.LabelFrame(root, text="Data Table")
    tree_frame.grid(row=2, column=0, padx=10, pady=5, sticky='nsew')
    tree_frame.grid_rowconfigure(0, weight=3) 
    tree_frame.grid_columnconfigure(0, weight=1)
    tree_frame.grid_rowconfigure(1, weight=0)  # Horizontal Scrollbar space

    tree_columns = ["Agent", "Manager", "Crit50", "Crit100"]
    tree = ttk.Treeview(tree_frame, columns=tree_columns, show='headings')

    def sort_treeview_column(tree, col, reverse):
        data = [(tree.set(item, col), item) for item in tree.get_children('')]
        data.sort(reverse=reverse)

        for index, (val, item) in enumerate(data):
            tree.move(item, '', index)

        tree.heading(col, command=lambda: sort_treeview_column(tree, col, not reverse))

    for col in tree_columns:
        tree.heading(col, text=col, command=lambda c=col: sort_treeview_column(tree, c, False))
        tree.column(col, width=100)

    # Vertical Scrollbar
    tree_scroll_y = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
    tree.configure(yscrollcommand=tree_scroll_y.set)
    tree_scroll_y.grid(row=0, column=1, sticky='ns')

    # Horizontal Scrollbar
    tree_scroll_x = ttk.Scrollbar(tree_frame, orient='horizontal', command=tree.xview)
    tree.configure(xscrollcommand=tree_scroll_x.set)
    tree_scroll_x.grid(row=1, column=0, sticky='ew')

    tree.grid(row=0, column=0, sticky='nsew')

    # DashBoard View
    dash_frame = tk.LabelFrame(root, text="Dashboard")
    dash_frame.grid(row=3, column=0, padx=10, pady=5, sticky='nsew')
    dash_frame.grid_rowconfigure(0, weight=1)  # Dashboard gets 1/3 height
    dash_frame.grid_columnconfigure(0, weight=1)
    dash_frame.grid_rowconfigure(1, weight=0)  # Horizontal Scrollbar space

    dash_columns = ["Agent", "Chats", "Crit50", "Crit100", "Comments"]
    dashboard = ttk.Treeview(dash_frame, columns=dash_columns, show='headings')
    for col in dash_columns:
        dashboard.heading(col, text=col)
        dashboard.column(col, width=80, stretch=True)

    # Vertical Scrollbar
    dash_scroll_y = ttk.Scrollbar(dash_frame, orient='vertical', command=dashboard.yview)
    dashboard.configure(yscrollcommand=dash_scroll_y.set)
    dash_scroll_y.grid(row=0, column=1, sticky='ns')

    # Horizontal Scrollbar
    dash_scroll_x = ttk.Scrollbar(dash_frame, orient='horizontal', command=dashboard.xview)
    dashboard.configure(xscrollcommand=dash_scroll_x.set)
    dash_scroll_x.grid(row=1, column=0, sticky='ew')

    dashboard.grid(row=0, column=0, sticky='nsew')

    # Adjust responsiveness
    root.grid_rowconfigure(0, weight=3)
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # Initialize a dictionary to store consolidated metrics
    dashboard_data = {}

    # Iterate over Treeview entries to calculate metrics
    for child in tree.get_children():
        entry = tree.item(child)['values']

        agent = entry[0]
        manager = entry[1]
        crit50 = entry[2]
        crit100 = entry[3]
            
        if agent not in dashboard_data:
            dashboard_data[agent] = {'manager': 0,'chats': 0, 'crit50': 0, 'crit100': 0}
            
        # Update metrics
        dashboard_data[agent]['chats'] += 1
        if manager:
            dashboard_data[agent]['manager'] += 1
        if crit50:
            dashboard_data[agent]['crit50'] += 1
        if crit100:
            dashboard_data[agent]['crit100'] += 1

    root.bind("<Return>", lambda event: add_entry(entry_vars, data_entries, tree, dashboard, edit_button))
    tree.bind("<Double-1>", lambda event: edit_entry(entry_vars, data_entries, tree, dashboard, edit_button))


    root.mainloop()