import frappe
from frappe import _
from frappe.utils import get_system_timezone

no_cache = 1


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login to access Nexus Books"), frappe.PermissionError)

    frappe.db.commit()
    context.boot = get_boot()
    return context


@frappe.whitelist(methods=["POST"], allow_guest=True)
def get_context_for_dev():
    if not frappe.conf.developer_mode:
        frappe.throw(_("This method is only available in developer mode"))
    return get_boot()


def get_boot():
    return frappe._dict(
        {
            "frappe_version": frappe.__version__,
            "site_name": frappe.local.site,
            "csrf_token": frappe.sessions.get_csrf_token(),
            "read_only_mode": frappe.flags.read_only,
            "sysdefaults": frappe.defaults.get_defaults(),
            "user_id": frappe.session.user,
            "is_logged_in": frappe.session.user != "Guest",
            "timezone": {
                "system": get_system_timezone(),
                "user": frappe.db.get_value("User", frappe.session.user, "time_zone")
                or get_system_timezone(),
            },
        }
    )
