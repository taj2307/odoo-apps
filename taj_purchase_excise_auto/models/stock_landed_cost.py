from odoo import models
from odoo.tools import float_round


class StockLandedCost(models.Model):
    _inherit = "stock.landed.cost"

    def _get_excise_product_id(self):
        """Configured excise product id, with EXCISE1 reference fallback."""
        ICP = self.env['ir.config_parameter'].sudo()
        product_id = int(ICP.get_param('purchase_excise.product_id', 0) or 0)
        if product_id:
            return product_id
        product = self.env['product.product'].search(
            [('default_code', '=', 'EXCISE1')], limit=1
        )
        return product.id or 0

    def compute_landed_cost(self):
        self.ensure_one()
        AdjustmentLines = self.env['stock.valuation.adjustment.lines']
        AdjustmentLines.search([('cost_id', '=', self.id)]).unlink()

        # get valuation lines (compatible across versions)
        getter = getattr(self, '_get_valuation_lines', None) or getattr(self, 'get_valuation_lines', None)
        if not getter:
            # Nothing to compute on this Odoo version
            return True

        # Call getter (some signatures may accept args; we try without args first)
        try:
            all_val_line_values = list(getter())
        except TypeError:
            # fallback if signature expects a picking argument etc.
            all_val_line_values = list(getter(self))

        excise_product_id = self._get_excise_product_id()

        for line in self.cost_lines:
            val_line_values_list = list(all_val_line_values)

            # Excise cost split by volume: exclude free items
            # (former_cost == 0 and value == 0) from the distribution.
            is_excise_line = (
                excise_product_id
                and line.product_id
                and line.product_id.id == excise_product_id
            )
            if is_excise_line and line.split_method == 'by_volume':
                filtered = []
                for vl in all_val_line_values:
                    former_cost = float(vl.get('former_cost', 0.0) or 0.0)
                    value = float(vl.get('value', 0.0) or 0.0)
                    if former_cost > 0.0 or value > 0.0:
                        filtered.append(vl)
                val_line_values_list = filtered if filtered else list(all_val_line_values)

            if not val_line_values_list:
                continue

            total_qty = sum(float(vl.get('quantity', 0.0) or 0.0) for vl in val_line_values_list)
            total_weight = sum(float(vl.get('weight', 0.0) or 0.0) for vl in val_line_values_list)
            total_volume = sum(float(vl.get('volume', 0.0) or 0.0) for vl in val_line_values_list)
            total_former_cost = sum(float(vl.get('former_cost', 0.0) or 0.0) for vl in val_line_values_list)
            total_lines = len(val_line_values_list)

            for val in val_line_values_list:
                value = 0.0
                if line.split_method == 'equal':
                    if total_lines:
                        value = line.price_unit / total_lines
                elif line.split_method == 'by_quantity':
                    if total_qty:
                        value = (line.price_unit * float(val.get('quantity', 0.0))) / total_qty
                elif line.split_method == 'by_weight':
                    if total_weight:
                        value = (line.price_unit * float(val.get('weight', 0.0))) / total_weight
                elif line.split_method == 'by_volume':
                    if total_volume:
                        value = (line.price_unit * float(val.get('volume', 0.0))) / total_volume
                elif line.split_method == 'by_current_cost_price':
                    if total_former_cost:
                        value = (line.price_unit * float(val.get('former_cost', 0.0))) / total_former_cost
                else:
                    if total_qty:
                        value = (line.price_unit * float(val.get('quantity', 0.0))) / total_qty

                rounding = (self.company_id.currency_id.rounding if self.company_id and self.company_id.currency_id else 0.01)
                value = float_round(value, precision_rounding=rounding)

                if value:
                    adj_vals = {
                        'cost_id': self.id,
                        'move_id': val.get('move_id'),
                        'product_id': val.get('product_id'),
                        'quantity': val.get('quantity'),
                        'weight': val.get('weight'),
                        'volume': val.get('volume'),
                        'former_cost': val.get('former_cost'),
                        'cost_line_id': line.id,
                        'additional_landed_cost': value,
                        'name': line.name or (line.product_id.display_name if line.product_id else line.name),
                    }
                    AdjustmentLines.create(adj_vals)

        return True
