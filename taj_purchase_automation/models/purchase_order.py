from odoo import fields, models
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_confirm(self):
        ICP = self.env['ir.config_parameter'].sudo()
        auto_receipt = ICP.get_param('purchase_automation.auto_validate_receipt')
        auto_bill = ICP.get_param('purchase_automation.auto_create_bill')
        auto_post = ICP.get_param('purchase_automation.auto_post_bill')

        res = super().button_confirm()

        if not (auto_receipt or auto_bill):
            return res

        for order in self:
            if order.state not in ('purchase', 'done'):
                continue
            if auto_receipt:
                order._auto_validate_receipts()
            if auto_bill:
                order._auto_create_bill(auto_post=bool(auto_post))
        return res

    # ------------------------------------------------------------------
    # Receipts
    # ------------------------------------------------------------------

    def _auto_validate_receipts(self):
        self.ensure_one()
        for picking in self.picking_ids:
            if picking.state in ('done', 'cancel'):
                continue
            try:
                if picking.state == 'draft':
                    picking.action_confirm()
                if picking.state in ('confirmed', 'waiting'):
                    picking.action_assign()
                for move in picking.move_ids:
                    if not move.quantity:
                        move.quantity = move.product_uom_qty
                picking.with_context(
                    skip_backorder=True,
                    picking_ids_not_to_backorder=picking.ids,
                ).button_validate()
                self.message_post(
                    body=(
                        f"Receipt <a href='/web#id={picking.id}"
                        f"&model=stock.picking'>{picking.name}</a> "
                        "validated automatically."
                    )
                )
            except (UserError, ValueError) as e:
                self.message_post(
                    body=(
                        f"Automatic validation of receipt {picking.name} "
                        f"failed: {e}. Please validate it manually."
                    )
                )

    # ------------------------------------------------------------------
    # Bills
    # ------------------------------------------------------------------

    def _auto_create_bill(self, auto_post=False):
        self.ensure_one()
        if self.invoice_ids:
            return

        # Products billed on RECEIVED quantities can only be billed once
        # the receipt is validated. If such lines exist and the receipts
        # are not done (e.g. Auto Validate Receipt is off or it failed),
        # skip bill creation with a clear chatter note instead of raising
        # "no invoiceable line".
        receive_policy_lines = self.order_line.filtered(
            lambda l: l.product_id
            and l.product_id.purchase_method == 'receive'
        )
        if receive_policy_lines:
            receipts_pending = any(
                p.state not in ('done', 'cancel') for p in self.picking_ids
            )
            if receipts_pending or not self.picking_ids:
                self.message_post(
                    body=(
                        "Bill not created automatically: some products on "
                        "this order are billed on received quantities and "
                        "the receipt is not validated yet. Validate the "
                        "receipt, then create the bill, or enable Auto "
                        "Validate Receipt in Purchase Settings."
                    )
                )
                return

        try:
            # Standard Odoo billing flow: respects each product's bill
            # control policy (ordered vs received quantities).
            self.action_create_invoice()
        except UserError as e:
            self.message_post(
                body=(
                    f"Automatic bill creation failed: {e}. "
                    "Please create the bill manually."
                )
            )
            return

        for bill in self.invoice_ids.filtered(lambda b: b.state == 'draft'):
            if not bill.invoice_date:
                # Integrates with the Transaction Date module when installed
                txn_date = getattr(self, 'transaction_date', False)
                bill.invoice_date = txn_date or fields.Date.context_today(self)
            self.message_post(
                body=(
                    f"Bill <a href='/web#id={bill.id}&model=account.move'>"
                    f"{bill.display_name}</a> created automatically."
                )
            )
            if auto_post:
                try:
                    bill.action_post()
                    self.message_post(
                        body=(
                            f"Bill <a href='/web#id={bill.id}"
                            f"&model=account.move'>{bill.display_name}</a> "
                            "posted automatically."
                        )
                    )
                except UserError as e:
                    self.message_post(
                        body=(
                            f"Automatic posting of the bill failed: {e}. "
                            "Please post it manually."
                        )
                    )
