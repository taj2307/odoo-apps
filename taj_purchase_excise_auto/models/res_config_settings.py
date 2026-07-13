from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    excise_product_id = fields.Many2one(
        'product.product',
        string='Excise Duty Product',
        domain="[('purchase_ok', '=', True)]",
        help='Service product used for the automatic excise duty line on '
             'purchase orders. Also used to recognise the excise cost line '
             'in landed costs.',
    )
    excise_rate = fields.Float(
        string='Rate per Volume Unit',
        digits='Product Price',
        help='Duty charged per unit of volume. If left at zero, the sales '
             'price or cost of the excise product is used instead.',
    )

    @api.model
    def get_values(self):
        res = super().get_values()
        ICP = self.env['ir.config_parameter'].sudo()
        product_id = int(ICP.get_param('purchase_excise.product_id', 0) or 0)
        # Must be False (not 0) when unset: a zero id crashes the
        # settings form's onchange snapshot in Odoo 18.
        res.update(
            excise_product_id=product_id or False,
            excise_rate=float(ICP.get_param('purchase_excise.rate', 0) or 0),
        )
        return res

    def set_values(self):
        super().set_values()
        ICP = self.env['ir.config_parameter'].sudo()
        ICP.set_param('purchase_excise.product_id', self.excise_product_id.id or 0)
        ICP.set_param('purchase_excise.rate', self.excise_rate or 0)
