# Copyright (c) 2026, RAhmed-Dev and contributors
# For license information, please see license.txt

"""
GL Scheduler for Nexus Books

Runs hourly to post pending Financial Transactions to ERPNext GL.
Decoupled from transaction submit so that ERPNext availability never
blocks recording a transaction in nexus_books.
"""

import frappe
from frappe import _


def post_pending_gl_entries():
	"""Scheduler job: attempt ERPNext GL posting for all pending transactions.

	Called hourly via hooks.py scheduler_events.
	Fetches submitted Financial Transactions with gl_status = 'pending'
	and attempts GL posting for each. Sets gl_status to 'posted' on success
	or 'failed' (with gl_error) on failure.

	Skips transactions where erpnext_origin = 1 — those were imported from
	ERPNext and must never be pushed back.
	"""
	pending_transactions = frappe.get_all(
		"Financial Transaction",
		filters={"gl_status": "pending", "docstatus": 1, "erpnext_origin": 0},
		fields=["name"],
		limit=100,
	)

	for row in pending_transactions:
		try:
			txn = frappe.get_doc("Financial Transaction", row.name)
			txn._attempt_gl_posting()
			frappe.db.commit()
		except Exception as gl_error:
			frappe.db.rollback()
			frappe.log_error(
				message=str(gl_error),
				title=f"GL Scheduler Failed: {row.name}",
			)
			# Mark as failed so the user can see it in Sync Errors sheet
			frappe.db.set_value(
				"Financial Transaction",
				row.name,
				{
					"gl_status": "failed",
					"gl_error": str(gl_error),
				},
			)
			frappe.db.commit()
