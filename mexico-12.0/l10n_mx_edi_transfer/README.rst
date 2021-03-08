CFDI to Transfers
=================

Now this module support when is generated a CFDI to transfer your merchandise
with your own transport.

To this the SAT specific that you are the sam emitter and receiver of the CFDI,
but in the receiver the VAT is the generic (XAXX010101000).

How do I can generate this CFDI?
--------------------------------

To get this CFDI, must be generated a new customer invoice with the next
values:

* Partner: Must be the same partner that in the company.
* Invoice lines: Must be specified all the products that will be transfered,
  with the quantity to move, but the amounts must be 0 and without taxes.

Here an example:
  .. figure:: ../l10n_mx_edi_transfer/static/src/invoice.png
    :width: 500pt

The next step is validate the invoice as any other.

This generate a CFDI like this:
  .. figure:: ../l10n_mx_edi_transfer/static/src/cfdi.png
    :width: 500pt

And if you print the CFDI looks like this:
  .. figure:: ../l10n_mx_edi_transfer/static/src/pdf.png
    :width: 500pt

How the amount total is 0, the accounting in your system is not affected.

For more information about this, you could read the `Anexo20
<http://www.sat.gob.mx/informacion_fiscal/factura_electronica/Documents/Gu%C3%ADaAnexo20.pdf>`_

If you have real_time valuation the account move line for this case will be skipped.
