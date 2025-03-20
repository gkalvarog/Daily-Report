import csv
import os
from collections import defaultdict
from config import DATE_FORMAT, REPORT_OUTPUT_DIR
from log_config import logger

class ReportGenerator:
    @staticmethod
    def generate_csv_report(entries, start_date, end_date):
        try:
            os.makedirs(REPORT_OUTPUT_DIR, exist_ok=True)
            report_path = os.path.join(REPORT_OUTPUT_DIR, "report.csv")
            
            logger.info("Generating CSV report...")
            
            # Data aggregation structures
            total_entries_per_employee = defaultdict(int)
            entries_per_employee_per_agent = defaultdict(lambda: defaultdict(int))
            crits_per_employee_per_agent = defaultdict(lambda: defaultdict(int))
            crits_per_agent = defaultdict(lambda: {'50': 0, '100': 0})
            in_progress_per_employee = defaultdict(int)
            missing_employee_id_count = 0
            missing_vip_count = 0
            total_ready_rows = 0  # Global count of 'Ready' rows
            
            # Process entries
            for entry in entries:
                employee_id = entry.get('Employee ID', 'Unknown')
                agent = entry.get('agent', 'Unknown')
                vip = entry.get('VIP', '').strip()
                status = entry.get('status', '').lower()
                
                try:
                    crit_value = int(entry.get('crit', 0))  # Ensure crit is an integer
                except ValueError:
                    crit_value = 0  # Default to 0 if conversion fails
                
                # Count 'Ready' rows for aggregations
                if status == 'ready':
                    total_entries_per_employee[employee_id] += 1
                    entries_per_employee_per_agent[employee_id][agent] += 1
                    if crit_value in [-50, -100]:
                        crits_per_employee_per_agent[employee_id][agent] += 1
                        crits_per_agent[agent][str(abs(crit_value))] += 1  # Store as '50' or '100'
                    total_ready_rows += 1
                
                # Count 'In Progress' statuses separately
                if status == 'in progress':
                    in_progress_per_employee[employee_id] += 1
                
                # Count missing Employee IDs
                if not employee_id.strip() or employee_id == 'Unknown':
                    missing_employee_id_count += 1
                
                # Count missing VIPs
                if not vip:
                    missing_vip_count += 1
            
            # Write to CSV
            with open(report_path, 'w', newline='', encoding='utf-8') as csvfile:
                csv_writer = csv.writer(csvfile)
                
                # Write period
                csv_writer.writerow(["Report Period:", f"{start_date} - {end_date}"])
                csv_writer.writerow([])
                
                # Global count of Ready rows
                csv_writer.writerow(["Global Count of Ready Rows", total_ready_rows])
                csv_writer.writerow([])
                
                # Total entries per Employee ID
                csv_writer.writerow(["Total Entries per Employee ID (Ready Only)"])
                csv_writer.writerow(["Employee ID", "Total Entries"])
                for employee_id, count in total_entries_per_employee.items():
                    csv_writer.writerow([employee_id, count])
                csv_writer.writerow([])
                
                # Entries per Employee ID per Agent
                csv_writer.writerow(["Entries per Employee ID per Agent (Ready Only)"])
                csv_writer.writerow(["Employee ID", "Agent", "Entries"])
                for employee_id, agents in entries_per_employee_per_agent.items():
                    for agent, count in agents.items():
                        csv_writer.writerow([employee_id, agent, count])
                csv_writer.writerow([])
                
                # Crits per Employee ID per Agent
                csv_writer.writerow(["Crits per Employee ID per Agent (Ready Only)"])
                csv_writer.writerow(["Employee ID", "Agent", "Total Crits"])
                for employee_id, agents in crits_per_employee_per_agent.items():
                    for agent, count in agents.items():
                        csv_writer.writerow([employee_id, agent, count])
                csv_writer.writerow([])
                
                # Crit count per Agent
                csv_writer.writerow(["Crit 50 & 100 per Agent (Ready Only)"])
                csv_writer.writerow(["Agent", "Crit 50", "Crit 100"])
                for agent, crit_counts in crits_per_agent.items():
                    csv_writer.writerow([agent, crit_counts['50'], crit_counts['100']])
                csv_writer.writerow([])
                
                # In Progress per Employee ID
                csv_writer.writerow(["In Progress per Employee ID"])
                csv_writer.writerow(["Employee ID", "In Progress Entries"])
                for employee_id, count in in_progress_per_employee.items():
                    csv_writer.writerow([employee_id, count])
                csv_writer.writerow([])
                
                # Missing Data Counts
                csv_writer.writerow(["Missing Data Counts"])
                csv_writer.writerow(["Missing Employee ID Entries", missing_employee_id_count])
                csv_writer.writerow(["Missing VIP Entries", missing_vip_count])
                
            logger.info(f"CSV report successfully generated: {report_path}")
            return report_path
        except Exception as e:
            logger.error(f"Error generating CSV report: {str(e)}")
            raise