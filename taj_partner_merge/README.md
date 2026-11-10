# Safe Partner Merge

Adds two rules to Odoo 19's contact merge:

1. Permission: only users with the "Can Merge Partners" checkbox
   (on the user form, Access Rights tab) can merge contacts. The flag
   also grants Odoo's Contact Creation right, which merging needs.
2. Draft check: selected partners are scanned for draft invoices and
   bills. If any exist the merge is blocked and the documents are listed,
   because merging with drafts can cause journal sequence conflicts.

The rules are enforced inside Odoo's merge, so they cover the native
Merge action, the deduplication tool and the module's own Safe Merge
action, which shows the check result before opening the merge wizard.

Depends on `account` only. License: LGPL-3.

Author: Adedeji Toriade (Tajdigitals) | Support: adedejitoriade@gmail.com
