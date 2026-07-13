{
    'name': 'Purchase Order Automation',
    'version': '18.0.1.0.1',
    'summary': 'Confirm a purchase order and let Odoo validate the receipt, '
               'create the vendor bill and post it. Each step optional.',
    'description': """
Three switches in Purchase Settings, each independent:

* Auto Validate Receipt: incoming shipments are validated the moment
  the purchase order is confirmed.
* Auto Create Vendor Bill: a draft bill is created from the order using
  Odoo's standard billing flow (respects each product's bill control
  policy).
* Auto Post Vendor Bill: the created bill is posted immediately.

Every automated step is logged in the purchase order's chatter. If a
step cannot complete (stock issue, missing data), the order is not
blocked: the step is skipped and a chatter message explains what to do
manually.

Works with the Transaction Date for Orders & Inventory module by the
same author: when installed, receipts and bills are dated with the
order's transaction date automatically.
""",
    'author': 'Adedeji Toriade',
    'maintainer': 'Tajdigitals',
    'website': 'https://github.com/taj2307',
    'support': 'adedejitoriade@gmail.com',
    'category': 'Inventory/Purchase',
    'license': 'LGPL-3',
    'depends': ['purchase', 'stock'],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
