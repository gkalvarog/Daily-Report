import datetime
import os
from collections import defaultdict

def generate_report2(data_entries):
    if not data_entries:
        return "No data entered to generate a report."

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    desktop_path = os.path.expanduser("~\\Desktop")
    file_name = f"daily_combined_report_{today}.txt"
    report_path = os.path.join(desktop_path, file_name)

    with open(report_path, 'w', encoding='utf-8') as file:
        # ───────────────────────────────────────────────
        # Section 1: Detailed Report
        # ───────────────────────────────────────────────
        file.write("=== Detailed Report ===\n\n")
        headers = ["Agent", "Tool", "Server", "Manager", "Crit50", "Crit100", "Crit50_Comment", "Crit100_Comment", "General_Comment"]
        file.write("\t".join(headers) + "\n")

        for entry in data_entries:
            row = [
                entry.get('Agent', ''),
                entry.get('Tool', ''),
                entry.get('Server', ''),
                entry.get('Manager', ''),
                str(entry.get('Crit50', 0)),
                str(entry.get('Crit100', 0)),
                entry.get('Crit50_Comment', ''),
                entry.get('Crit100_Comment', ''),
                entry.get('General_Comment', '')
            ]
            file.write("\t".join(row) + "\n")
        
        file.write("\n\n")

        # ───────────────────────────────────────────────
        # Section 2: Summary Report
        # ───────────────────────────────────────────────
        file.write("=== Summary Report ===\n\n")

        # Block 1: Total Chats per Agent
        file.write("[Block 1: Total Chats per Agent]\n")
        agent_chat_count = defaultdict(int)
        for entry in data_entries:
            agent_chat_count[entry.get('Agent', '')] += 1
        for agent, total in agent_chat_count.items():
            file.write(f"{agent}: {total} chats\n")
        file.write("\n")

        # Block 2: Total Chats per Manager
        file.write("[Block 2: Total Chats per Manager]\n")
        manager_chat_count = defaultdict(int)
        for entry in data_entries:
            manager_chat_count[entry.get('Manager', '')] += 1
        for manager, total in manager_chat_count.items():
            file.write(f"{manager}: {total} chats\n")
        file.write("\n")

        # Block 3: Total Crit50 and Crit100 per Agent
        file.write("[Block 3: Total Crit50 and Crit100 per Agent]\n")
        agent_crit_count = defaultdict(lambda: {"Crit50": 0, "Crit100": 0})
        for entry in data_entries:
            agent_crit_count[entry.get('Agent', '')]["Crit50"] += int(entry.get('Crit50', 0))
            agent_crit_count[entry.get('Agent', '')]["Crit100"] += int(entry.get('Crit100', 0))
        for agent, crits in agent_crit_count.items():
            file.write(f"{agent}: Crit50={crits['Crit50']}, Crit100={crits['Crit100']}\n")
        file.write("\n")

        # Block 4: Total Crit50 and Crit100 per Manager
        file.write("[Block 4: Total Crit50 and Crit100 per Manager]\n")
        manager_crit_count = defaultdict(lambda: {"Crit50": 0, "Crit100": 0})
        for entry in data_entries:
            manager_crit_count[entry.get('Manager', '')]["Crit50"] += int(entry.get('Crit50', 0))
            manager_crit_count[entry.get('Manager', '')]["Crit100"] += int(entry.get('Crit100', 0))
        for manager, crits in manager_crit_count.items():
            file.write(f"{manager}: Crit50={crits['Crit50']}, Crit100={crits['Crit100']}\n")
    
    return f"Text report successfully generated:\n- {report_path}"
