from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    po_auto_validate_receipt = fields.Boolean(
        string="Auto Validate Receipt",
        config_parameter='purchase_automation.auto_validate_receipt',
        help="Automatically validate incoming shipments when a purchase "
             "order is confirmed.",
    )
    po_auto_create_bill = fields.Boolean(
        string="Auto Create Vendor Bill",
        config_parameter='purchase_automation.auto_create_bill',
        help="Automatically create a draft vendor bill when a purchase "
             "order is confirmed.",
    )
    po_auto_post_bill = fields.Boolean(
        string="Auto Post Vendor Bill",
        config_parameter='purchase_automation.auto_post_bill',
        help="Automatically post the vendor bill after it is created.",
    )
