
import frappe
from frappe import _, bold, qb, throw
from frappe.utils import (
	add_days,
	add_months,
	cint,
	comma_and,
	flt,
	fmt_money,
	formatdate,
	get_last_day,
	get_link_to_form,
	getdate,
	nowdate,
	parse_json,
	today,
)

from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice

class OverrideSalesInvoice(SalesInvoice):
	def validate_against_voucher_outstanding(self):
		from frappe.model.meta import get_meta

		if not get_meta(self.doctype).has_field("outstanding_amount"):
			return

		if self.get("is_return") and self.return_against and not self.get("is_pos"):
			against_voucher_outstanding = frappe.get_value(
				self.doctype, self.return_against, "outstanding_amount"
			)
			document_type = "Credit Note" if self.doctype == "Sales Invoice" else "Debit Note"

			msg = ""
			if self.get("update_outstanding_for_self"):
				msg = (
					"We can see {0} is made against {1}. If you want {1}'s outstanding to be updated, "
					"uncheck '{2}' checkbox. <br><br>Or"
				).format(
					frappe.bold(document_type),
					get_link_to_form(self.doctype, self.get("return_against")),
					frappe.bold(_("Update Outstanding for Self")),
				)


			elif not self.update_outstanding_for_self and (
				abs(flt(self.base_rounded_total) or flt(self.base_grand_total)) > flt(against_voucher_outstanding)
			):
				self.update_outstanding_for_self = 1
				msg = (
					"The outstanding amount {} in {} is lesser than {}. Updating the outstanding to this invoice. <br><br>And"
				).format(
					against_voucher_outstanding,
					get_link_to_form(self.doctype, self.get("return_against")),
					flt(abs(self.outstanding_amount)),
				)
			
			if msg:
				msg += " you can use {} tool to reconcile against {} later.".format(
					get_link_to_form("Payment Reconciliation", "Payment Reconciliation"),
					get_link_to_form(self.doctype, self.get("return_against")),
				)
				frappe.msgprint(_(msg))