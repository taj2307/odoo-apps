{
    'name': 'Safe Partner Merge',
    'version': '20.0.1.1.0',
    'summary': 'Control who can merge contacts and block merges while '
               'draft invoices exist.',
    'description': """
Odoo's built-in contact merge is powerful and dangerous: any user who can
reach it can collapse customers into each other, and merging partners that
still have draft invoices can cause journal sequence conflicts.

This module adds two safety layers:

* Permission control. Only users with the "Can Merge Partners" flag
  (a simple checkbox on the user form) see and can run the merge action.
* Pre-merge check. Before the merge wizard opens, the selected partners
  are scanned for draft invoices and bills. If any exist, the merge is
  blocked and each offending document is listed so it can be posted or
  deleted first.

When the check passes, the user continues into the standard Odoo merge
wizard, nothing else about the native flow changes.

The same two rules are enforced inside Odoo's merge itself, so they also
apply to the native Merge action and to the automatic contact
deduplication tool. Users start from the Safe Merge action in the
Actions menu to see the pre-check.
""",
    'author': 'Adedeji Toriade',
    'maintainer': 'Tajdigitals',
    'website': 'https://github.com/taj2307',
    'support': 'adedejitoriade@gmail.com',
    'category': 'Tools',
    'license': 'LGPL-3',
    'depends': ['account'],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/res_users_view.xml',
        'views/partner_merge_check_view.xml',
        'data/partner_merge_action.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
