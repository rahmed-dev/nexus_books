# Copyright (c) 2026, RAhmed-Dev and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class TransactionCategory(Document):
	def validate(self):
		"""Validate Transaction Category before save."""
		self.validate_gl_account_type()
		self.validate_item()
		self.set_defaults()

	def validate_gl_account_type(self):
		"""Validate that gl_account type is appropriate for the category type.

		Transfer categories do not use gl_account (they use Nexus Account GL links).
		"""
		if not self.gl_account or self.category_type == "Transfer":
			return

		account_doc = frappe.get_cached_doc("Account", self.gl_account)
		account_type = account_doc.account_type

		if self.category_type == "Income" and account_type not in ["Income Account", "Income"]:
			frappe.throw(
				_("Income category GL Account must be an Income account. Selected: {0}").format(account_type)
			)

		if self.category_type == "Expense" and account_type not in ["Expense Account", "Expenses"]:
			frappe.throw(
				_("Expense category GL Account must be an Expense account. Selected: {0}").format(account_type)
			)

	def validate_item(self):
		"""Validate that the linked item is a non-stock service item."""
		if not self.item:
			return

		item_doc = frappe.get_cached_doc("Item", self.item)
		if item_doc.is_stock_item:
			frappe.throw(
				_("Item {0} must be a non-stock Service item.").format(self.item)
			)

	def set_defaults(self):
		"""Set default values."""
		if not self.category_code and self.category_name:
			self.category_code = self.category_name[:10].upper().replace(" ", "_")
