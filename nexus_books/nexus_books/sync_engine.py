# Copyright (c) 2026, RAhmed-Dev and contributors
# For license information, please see license.txt

"""
Sync Engine for Nexus Books

Receives transaction payloads from the PWA IndexedDB offline queue,
creates a Financial Transaction document, and submits it.

The Financial Transaction controller (financial_transaction.py) handles
all GL routing logic (SI / PI / JE) and deferred GL posting when
accounts are not yet configured.
"""

import json

import frappe
from frappe import _
from frappe.utils import flt


@frappe.whitelist()
def sync_transaction_to_erpnext(transaction_data):
	"""Create and submit a Financial Transaction from the PWA offline queue.

	Args:
		transaction_data (dict|str): Transaction payload from IndexedDB

	Returns:
		dict: {status, transaction_name, gl_status, reference_doctype, reference_name}
	"""
	if isinstance(transaction_data, str):
		transaction_data = json.loads(transaction_data)

	try:
		txn = frappe.get_doc({
			"doctype": "Financial Transaction",
			"transaction_type": transaction_data.get("transaction_type"),
			"date": transaction_data.get("date"),
			"category": transaction_data.get("category") or None,
			"amount": flt(transaction_data.get("amount", 0)),
			"tax_amount": flt(transaction_data.get("tax_amount", 0)),
			"customer": transaction_data.get("customer") or None,
			"supplier": transaction_data.get("supplier") or None,
			"nexus_account": transaction_data.get("nexus_account") or None,
			"to_nexus_account": transaction_data.get("to_nexus_account") or None,
			"description": transaction_data.get("description", ""),
			"receipt_image": transaction_data.get("receipt_image") or None,
			"tags": transaction_data.get("tags", ""),
		})

		txn.insert(ignore_permissions=True)
		txn.submit()
		frappe.db.commit()

		return {
			"status": "success",
			"transaction_name": txn.name,
			"gl_status": txn.gl_status,
			"reference_doctype": txn.reference_document,
			"reference_name": txn.dynamic_link_knor,
		}

	except Exception as sync_error:
		frappe.db.rollback()
		frappe.log_error(message=str(sync_error), title="Transaction Sync Failed")
		return {
			"status": "failed",
			"error": str(sync_error),
		}


@frappe.whitelist()
def get_pending_sync_transactions(limit=50):
	"""Get Financial Transactions with gl_status = pending.

	Args:
		limit (int): Max records to return

	Returns:
		list: Transactions pending GL posting
	"""
	return frappe.get_all(
		"Financial Transaction",
		filters={"gl_status": "pending", "docstatus": 1},
		fields=["name", "transaction_type", "date", "amount", "category", "gl_error"],
		order_by="date desc",
		limit=limit,
	)
