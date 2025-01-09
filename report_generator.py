from openpyxl import Workbook
import datetime
import os
from collections import defaultdict

def generate_report(data_entries):
    if not data_entries:
        return "No data entered to generate a report."

    workbook = Workbook()
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    desktop_path = os.path.expanduser("~\\Desktop")
    file_name = f"daily_combined_report_{today}.xlsx"
    report_path = os.path.join(desktop_path, file_name)

    # ─────────────────────────────────────────────────────
    # Sheet 1: Detailed Report
    # ─────────────────────────────────────────────────────
    detailed_sheet = workbook.active
    detailed_sheet.title = "Detailed Report"
    
    headers = ["Agent", "Tool", "Server", "Manager", "Crit50", "Crit100", "Crit50_Comment", "Crit100_Comment", "General_Comment"]
    detailed_sheet.append(headers)

    for entry in data_entries:
        detailed_sheet.append([
            entry.get('Agent', ''),
            entry.get('Tool', ''),
            entry.get('Server', ''),
            entry.get('Manager', ''),
            entry.get('Crit50', 0),
            entry.get('Crit100', 0),
            entry.get('Crit50_Comment', ''),
            entry.get('Crit100_Comment', ''),
            entry.get('General_Comment', '')
        ])

    # ─────────────────────────────────────────────────────
    # Sheet 2: Summary Report
    # ─────────────────────────────────────────────────────
    summary_sheet = workbook.create_sheet(title="Summary Report")

    # Block 1: Total Chats per Agent
    summary_sheet.append(["Block 1: Total Chats per Agent"])
    summary_sheet.append(["Agent", "Total Chats"])
    agent_chat_count = defaultdict(int)
    for entry in data_entries:
        agent_chat_count[entry.get('Agent', '')] += 1
    for agent, total in agent_chat_count.items():
        summary_sheet.append([agent, total])
    summary_sheet.append([])

    # Block 2: Total Chats per Manager
    summary_sheet.append(["Block 2: Total Chats per Manager"])
    summary_sheet.append(["Manager", "Total Chats"])
    manager_chat_count = defaultdict(int)
    for entry in data_entries:
        manager_chat_count[entry.get('Manager', '')] += 1
    for manager, total in manager_chat_count.items():
        summary_sheet.append([manager, total])
    summary_sheet.append([])

    # Block 3: Total Crit50 and Crit100 per Agent
    summary_sheet.append(["Block 3: Total Crit50 and Crit100 per Agent"])
    summary_sheet.append(["Agent", "Total Crit50", "Total Crit100"])
    agent_crit_count = defaultdict(lambda: {"Crit50": 0, "Crit100": 0})
    for entry in data_entries:
        agent_crit_count[entry.get('Agent', '')]["Crit50"] += int(entry.get('Crit50', 0))
        agent_crit_count[entry.get('Agent', '')]["Crit100"] += int(entry.get('Crit100', 0))
    for agent, crits in agent_crit_count.items():
        summary_sheet.append([agent, crits["Crit50"], crits["Crit100"]])
    summary_sheet.append([])

    # Block 4: Total Crit50 and Crit100 per Manager
    summary_sheet.append(["Block 4: Total Crit50 and Crit100 per Manager"])
    summary_sheet.append(["Manager", "Total Crit50", "Total Crit100"])
    manager_crit_count = defaultdict(lambda: {"Crit50": 0, "Crit100": 0})
    for entry in data_entries:
        manager_crit_count[entry.get('Manager', '')]["Crit50"] += int(entry.get('Crit50', 0))
        manager_crit_count[entry.get('Manager', '')]["Crit100"] += int(entry.get('Crit100', 0))
    for manager, crits in manager_crit_count.items():
        summary_sheet.append([manager, crits["Crit50"], crits["Crit100"]])

    workbook.save(report_path)

    return f"Report successfully generated:\n- {report_path}"
