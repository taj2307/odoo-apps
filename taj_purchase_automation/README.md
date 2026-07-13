# Purchase Order Automation

Three independent switches in Odoo 18 Purchase Settings:

1. Auto Validate Receipt on PO confirmation
2. Auto Create Vendor Bill (standard billing flow, respects bill control policy)
3. Auto Post Vendor Bill

Every automated step is logged in the PO chatter. Failures never block the
confirmation: the step is skipped with a chatter note explaining what to do
manually.

Integrates with the Transaction Date for Orders & Inventory module (same
author): when installed, receipts and bills carry the order's transaction date.

Depends on `purchase` and `stock`. License: LGPL-3.

Author: Adedeji Toriade (Tajdigitals) | Support: adedejitoriade@gmail.com
