# Copyright (c) 2026, RAhmed-Dev and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate


class FinancialTransaction(Document):
	def validate(self):
		"""Validate Financial Transaction before save."""
		self.validate_amounts()
		self.validate_party_selection()
		self.validate_category_type()
		self.validate_transfer_accounts()

	def validate_amounts(self):
		"""Validate amount fields are positive."""
		if flt(self.amount) <= 0:
			frappe.throw(_("Amount must be greater than zero"))

		if self.tax_amount and flt(self.tax_amount) < 0:
			frappe.throw(_("Tax amount cannot be negative"))

	def validate_party_selection(self):
		"""Validate party fields based on transaction type."""
		if self.customer and self.supplier:
			frappe.throw(_("Cannot select both Customer and Supplier"))

		if self.transaction_type == "Income" and self.supplier:
			frappe.throw(_("Income transactions should use a Customer, not Supplier"))

		if self.transaction_type == "Expense" and self.customer:
			frappe.throw(_("Expense transactions should use a Supplier, not Customer"))

	def validate_category_type(self):
		"""Validate category type matches transaction type (skipped for Transfer)."""
		if not self.category or self.transaction_type == "Transfer":
			return

		category_doc = frappe.get_cached_doc("Transaction Category", self.category)

		if self.transaction_type == "Income" and category_doc.category_type != "Income":
			frappe.throw(_("Income transaction must use an Income category"))

		if self.transaction_type == "Expense" and category_doc.category_type != "Expense":
			frappe.throw(_("Expense transaction must use an Expense category"))

	def validate_transfer_accounts(self):
		"""Transfer requires both from and to Nexus Accounts, and they must differ."""
		if self.transaction_type != "Transfer":
			return

		if not self.to_nexus_account:
			frappe.throw(_("Transfer requires a destination account (To Account)"))

		if self.nexus_account == self.to_nexus_account:
			frappe.throw(_("From Account and To Account must be different"))

	def on_submit(self):
		"""Queue transaction for background GL posting.

		ERPNext GL posting is handled by the hourly gl_scheduler — this keeps
		transaction recording fast and independent of ERPNext availability.
		Transactions imported from ERPNext (erpnext_origin=1) are never posted back.
		"""
		if self.erpnext_origin:
			self.db_set("gl_status", "erpnext_origin")
			return
		self.db_set("gl_status", "pending")

	def _attempt_gl_posting(self):
		"""Attempt ERPNext GL posting. Called by gl_scheduler, not on_submit.

		Raises exceptions on failure — caller (scheduler) catches and records them.
		"""
		if self.transaction_type == "Transfer":
			self._attempt_transfer_journal_entry()
		elif self.transaction_type == "Income":
			self._attempt_income_gl_posting()
		elif self.transaction_type == "Expense":
			self._attempt_expense_gl_posting()

	def on_cancel(self):
		"""Cancel the linked ERPNext GL document if one was created."""
		if not (self.reference_document and self.dynamic_link_knor):
			return

		try:
			linked_doc = frappe.get_doc(self.reference_document, self.dynamic_link_knor)
			if linked_doc.docstatus == 1:
				linked_doc.cancel()
		except frappe.DoesNotExistError:
			pass  # Already deleted — nothing to cancel

		self.db_set("gl_status", "skipped")

	# --- GL posting attempts (never throw — defer to pending) ---

	def _attempt_income_gl_posting(self):
		"""Post Income transaction to GL as Sales Invoice or Journal Entry."""
		category = frappe.get_cached_doc("Transaction Category", self.category)

		if self.customer:
			# Sales Invoice path — item required (from category or generic)
			gl_doc = self._create_sales_invoice(category)
		else:
			# Journal Entry path — needs gl_account on category + linked nexus account
			gl_account = category.gl_account
			payment_gl_account = self._resolve_nexus_gl_account(self.nexus_account)
			if not gl_account or not payment_gl_account:
				self._defer_gl_posting("Income GL Account or Nexus Account GL link not configured")
				return
			gl_doc = self._create_income_journal_entry(gl_account, payment_gl_account)

		self._record_gl_success(gl_doc)

	def _attempt_expense_gl_posting(self):
		"""Post Expense transaction to GL as Purchase Invoice or Journal Entry."""
		category = frappe.get_cached_doc("Transaction Category", self.category)

		if self.supplier:
			# Purchase Invoice path — item required (from category or generic)
			gl_doc = self._create_purchase_invoice(category)
		else:
			# Journal Entry path — needs gl_account on category + linked nexus account
			gl_account = category.gl_account
			payment_gl_account = self._resolve_nexus_gl_account(self.nexus_account)
			if not gl_account or not payment_gl_account:
				self._defer_gl_posting("Expense GL Account or Nexus Account GL link not configured")
				return
			gl_doc = self._create_expense_journal_entry(gl_account, payment_gl_account)

		self._record_gl_success(gl_doc)

	def _attempt_transfer_journal_entry(self):
		"""Post Transfer as a Bank Entry Journal Entry between two Nexus Accounts."""
		from_gl_account = self._resolve_nexus_gl_account(self.nexus_account)
		to_gl_account = self._resolve_nexus_gl_account(self.to_nexus_account)

		if not from_gl_account or not to_gl_account:
			self._defer_gl_posting("One or both Nexus Accounts do not have a linked GL Account")
			return

		amount = flt(self.amount)
		journal_entry = frappe.get_doc({
			"doctype": "Journal Entry",
			"posting_date": getdate(self.date),
			"voucher_type": "Bank Entry",
			"user_remark": self.description or _("Transfer from Nexus Books"),
			"nexus_books_ref": self.name,
			"accounts": [
				{"account": from_gl_account, "credit_in_account_currency": amount},
				{"account": to_gl_account, "debit_in_account_currency": amount},
			],
		})
		journal_entry.insert(ignore_permissions=True)

		settings = frappe.get_single("Nexus Books Settings")
		if settings.auto_submit_documents:
			journal_entry.submit()

		self._record_gl_success({"doctype": "Journal Entry", "name": journal_entry.name})

	# --- Invoice / JE creators ---

	def _create_sales_invoice(self, category):
		"""Create Sales Invoice for income with customer."""
		income_item = category.item or _get_or_create_generic_item("Nexus Income Item")

		sales_invoice = frappe.get_doc({
			"doctype": "Sales Invoice",
			"customer": self.customer,
			"posting_date": getdate(self.date),
			"due_date": getdate(self.date),
			"nexus_books_ref": self.name,
			"items": [{
				"item_code": income_item,
				"qty": 1,
				"rate": flt(self.amount),
				"description": self.description or _("Income from Nexus Books"),
			}],
		})
		sales_invoice.insert(ignore_permissions=True)

		settings = frappe.get_single("Nexus Books Settings")
		if settings.auto_submit_documents:
			sales_invoice.submit()

		return {"doctype": "Sales Invoice", "name": sales_invoice.name}

	def _create_purchase_invoice(self, category):
		"""Create Purchase Invoice for expense with supplier."""
		expense_item = category.item or _get_or_create_generic_item("Nexus Expense Item")

		purchase_invoice = frappe.get_doc({
			"doctype": "Purchase Invoice",
			"supplier": self.supplier,
			"posting_date": getdate(self.date),
			"bill_date": getdate(self.date),
			"nexus_books_ref": self.name,
			"items": [{
				"item_code": expense_item,
				"qty": 1,
				"rate": flt(self.amount),
				"description": self.description or _("Expense from Nexus Books"),
			}],
		})
		purchase_invoice.insert(ignore_permissions=True)

		settings = frappe.get_single("Nexus Books Settings")
		if settings.auto_submit_documents:
			purchase_invoice.submit()

		return {"doctype": "Purchase Invoice", "name": purchase_invoice.name}

	def _create_income_journal_entry(self, income_gl_account, payment_gl_account):
		"""Create Journal Entry for income without customer."""
		amount = flt(self.amount)
		journal_entry = frappe.get_doc({
			"doctype": "Journal Entry",
			"posting_date": getdate(self.date),
			"voucher_type": "Journal Entry",
			"user_remark": self.description or _("Income from Nexus Books"),
			"nexus_books_ref": self.name,
			"accounts": [
				{"account": payment_gl_account, "debit_in_account_currency": amount},
				{"account": income_gl_account, "credit_in_account_currency": amount},
			],
		})
		journal_entry.insert(ignore_permissions=True)

		settings = frappe.get_single("Nexus Books Settings")
		if settings.auto_submit_documents:
			journal_entry.submit()

		return {"doctype": "Journal Entry", "name": journal_entry.name}

	def _create_expense_journal_entry(self, expense_gl_account, payment_gl_account):
		"""Create Journal Entry for expense without supplier."""
		amount = flt(self.amount)
		journal_entry = frappe.get_doc({
			"doctype": "Journal Entry",
			"posting_date": getdate(self.date),
			"voucher_type": "Journal Entry",
			"user_remark": self.description or _("Expense from Nexus Books"),
			"nexus_books_ref": self.name,
			"accounts": [
				{"account": expense_gl_account, "debit_in_account_currency": amount},
				{"account": payment_gl_account, "credit_in_account_currency": amount},
			],
		})
		journal_entry.insert(ignore_permissions=True)

		settings = frappe.get_single("Nexus Books Settings")
		if settings.auto_submit_documents:
			journal_entry.submit()

		return {"doctype": "Journal Entry", "name": journal_entry.name}

	# --- Helpers ---

	def _resolve_nexus_gl_account(self, nexus_account_name):
		"""Return linked_account from a Nexus Account, or None if not configured."""
		if not nexus_account_name:
			return None
		return frappe.db.get_value("Nexus Account", nexus_account_name, "linked_account")

	def _defer_gl_posting(self, reason):
		"""Mark GL posting as pending without raising an error."""
		self.db_set("gl_status", "pending")
		self.db_set("gl_error", reason)

	def _record_gl_success(self, gl_doc):
		"""Persist GL document reference and mark as posted."""
		self.db_set("reference_document", gl_doc["doctype"])
		self.db_set("dynamic_link_knor", gl_doc["name"])
		self.db_set("gl_status", "posted")
		self.db_set("gl_error", None)


# --- Module-level helper ---

def _get_or_create_generic_item(item_name):
	"""Get or create a generic non-stock service item for invoices."""
	if frappe.db.exists("Item", item_name):
		return item_name

	item = frappe.get_doc({
		"doctype": "Item",
		"item_code": item_name,
		"item_name": item_name,
		"item_group": "Services",
		"stock_uom": "Nos",
		"is_stock_item": 0,
	})
	item.insert(ignore_permissions=True)
	frappe.db.commit()
	return item.name


