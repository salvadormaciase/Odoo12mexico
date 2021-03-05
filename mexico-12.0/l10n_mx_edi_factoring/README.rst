EDI Financial Factoring
=======================

This Financial Factoring module for Mexican Localization allows satisfying the
SAT indication which establishes that a financial factor can buy my customer's
debts. In doing so, payment complement shall be emited in financial factor's
name instead of my original customer's name.

The process is Described in `Guía de Llenado de complemento de pago <http://omawww.sat.gob.mx/informacion_fiscal/factura_electronica/Documents/Complementoscfdi/Guia_comple_pagos.pdf>`_ at page 67

Further information on Financial Factoring can be found at `Wikipedia <https://www.wikiwand.com/en/Factoring_(finance)>`_

Summary of SAT Financial Factoring
----------------------------------

When the Factoree (`Factorado`) approaches to Financial Factor (`Factorante`)
with a batch of invoices to be collected to a Customer. Factoree relinquishes
its rights to claim the collection of the invoices and in exchange it receives
a money share - let us say 80% - of the total of the invoices to collect (First
Payment).

The Financial Factor invoices the Factoree its Loaning Services - it can be 5%
the total amount to collect. These Loaning Services serve the basis for a
compensation made to the invoices involved in the financial factoring - that is
the name of this kind of transaction. Thus it serves as Second Payment. So
Financial Factor is withholding 15% of the total of the invoices to collect.
That amount serves as warranty.

At Due Date Financial Factor approaches Customer to collect the dued invoices.
If successful, then Financial Factor releases the withheld warranty minus the
interest - Let it be 3% of total amount. Thus the amount released is 12%. Here
we have two transactions: the released warranty (Third Payment) and the
interest that is to be invoiced by the Financial Factor to the Factoree which
will be used to compensate and ultimately fully pay the Customer invoices
(Fourth Payment).

It is to be noticed that all payments and compensations are to be signed (CFDI
XML) on Financial Factor's name not on Customer's. Though from the accounting
point of view the customer has being paying its invoices.

Billing because of Loaning Services and Loaning Interest and Warranty
Withholding vary upon trust of the parties - Financial Factor and the Factoree.

How to use this module
----------------------

After installing this module you will be able to:

- See the Financial Factor field in Open or Paid Customer Invoices.
- Set a Financial Factor in a Open Customer Invoice if no other has been set.
- Set a Financial Factor to blank if there are no outstanding payments in the
  Customer Invoice.
- Switch to a different Financial Factor while there are no outstanding
  payments.
- Apply a payment from wizard `Register Payment` on a Customer Invoice bearing
  a Financial Factor. And having the CFDI XML payment signed on Financial
  Factor's name & VAT instead of Customer's.
- Apply a payment from wizard `Register Payment` on a Customer Invoice bearing
  no Financial Factor. And having the CFDI XML payment signed on Customer's
  name & VAT.
- Apply a payment in bulk using wizard `Register Payment` on Customer Invoice
  list view bearing the same Financial Factor. And having the CFDI XML payments
  signed on Financial Factor's name & VAT instead of Customer's.
- Apply a payment in bulk using wizard `Register Payment` on Customer Invoice
  list view bearing no Financial Factor. And having the CFDI XML payments
  signed on Customer's name & VAT.
- Apply a payment from `Bank Statement` on one or several Customer Invoices
  bearing the same Financial Factor. And having the CFDI XML payments signed on
  Financial Factor's name & VAT instead of Customer's.
- Apply a payment from `Bank Statement` on one or several Customer Invoices
  bearing no Financial Factor. And having the CFDI XML payments signed on
  Customer's name & VAT.

If a customer always use a Financial Factor, that could be defined in the
partner and will be propused by default when is created a paymnent.
