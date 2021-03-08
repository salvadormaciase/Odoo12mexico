Invoice Discounting
===================

Currently in Odoo, discounts per invoice line are based on percentages, but in
some cases we need to establish discounts in fixed amounts not defined in
percentage.

With this module we can write the discount per invoice line in percentages or
in a fixed amount. Depending on how the discount is established, the other
value will be calculated automatically. That is to say:

1. If a discount is established in a fixed amount, the percentage will be
   calculated automatically.

2. If a percentage discount is established, the fixed amount will be calculated
   automatically.
