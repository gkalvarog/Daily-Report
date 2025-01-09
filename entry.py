import tkinter as tk
from tkinter import messagebox

def delete_entry(data_entries, tree, dashboard):
    selected_item = tree.selection()
    if not selected_item:
        return
    
    # Remove from tree and data_entries
    item_index = tree.index(selected_item)
    tree.delete(selected_item)
    del data_entries[item_index]
    
    # Update the dashboard after deletion
    update_dashboard(dashboard, data_entries)

def edit_entry(entry_vars, data_entries, tree, dashboard, edit_button):
    selected_item = tree.selection()
    if not selected_item:
        return
    
    # Disable the Edit button while editing
    edit_button.config(state='disabled')

    try:
        item_id = selected_item[0]
        index = tree.index(item_id)
        selected_data = data_entries[index]

        # Populate fields with selected entry data
        entry_vars["Agent:"].delete(0, tk.END)
        entry_vars["Agent:"].insert(0, selected_data.get('Agent', ''))

        entry_vars["Manager:"].set(selected_data.get('Manager', ''))

        entry_vars["Server:"].delete(0, tk.END)
        entry_vars["Server:"].insert(0, selected_data.get('Server', ''))

        entry_vars["Comment:"].delete(0, tk.END)
        entry_vars["Comment:"].insert(0, selected_data.get('Comment', ''))

        entry_vars["Crit50:"].delete(0, tk.END)
        entry_vars["Crit50:"].insert(0, selected_data.get('Crit50', ''))

        entry_vars["Crit50 Comment:"].delete(0, tk.END)
        entry_vars["Crit50 Comment:"].insert(0, selected_data.get('Crit50 Comment', ''))

        entry_vars["Crit100:"].delete(0, tk.END)
        entry_vars["Crit100:"].insert(0, selected_data.get('Crit100', ''))

        entry_vars["Crit100 Comment:"].delete(0, tk.END)
        entry_vars["Crit100 Comment:"].insert(0, selected_data.get('Crit100 Comment', ''))

        # Remove the old entry
        tree.delete(item_id)
        data_entries.pop(index)

        update_dashboard(dashboard, data_entries)
    
    finally:
        return
    
def update_dashboard(dashboard, data_entries):
    """
    Update the dashboard with consolidated data per agent.
    Allows editing of 'General Comment' directly in the dashboard.
    """
    # Clear existing dashboard entries
    for row in dashboard.get_children():
        dashboard.delete(row)
    
    # Aggregate data by agent
    agent_summary = {}
    for entry in data_entries:
        agent = entry['Agent']
        crit50 = entry['Crit50']
        crit100 = entry['Crit100']

        if agent not in agent_summary:
            agent_summary[agent] = {
                'Total Chats': 0,
                'Total Crit50': 0,
                'Total Crit100': 0,
                'General Comment': ''
            }

        agent_summary[agent]['Total Chats'] += 1
        agent_summary[agent]['Total Crit50'] += crit50
        agent_summary[agent]['Total Crit100'] += crit100

    # Populate the dashboard TreeView
    for agent, summary in agent_summary.items():
        dashboard.insert('', 'end', values=(
            agent,
            summary['Total Chats'],
            summary['Total Crit50'],
            summary['Total Crit100'],
            summary['General Comment']
        ))

    # Enable editing of the 'Comment' column
    def on_double_click(event):
        selected_item = dashboard.selection()
        if selected_item:
            column_id = dashboard.identify_column(event.x)
            column = int(column_id.replace('#', '')) - 1

            if column == 4:  # Index of 'General Comment'
                entry_window = tk.Toplevel()
                entry_window.title("Edit General Comment")
                
                tk.Label(entry_window, text="Comment:").pack(padx=5, pady=5)
                comment_entry = tk.Entry(entry_window, width=50)
                comment_entry.pack(padx=5, pady=5)
                
                # Pre-fill with existing comment
                current_comment = dashboard.item(selected_item, 'values')[4]
                comment_entry.insert(0, current_comment)
                
                def save_comment(event=None):
                    new_comment = comment_entry.get()
                    values = list(dashboard.item(selected_item, 'values'))
                    values[4] = new_comment
                    dashboard.item(selected_item, values=values)
                    entry_window.destroy()

                
                comment_entry.bind("<Return>", save_comment)  # Save on Enter
                tk.Button(entry_window, text="Save", command=save_comment).pack(pady=5)
    
    dashboard.bind("<Double-1>", on_double_click)

def clear_crit_fields(entry_vars):
    """
    Clear Crit50, Crit50 Comment, Crit100, and Crit100 Comment fields.
    """
    entry_vars["Crit50:"].delete(0, tk.END)
    entry_vars["Crit50 Comment:"].delete(0, tk.END)
    entry_vars["Crit100:"].delete(0, tk.END)
    entry_vars["Crit100 Comment:"].delete(0, tk.END)

def add_entry(entry_vars, data_entries, tree, dashboard, edit_button):

    tool = entry_vars["Tool:"].get().strip() if "Tool:" in entry_vars else ''
    server = entry_vars["Server:"].get().strip() if "Server:" in entry_vars else ''
    agent = entry_vars["Agent:"].get().strip() if "Agent:" in entry_vars else ''
    manager = entry_vars["Manager:"].get().strip() if "Manager:" in entry_vars else ''

    crit50 = entry_vars["Crit50:"].get().strip() if "Crit50:" in entry_vars else ''
    crit50_comment = entry_vars["Crit50 Comment:"].get().strip() if "Crit50 Comment:" in entry_vars else ''

    crit100 = entry_vars["Crit100:"].get().strip() if "Crit100:" in entry_vars else ''
    crit100_comment = entry_vars["Crit100 Comment:"].get().strip() if "Crit100 Comment:" in entry_vars else ''

    general_comment = entry_vars["General Comment:"].get().strip() if "General Comment:" in entry_vars else ''

    if not agent:
        return

    try:
        crit50 = int(crit50) if crit50 else 0
        crit100 = int(crit100) if crit100 else 0
    except ValueError:
        messagebox.showerror("Invalid Input", "Crit50 and Crit100 must be integers.")
        return
    
    new_entry = {
        'Agent': agent,
        'Manager': manager,
        'Tool': tool,
        'Server': server,
        'Crit50': crit50,
        'Crit50_Comment': crit50_comment,
        'Crit100': crit100,
        'Crit100_Comment': crit100_comment,
        'General_Comment': general_comment
    }

    data_entries.append(new_entry)

    tree.insert('', 'end', values=(
        agent,
        manager,
        crit50,
        crit100
    ))

    update_dashboard(dashboard, data_entries)

    # Clear crit fields after adding an entry
    clear_crit_fields(entry_vars)

    edit_button.config(state='normal')

