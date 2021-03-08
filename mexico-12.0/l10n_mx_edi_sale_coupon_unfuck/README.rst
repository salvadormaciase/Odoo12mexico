EDI sale Coupon
===============

This module allows generate a valid CFDI for an invoice that comes from a sale with
a coupon. In this case, the coupon is applied like a discount in the invoice.

Now support the next case:
  1. Create a new coupon for the order with 10% of discount
  2. Create a sale order and apply the coupon
  3. Generate the customer invoice

Now when is generated the invoice, the discount line is updated to
``price unit = 0`` and the discount is assigned to the other lines in the invoice.

Technical:
==========

To install this module go to ``Apps`` search ``l10n_mx_edi_sale_coupon_unfuck`` and click
in button ``Install``.

Contributors
------------

* Luis Torres <luis_t@vauxoo.com>

Maintainer
----------

.. figure:: https://www.vauxoo.com/logo.png
   :alt: Vauxoo
   :target: https://vauxoo.com

This module is maintained by Vauxoo.

a latinamerican company that provides training, coaching,
development and implementation of enterprise management
sytems and bases its entire operation strategy in the use
of Open Source Software and its main product is odoo.

To contribute to this module, please visit http://www.vauxoo.com.
