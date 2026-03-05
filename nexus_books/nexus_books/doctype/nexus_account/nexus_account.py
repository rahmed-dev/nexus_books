# Copyright (c) 2026, RAhmed-Dev and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class NexusAccount(Document):
	def validate(self):
		"""Validate Nexus Account before save."""
		self.enforce_single_default()

	def enforce_single_default(self):
		"""Ensure only one Nexus Account is marked as default at a time."""
		if self.is_default:
			frappe.db.set_value(
				"Nexus Account",
				{"is_default": 1, "name": ("!=", self.name)},
				"is_default",
				0,
			)
