# Safe Partner Merge

Adds two guards in front of Odoo 20's native contact merge:

1. Permission gate: only users with the "Can Merge Partners" checkbox
   (on the user form, Access Rights tab) can run the merge action.
2. Pre-merge check: selected partners are scanned for draft invoices and
   bills. If any exist the merge is blocked and the documents are listed,
   because merging with drafts can cause journal sequence conflicts.

The native merge wizard itself is untouched.

Depends on `account` only. License: LGPL-3.

Author: Adedeji Toriade (Tajdigitals) | Support: adedejitoriade@gmail.com
