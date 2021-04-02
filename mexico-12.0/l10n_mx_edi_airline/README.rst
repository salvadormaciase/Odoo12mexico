This modules manages the Airlines Complement to handle the passenger's data on
Invoices.

To use this module complete the following information, on the Invoice you have
to provide a TUA product, and the extra charges if needed.

These **Extra Charges** and **TUA** product required the following information:

- *CodigoCargo*, it is the charge code according to IATA catalog only when
  extra charges. This is set on Product's Internal Reference field.
- *Importe*, it is the charge amount. You don't have to set this, this is
  product's price subtotal in the invoice.

In both cases, you should select the 'Product Type' in Product's Invoice
Tag.

The following is an example of a TUA product:

.. image:: l10n_mx_edi_airline/static/src/tua_example.png
   :align: center
   :width: 350pt

The following is an example of an Extra Charge product:

.. image:: l10n_mx_edi_airline/static/src/extra_charge_example.png
   :align: center
   :width: 350pt

And last, this is an example of and invoice with TUA and extra charge products:

.. image:: l10n_mx_edi_airline/static/src/invoice_example.png
   :align: center
   :width: 550pt


For more information in the `SAT page for Airline Complement <http://www.sat.gob.mx/informacion_fiscal/factura_electronica/Paginas/complemento_aerolineas.aspx>`_.
