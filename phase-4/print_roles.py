table = """
+------------+----------------------+--------------------------------------------------------------+
| Role       | Access Level & Scope | Permitted Endpoints & Permissions                            |
+------------+----------------------+--------------------------------------------------------------+
| Admin      | Full System Access   | /admin/dashboard, Full CRUD (Employees, Expenses, Payroll)   |
| HR         | Management Access    | /employees, /payslips/{id} (all records), Expenses & Vendors |
| Employee   | Self-Service Scope   | /payslips/{employee_id} (strictly own record only)           |
+------------+----------------------+--------------------------------------------------------------+
"""

print("\n--- LEDGER FORCE RBAC ACCESS CONTROL MATRIX ---")
print(table)