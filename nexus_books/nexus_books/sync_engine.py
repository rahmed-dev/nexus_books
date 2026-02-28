# Copyright (c) 2026, RAhmed-Dev and contributors
# For license information, please see license.txt

"""
Sync Engine for Nexus Books

Smart routing logic that creates appropriate ERPNext documents based on transaction type:
- Income + Customer → Sales Invoice
- Income (no customer) → Journal Entry
- Expense + Supplier → Purchase Invoice
- Expense (no supplier) → Journal Entry
- Transfer → Journal Entry (Bank Entry)
"""

import frappe
from frappe import _
from frappe.utils import flt, getdate


@frappe.whitelist()
def sync_transaction_to_erpnext(transaction_data):
	"""Create Financial Transaction from offline queue and sync to ERPNext.

	Accepts raw transaction data from the Nexus PWA IndexedDB offline queue.
	Inserts and submits a Financial Transaction document — the controller's
	on_submit() routes to Sales Invoice, Purchase Invoice, or Journal Entry
	based on transaction type and party.

	Args:
		transaction_data (dict|str): Transaction payload from the PWA offline queue

	Returns:
		dict: {status, reference_doctype, reference_name, transaction_name}
	"""
	import json

	if isinstance(transaction_data, str):
		transaction_data = json.loads(transaction_data)

	try:
		txn = frappe.get_doc({
			"doctype": "Financial Transaction",
			"transaction_type": transaction_data.get("transaction_type"),
			"date": transaction_data.get("date"),
			"category": transaction_data.get("category") or None,
			"amount": flt(transaction_data.get("amount", 0)),
			"customer": transaction_data.get("customer") or None,
			"supplier": transaction_data.get("supplier") or None,
			"payment_account": transaction_data.get("payment_account") or None,
			"tax_amount": flt(transaction_data.get("tax_amount", 0)),
			"description": transaction_data.get("description", ""),
			"receipt_image": transaction_data.get("receipt_image") or None,
			"tags": transaction_data.get("tags", ""),
		})

		txn.insert(ignore_permissions=True)
		txn.submit()
		frappe.db.commit()

		return {
			"status": "success",
			"reference_doctype": txn.reference_document,
			"reference_name": txn.dynamic_link_knor,
			"transaction_name": txn.name,
		}

	except Exception as sync_error:
		frappe.db.rollback()
		frappe.log_error(message=str(sync_error), title="Transaction Sync Failed")
		return {
			"status": "failed",
			"error": str(sync_error),
		}


def create_sales_invoice(txn, income_account):
	"""Create Sales Invoice for customer income.

	Args:
		txn: Financial Transaction document
		income_account (str): Income GL Account from category

	Returns:
		dict: Created document info
	"""
	category = frappe.get_cached_doc("Transaction Category", txn.category)
	income_item = category.item if category.item else get_or_create_generic_item("Income Item", "Service")

	sales_invoice = frappe.get_doc({
		"doctype": "Sales Invoice",
		"customer": txn.customer,
		"posting_date": getdate(txn.date),
		"due_date": getdate(txn.date),
		"items": [{
			"item_code": income_item,
			"qty": 1,
			"rate": flt(txn.amount),
			"income_account": income_account,
			"description": txn.description or _("Income from Nexus Books")
		}]
	})

	if txn.receipt_image:
		add_attachment_to_doc(sales_invoice, txn.receipt_image)

	sales_invoice.insert(ignore_permissions=True)

	settings = frappe.get_single("Nexus Books Settings")
	if settings.auto_submit_documents:
		sales_invoice.submit()

	return {"doctype": "Sales Invoice", "name": sales_invoice.name}


def create_purchase_invoice(txn, expense_account):
	"""Create Purchase Invoice for supplier expense.

	Args:
		txn: Financial Transaction document
		expense_account (str): Expense GL Account from category

	Returns:
		dict: Created document info
	"""
	category = frappe.get_cached_doc("Transaction Category", txn.category)
	expense_item = category.item if category.item else get_or_create_generic_item("Expense Item", "Service")

	purchase_invoice = frappe.get_doc({
		"doctype": "Purchase Invoice",
		"supplier": txn.supplier,
		"posting_date": getdate(txn.date),
		"bill_date": getdate(txn.date),
		"items": [{
			"item_code": expense_item,
			"qty": 1,
			"rate": flt(txn.amount),
			"expense_account": expense_account,
			"description": txn.description or _("Expense from Nexus Books")
		}]
	})

	if txn.receipt_image:
		add_attachment_to_doc(purchase_invoice, txn.receipt_image)

	purchase_invoice.insert(ignore_permissions=True)

	settings = frappe.get_single("Nexus Books Settings")
	if settings.auto_submit_documents:
		purchase_invoice.submit()

	return {"doctype": "Purchase Invoice", "name": purchase_invoice.name}


def create_journal_entry(txn, category_account):
	"""Create Journal Entry for transactions without party or transfers.

	Args:
		txn: Financial Transaction document
		category_account (str): GL Account from category

	Returns:
		dict: Created document info
	"""
	accounts = get_journal_accounts(txn, category_account)

	journal_entry = frappe.get_doc({
		"doctype": "Journal Entry",
		"posting_date": getdate(txn.date),
		"voucher_type": get_voucher_type(txn.transaction_type),
		"user_remark": txn.description or _("Transaction from Nexus Books"),
		"accounts": accounts
	})

	if txn.receipt_image:
		add_attachment_to_doc(journal_entry, txn.receipt_image)

	journal_entry.insert(ignore_permissions=True)

	settings = frappe.get_single("Nexus Books Settings")
	if settings.auto_submit_documents:
		journal_entry.submit()

	return {"doctype": "Journal Entry", "name": journal_entry.name}


def get_journal_accounts(txn, category_account):
	"""Build journal entry accounts based on transaction type.

	Args:
		txn: Financial Transaction document
		category_account (str): GL Account from category

	Returns:
		list: Journal entry accounts array
	"""
	if not txn.payment_account:
		frappe.throw(_("Payment Account is required for Journal Entry"))

	amount = flt(txn.amount)
	accounts = []

	if txn.transaction_type == "Income":
		accounts.append({"account": txn.payment_account, "debit_in_account_currency": amount})
		accounts.append({"account": category_account, "credit_in_account_currency": amount})

	elif txn.transaction_type == "Expense":
		accounts.append({"account": category_account, "debit_in_account_currency": amount})
		accounts.append({"account": txn.payment_account, "credit_in_account_currency": amount})

	elif txn.transaction_type in ["Transfer", "Correction"]:
		accounts.append({"account": category_account, "debit_in_account_currency": amount})
		accounts.append({"account": txn.payment_account, "credit_in_account_currency": amount})

	return accounts


def get_voucher_type(transaction_type):
	"""Get appropriate Journal Entry voucher type.

	Args:
		transaction_type (str): Transaction type

	Returns:
		str: Voucher type
	"""
	voucher_map = {
		"Income": "Journal Entry",
		"Expense": "Journal Entry",
		"Transfer": "Bank Entry"
	}
	return voucher_map.get(transaction_type, "Journal Entry")


def get_or_create_generic_item(item_name, item_group="Service"):
	"""Get or create a generic non-stock item for invoices.

	Args:
		item_name (str): Item name / code
		item_group (str): Item group

	Returns:
		str: Item code
	"""
	if frappe.db.exists("Item", item_name):
		return item_name

	item = frappe.get_doc({
		"doctype": "Item",
		"item_code": item_name,
		"item_name": item_name,
		"item_group": item_group,
		"stock_uom": "Nos",
		"is_stock_item": 0
	})
	item.insert(ignore_permissions=True)
	frappe.db.commit()

	return item.name


def add_attachment_to_doc(doc, file_url):
	"""Add attachment reference to document.

	Args:
		doc: Frappe document
		file_url (str): File URL
	"""
	pass


@frappe.whitelist()
def get_pending_transactions(limit=50):
	"""Get list of unsynced transactions.

	Args:
		limit (int): Number of transactions to return

	Returns:
		list: Pending transactions
	"""
	return frappe.get_all(
		"Financial Transaction",
		filters={"synced": 0, "docstatus": ["<", 2]},
		fields=["name", "transaction_type", "date", "amount", "category"],
		order_by="date desc",
		limit=limit
	)


@frappe.whitelist()
def bulk_sync_transactions(transaction_names):
	"""Sync multiple transactions in bulk.

	Args:
		transaction_names (list): List of transaction names

	Returns:
		dict: Bulk sync results with success and failed lists
	"""
	if isinstance(transaction_names, str):
		import json
		transaction_names = json.loads(transaction_names)

	results = {"success": [], "failed": []}

	for txn_name in transaction_names:
		result = sync_transaction_to_erpnext(txn_name)
		if result.get("status") == "success":
			results["success"].append(txn_name)
		else:
			results["failed"].append({"name": txn_name, "error": result.get("error")})

	return results
