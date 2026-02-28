# Copyright (c) 2026, RAhmed-Dev and contributors
# For license information, please see license.txt

"""
API methods for Nexus Books

Provides methods for:
- Party (Customer/Supplier) caching for offline use
- Transaction category caching
- Transaction statistics
"""

import frappe
from frappe import _


@frappe.whitelist()
def get_cached_parties(party_type="Customer", limit=50):
	"""Get frequently used parties for offline caching.

	Args:
		party_type (str): "Customer" or "Supplier"
		limit (int): Number of parties to return

	Returns:
		list: Party data for offline use
	"""
	if party_type not in ["Customer", "Supplier"]:
		frappe.throw(_("Invalid party type. Must be Customer or Supplier."))

	if not limit:
		settings = frappe.get_single("Nexus Books Settings")
		limit = settings.cache_party_count or 50

	if party_type == "Customer":
		parties = frappe.db.sql("""
			SELECT
				c.name,
				c.customer_name as party_name,
				c.mobile_no,
				c.email_id,
				c.image,
				COUNT(si.name) as transaction_count
			FROM `tabCustomer` c
			LEFT JOIN `tabSales Invoice` si ON si.customer = c.name AND si.docstatus = 1
			WHERE c.disabled = 0
			GROUP BY c.name
			ORDER BY transaction_count DESC, c.modified DESC
			LIMIT %s
		""", (limit,), as_dict=True)
	else:
		parties = frappe.db.sql("""
			SELECT
				s.name,
				s.supplier_name as party_name,
				s.mobile_no,
				s.email_id,
				s.image,
				COUNT(pi.name) as transaction_count
			FROM `tabSupplier` s
			LEFT JOIN `tabPurchase Invoice` pi ON pi.supplier = s.name AND pi.docstatus = 1
			WHERE s.disabled = 0
			GROUP BY s.name
			ORDER BY transaction_count DESC, s.modified DESC
			LIMIT %s
		""", (limit,), as_dict=True)

	return parties


@frappe.whitelist()
def get_transaction_categories(category_type=None):
	"""Get active transaction categories for offline caching.

	Args:
		category_type (str): Optional filter - "Income", "Expense", or "Transfer"

	Returns:
		list: Category data for offline use
	"""
	filters = {"is_active": 1}

	if category_type:
		if category_type not in ["Income", "Expense", "Transfer"]:
			frappe.throw(_("Invalid category type. Must be Income, Expense, or Transfer."))
		filters["category_type"] = category_type

	return frappe.get_all(
		"Transaction Category",
		filters=filters,
		fields=["name", "category_name", "category_code", "category_type", "is_active", "account", "color", "icon"],
		order_by="category_name asc"
	)


@frappe.whitelist()
def get_default_payment_account():
	"""Get default payment account from Nexus Books Settings.

	Returns:
		str: Default payment account name or None
	"""
	settings = frappe.get_single("Nexus Books Settings")
	return settings.default_payment_account


@frappe.whitelist()
def get_transaction_summary(from_date=None, to_date=None):
	"""Get transaction summary for dashboard.

	Args:
		from_date (str): Start date (optional, defaults to current month start)
		to_date (str): End date (optional, defaults to current month end)

	Returns:
		dict: Transaction summary with income, expense, balance
	"""
	from frappe.utils import get_first_day, get_last_day, nowdate

	if not from_date:
		from_date = get_first_day(nowdate())
	if not to_date:
		to_date = get_last_day(nowdate())

	income = frappe.db.sql("""
		SELECT SUM(amount) as total
		FROM `tabFinancial Transaction`
		WHERE transaction_type = 'Income'
		AND date BETWEEN %s AND %s
		AND docstatus < 2
	""", (from_date, to_date), as_dict=True)[0].total or 0

	expense = frappe.db.sql("""
		SELECT SUM(amount) as total
		FROM `tabFinancial Transaction`
		WHERE transaction_type = 'Expense'
		AND date BETWEEN %s AND %s
		AND docstatus < 2
	""", (from_date, to_date), as_dict=True)[0].total or 0

	return {
		"income": income,
		"expense": expense,
		"balance": income - expense,
		"from_date": from_date,
		"to_date": to_date
	}


@frappe.whitelist()
def create_category(category_name, category_type, color=None, icon=None):
	"""Create a new Transaction Category from the PWA.

	Args:
		category_name (str): Display name (also used as docname)
		category_type (str): "Income", "Expense", or "Transfer"
		color (str): Hex color string, e.g. "#ef4444"
		icon (str): Lucide icon name, e.g. "shopping-cart"

	Returns:
		dict: Created category fields
	"""
	if category_type not in ["Income", "Expense", "Transfer"]:
		frappe.throw(_("Invalid category type. Must be Income, Expense, or Transfer."))

	if not category_name or not category_name.strip():
		frappe.throw(_("Category name is required."))

	doc = frappe.get_doc({
		"doctype": "Transaction Category",
		"category_name": category_name.strip(),
		"category_type": category_type,
		"is_active": 1,
		"color": color or None,
		"icon": icon or None,
	})
	doc.insert(ignore_permissions=False)

	return {
		"name": doc.name,
		"category_name": doc.category_name,
		"category_type": doc.category_type,
		"is_active": doc.is_active,
		"color": doc.color,
		"icon": doc.icon,
	}


@frappe.whitelist()
def update_category(category, category_name, category_type, color=None, icon=None):
	"""Update an existing Transaction Category from the PWA.

	Args:
		category (str): Docname of the category to update
		category_name (str): New display name
		category_type (str): "Income", "Expense", or "Transfer"
		color (str): Hex color string
		icon (str): Lucide icon name

	Returns:
		dict: Updated category fields
	"""
	if category_type not in ["Income", "Expense", "Transfer"]:
		frappe.throw(_("Invalid category type. Must be Income, Expense, or Transfer."))

	if not category_name or not category_name.strip():
		frappe.throw(_("Category name is required."))

	doc = frappe.get_doc("Transaction Category", category)
	if not doc.has_permission("write"):
		frappe.throw(_("Insufficient permissions to update this category."))

	doc.category_name = category_name.strip()
	doc.category_type = category_type
	doc.color = color or None
	doc.icon = icon or None
	doc.save()

	return {
		"name": doc.name,
		"category_name": doc.category_name,
		"category_type": doc.category_type,
		"is_active": doc.is_active,
		"color": doc.color,
		"icon": doc.icon,
	}


@frappe.whitelist()
def toggle_category_active(category):
	"""Toggle the is_active flag on a Transaction Category.

	Args:
		category (str): Docname of the category to toggle

	Returns:
		dict: Updated is_active value
	"""
	doc = frappe.get_doc("Transaction Category", category)
	if not doc.has_permission("write"):
		frappe.throw(_("Insufficient permissions to update this category."))

	doc.is_active = 0 if doc.is_active else 1
	doc.save()

	return {"name": doc.name, "is_active": doc.is_active}


@frappe.whitelist()
def get_recent_transactions(limit=20):
	"""Get recent transactions for dashboard.

	Args:
		limit (int): Number of transactions to return

	Returns:
		list: Recent transactions enriched with category details
	"""
	transactions = frappe.get_all(
		"Financial Transaction",
		filters={"docstatus": ["<", 2]},
		fields=[
			"name", "transaction_type", "date", "category",
			"amount", "customer", "supplier", "description"
		],
		order_by="date desc",
		limit=limit
	)

	for txn in transactions:
		if txn.category:
			category = frappe.get_cached_doc("Transaction Category", txn.category)
			txn["category_color"] = category.color
			txn["category_icon"] = category.icon
			txn["category_name"] = category.category_name

	return transactions
