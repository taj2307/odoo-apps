# Auto Excise Duty on Purchases

Adds an automatic volume-based excise duty line to Odoo 18 purchase orders.

- Excise product and rate per volume unit configured in Purchase Settings
- Per order toggle: "Apply Auto Excise Duty"
- Duty quantity = sum of (line volume x line quantity), excluding free items
  and products without volume
- Recalculates when the order changes; removed when the toggle is off
- Landed cost integration: when the excise product is split by volume,
  free items are excluded from the distribution

Originally built for the Nigerian excise regime, usable for any per-volume levy.

Depends on `purchase`, `stock`, `stock_landed_costs`. License: LGPL-3.

Author: Adedeji Toriade (Tajdigitals) | Support: adedejitoriade@gmail.com
