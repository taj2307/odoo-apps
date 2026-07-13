from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    apply_excise_duty = fields.Boolean(
        string="Apply Auto Excise Duty",
        default=False,
        help="When checked, an excise duty line is calculated and added to "
             "this purchase order automatically, based on product volume "
             "and the rate configured in Purchase Settings.",
    )

    def _get_excise_product(self):
        """Return the configured excise product.

        Falls back to a product with internal reference EXCISE1 for
        databases configured before the settings screen existed."""
        ICP = self.env['ir.config_parameter'].sudo()
        product_id = int(ICP.get_param('purchase_excise.product_id', 0) or 0)
        if product_id:
            product = self.env['product.product'].browse(product_id).exists()
            if product:
                return product
        return self.env['product.product'].search(
            [('default_code', '=', 'EXCISE1')], limit=1
        )

    def _get_excise_rate(self, excise_product):
        """Rate per volume unit: settings first, then product prices."""
        ICP = self.env['ir.config_parameter'].sudo()
        rate = float(ICP.get_param('purchase_excise.rate', 0) or 0)
        if rate:
            return rate
        return excise_product.list_price or excise_product.standard_price or 0.0

    def _add_excise_line(self):
        excise_product = self._get_excise_product()
        if not excise_product:
            return

        for order in self:
            existing_excise_lines = order.order_line.filtered(
                lambda l: l.product_id == excise_product
            )

            # If excise is disabled, remove any existing excise line and stop
            if not order.apply_excise_duty:
                if existing_excise_lines:
                    existing_excise_lines.unlink()
                continue

            total_excise_qty = 0.0
            for line in order.order_line:
                product = line.product_id
                if not product or product == excise_product:
                    continue
                vol = float(product.volume or 0.0)
                qty = float(line.product_qty or 0.0)
                unit_price = float(line.price_unit or 0.0)
                # Include only if volume > 0, qty > 0, and unit price > 0 (not free)
                if vol > 0 and qty > 0 and unit_price > 0.0:
                    total_excise_qty += qty * vol

            price_unit = order._get_excise_rate(excise_product)
            uom_id = excise_product.uom_po_id.id or excise_product.uom_id.id

            if order.state == 'draft':
                # In draft: safe to delete and recreate
                if existing_excise_lines:
                    existing_excise_lines.unlink()
                if total_excise_qty > 0.0:
                    self.env['purchase.order.line'].create({
                        'order_id': order.id,
                        'product_id': excise_product.id,
                        'name': f"{excise_product.name} (Auto Excise)",
                        'product_qty': total_excise_qty,
                        'product_uom': uom_id,
                        'price_unit': price_unit,
                    })
            else:
                # In confirmed: update existing or create new
                if existing_excise_lines:
                    existing_excise_lines.write({
                        'product_qty': total_excise_qty,
                        'price_unit': price_unit,
                        'name': f"{excise_product.name} (Auto Excise)",
                    })
                elif total_excise_qty > 0.0:
                    self.env['purchase.order.line'].create({
                        'order_id': order.id,
                        'product_id': excise_product.id,
                        'name': f"{excise_product.name} (Auto Excise)",
                        'product_qty': total_excise_qty,
                        'product_uom': uom_id,
                        'price_unit': price_unit,
                    })

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        orders._add_excise_line()
        return orders

    def write(self, vals):
        res = super().write(vals)
        # Only recalculate if relevant fields changed to avoid unnecessary mutations
        relevant_fields = {'order_line', 'apply_excise_duty'}
        if relevant_fields.intersection(vals.keys()):
            self._add_excise_line()
        return res
