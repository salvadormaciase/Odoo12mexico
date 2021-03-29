EDI Payment Split
=================

This module allows to specify the amount paid on each invoice in a multi-invoice payment.

Usage
=====

- Create and validate more than one invoice for the same partner.

- Select the invoices in the tree view and use the Register Payment action.

  .. image:: l10n_mx_edi_payment_split/static/src/img/tree_view.png
    :width: 400pt
    :alt: Tree view

- Select currency, journal and amount.

  .. image:: l10n_mx_edi_payment_split/static/src/img/register_payment.png
    :width: 400pt
    :alt: Register payment

- You can change the rate using the custom rate for all lines or the rate field for a specific line.

  .. image:: l10n_mx_edi_payment_split/static/src/img/custom_rate.png
    :width: 400pt
    :alt: Custom Rate

- Check the payment lines for each invoice.

  * Blue lines mean a correct partial payment

    .. image:: l10n_mx_edi_payment_split/static/src/img/with_partial.png
      :width: 400pt
      :alt: With partial payment

  * Normal lines mean a correct total payment

    .. image:: l10n_mx_edi_payment_split/static/src/img/total_paid.png
      :width: 400pt
      :alt: Total payment

  * Red lines mean the payment amount is bigger than the due amount.

    .. image:: l10n_mx_edi_payment_split/static/src/img/red_line.png
      :width: 400pt
      :alt: Red line

- Change the payment amount or the payment currency amount if it's necessary.

- Optional: you can upload a csv file with the invoice info to pay. 
  The file must be comma separated and with 2 or 3 columns: invoice_number,amount,rate.

- Validate the payment.
