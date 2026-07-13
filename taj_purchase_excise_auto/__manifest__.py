{
    'name': 'Auto Excise Duty on Purchases',
    'version': '18.0.1.0.0',
    'summary': 'Automatically add a volume-based excise duty line to '
               'purchase orders, with landed cost distribution.',
    'description': """
Adds an automatic excise duty line to purchase orders, calculated from
product volume. Built for volume-based duties such as the Nigerian excise
on certain goods, but fully configurable for any per-volume levy.

How it works:

* Configure the excise product and the rate per volume unit in
  Purchase Settings.
* On a purchase order, switch on "Apply Auto Excise Duty".
* A duty line is added automatically: total volume of the order
  (volume x quantity per line) multiplied by your rate.
* Free items (zero price) and products without volume are excluded.
* The line updates itself when order lines change, and is removed if
  the toggle is switched off.

Landed costs:

* When the excise product is used as a landed cost split by volume,
  free items are excluded from the distribution too, so paid stock
  carries the duty.
""",
    'author': 'Adedeji Toriade',
    'maintainer': 'Tajdigitals',
    'website': 'https://github.com/taj2307',
    'support': 'adedejitoriade@gmail.com',
    'category': 'Inventory/Purchase',
    'license': 'LGPL-3',
    'depends': ['purchase', 'stock', 'stock_landed_costs'],
    'data': [
        'views/purchase_order_view.xml',
        'views/res_config_settings_views.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
