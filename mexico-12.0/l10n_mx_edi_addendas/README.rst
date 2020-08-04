.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
    :alt: License: LGPL-3

================
Mexican Addendas
================

Usage:
======

This module provides the structure for when signing an invoice, the xml corresponding appears with the addenda information.

As a first step, each addenda must be added in its corresponding partner.

     .. figure:: ../l10n_mx_edi_addendas/static/src/img/partner_addenda.png
        :width: 600pt

The addenda information is taken from the fields that are explicitly included in the invoice, and for the case that the
information is not in a specific field, it is necessary fill the fields in the wizard that appears in the view invoice.

Each addenda adds a button in invoice view wich open a wizard where the extra information
for the addenda can be set it. The fields in each wizard depend on the information required
by the addenda corresponding to the partner in active invoice.

     .. figure:: ../l10n_mx_edi_addendas/static/src/img/wizard_button.png
        :width: 600pt

Actually, the addendas available are:

Amazon
------

This addenda is added automatically if the partner has the addenda selected, and
the mandatory data depends if it is an invoice or a credit note. If the document
is an invoice:

- The field `Reference/Descripcion` has to have the Amazon Purchase Orden number.

If the document is a credit note:

- The field `Reference/Descripcion` has to have the credit note type and the 
  reference document number, with this format: `TYPE|reference document number`.

The credit note type could be:

- `RET`: Vendor returns.
- `COOP`: Bills against Cogs issued by Amazon to our suppliers due to promotional
  agreements, price protection and volume incentives.
- `PQV`: Variations in quantity between the invoiced merchandise versus that
  received in our warehouse.
- `PPV`: Price variations, between those established in the purchase order and
  those used to prepare the invoice.
- `QPD`: Discounts for prompt payment.

And the reference document number:

- If credit note type is: `RET` or `COOP`, it it the document number generated
  in Central Vendor.
- If the credit note type is: `PQV`, `PPV` or `QPD`, it is the Amazon Purchase number.


Chrysler
--------

A button with name ``ADDENDA CHRYSLER`` is added in invoice view. This button opens the
following wizard:

     .. figure:: ../l10n_mx_edi_addendas/static/src/img/wizard_addenda_chrysler.png
        :width: 600pt

In the wizard is provided the information corresponding to each field.

Ford
----

A button with name ``ADDENDA FORD`` is added in invoice view. This button opens the
following wizard:

     .. figure:: ../l10n_mx_edi_addendas/static/src/img/wizard_addenda_ford.png
        :width: 600pt

In the wizard is provided the information corresponding to each field.

Porcelanite
-----------

A button with name ``ADDENDA PORCELANITE`` is added in invoice view. This button opens the
following wizard:


In the wizard is provided the information corresponding to each field.

Bosh
----

A button with name ``ADDENDA BOSH`` is added in invoice view. This button opens the
following wizard:


In the wizard is provided the information corresponding to each field.

Femsa
-----

To use this Addenda, you should provide some values some of which are
configured in the partner's Internal Reference field with the format
`noSociedad|noProveedor`:

* `noSociedad`, is the univocal identifier for each of FEMSA's divisions.
* `noProveedor`, data assigned by the supply area, you must prefix five zeros
  to this number.
* `Remission Number`, the sale order which this invoice comes from. This value
  is taken from the field "Source Document".
* `Purchase Order`, the number of the customer's purchase order. This value
  is taken from the invoice's field "Reference/Description".


A button with name ``ADDENDA FEMSA`` is added in invoice view. This button opens
the following wizard:

     .. figure:: ../l10n_mx_edi_addendas/static/src/img/wizard_addenda_femsa.png
        :width: 600pt

In the wizard is provided the information corresponding to each field needed:

* `noEntrada`, is the warehouse receipt number.

Mabe
----

This addenda do not have extra attributes.

Only is necesary set in the customer ref the value that must be assigned in
the supplier code and the place of delivery with the format: 'supplier code|place
of delivery'.

If the record comes from an sale, set in the sale the customer ref (PO)

Calsonic Kansei
---------------

This addenda requires only one field:

- **Purchase Order**: the number of the customer's purchase order. This value
  is taken from the invoice's field "Reference/Description".

PepsiCo Mexico
--------------

A button with name ``ADDENDiA PEPSICO`` is added in invoice view.
This button opens the following wizard:

     .. figure:: ../l10n_mx_edi_addendas/static/src/img/wizard_addenda_pepsico.png
        :width: 600pt

In the wizard is provided the information corresponding to each field needed:

* `Payment request`, Indicates the number generated for the payment request
  to the services provider.
* `Reception Number`, Is the reception number in the customer system.
* `Purchase Order`, the number of the customer's purchase order. This value
  is taken from the invoice's field "Reference/Description". It will be be set
  on the attribute `idPedido`

To this addenda is necessary set in the customer ref the value that was
assigned from PepsiCo to your company, and will be used in the attribute
`idProveedor`.

AAM Maquiladora México, S. de R.L. de C.V.
------------------------------------------

This addenda uses the following fields:

- **Operational Organization**: a division code internally used by AAM. This
  code is provided to the seller when the order is made.
- **Product SAP Information**: SAP information of the product, as handled by
  AAM: description, code and unit of measure. This information has to be set on
  each invoice line.
- **Purchase Order**: the number of the customer's purchase order. This value
  is taken from the invoice's field "Reference/Description".
- **Requisitor**: information of the person who made the requisition: name and
  e-mail. Such information is taken from the customer of the invoice.
- **File**: The PDF file corresponding to the printed copy of the invoice,
  encoded in base64. This value is automatically filled using the invoice
  report.

Other values are static and will need to be set up per issuer on the template:

- **Bank Name**: the name of the bank used to receive the invoice payment.
- **Bank CLABE**: The standardized banking cipher for Mexico of the bank
  used to receive the invoice payment.
- **Supplier Code**: A code assigned by AAM to their customers.

The above values may be easily identified on the template because they are
enclosed in double-hyphens. For instance, the bank name is found as
``--Bank name here--``.

Agnico Eagle México, S.A. de C.V.
---------------------------------

This addenda requires only one field:

- **Purchase Order**: the number of the customer's purchase order. This value
  is taken from the invoice's field "Reference/Description".

Edumex, S.A. de C.V.
--------------------

This addenda uses only one field:

- **Incoming Number**: the code given to the product when it arrives at stock
  location. This code is provided by the supplier.

La Comercial City Fresko
------------------------

This addenda require to configure some additional values in the Client:

- **Internal Reference**: this is the 'Internal Reference' field found in the
  'Sales & Purchase' tag of the client's record. Here you will set the GLN of 
  the client.

- **Notes**: this is the 'Notes' field found in the 'Shipping Address' of the
  client. Here you will set the GLN of the shipping address, if this field is
  not set the GLN for the shipping address in the addenda will be the same as
  the client itself.

Now, the addenda requires to fill this fields:

- **Additional Reference Code**: this is the attribute to specify the code of
  Additional references and the possible values are:

  - *AAE*: Property account
  - *CK*: Check number
  - *ACE*: Document number (Referral)
  - *ATZ*: Approval number.
  - *AWR*: Number of document that is replaced
  - *ON*: Order number (buyer)
  - *DQ*: Merchandise receipt sheet
  - *IV*: Invoice Number

- **Additional Reference Number**: this is to express the additional reference
  number and it is related to the selection of the previous field.

- **Date Purchase Order**: this is the date of the purchase order.

- **Order Number**: this is the number of the pruchase order.

- **Lines**: these are the products from the invoice line with theirs supplier
  code. You can set the product's supplier code from here or from the Providers 
  in the 'Purchase' tag in the product configuration. This is the product GLNI
  code.

Las Encinas, S.A. de C.V.
-------------------------

This addenda does not require to configure additional values, but you may notice that uses the following fields:

- **Change rate**: This field is automatically calculated, and depends in the
  currency you have configured for the invoice.

- **Currency name**: This value will be get from the currency you are using in
  the current invoice.

Envases Universales de México
-----------------------------

This addenda uses the following fields:

- **Incoming Code**: The code given to the product when it arrives at stock
  location. This code is provided by the customer.

- **Purchase Order**: The number of the customer's purchase order. This value
  is taken from the invoice's field "Reference/Description".

Flextronics Holdings Mexico Dos, S.A. de C.V.
---------------------------------------------

This addenda uses the following values:

- **Purchase Order**: the number of the customer's purchase order. This value
  is taken from the invoice's field "Reference/Description".

Other values are static and will need to be set up per issuer on the template:

- **Flextronics company**: Id for the Flextronics company.

- **Supplier number**:  Number given to identify the supplier.

The above values may be easily identified on the template because they are
enclosed in double-hyphens. For instance, the flextronics company may be found as:

``--Flextronix Company here--``

Nestle Mexico, S.A. De C.V.
---------------------------

This addenda supports both cases for Nestle's addendas, namely customer
invoices and credit notes. The following values are common for both cases:

- **SAP Code**: The product's SAP code as handled by Nestle. This code has to
  be set on each invoice line.
- **Purchase Order**: the number of the customer's purchase order. This value
  is taken from the invoice's field "Reference/Description".
- **Bill To**: billing address information: street, colony, zip, city and
  state. Such information is taken from the invoice address contact
  configured for the partner.
- **Ship To**: shipping address information: street, colony, zip, city and
  state. Such information is taken from the shipping address contact
  configured for the partner.

The following values are case-specific:

- **Incoming Code**: Invoice validation code. This is applicable only for
  invoices, not credit notes.
- **Invoice Number**: If this is a credit note, specifies what invoice this
  credit note comes from. This is filled with the origin field.

Other values are static and will need to be set up per issuer on the template:

- **MXN bank name**: the name of the bank used to receive invoice payments
  in MXN.
- **MXN bank number**: the number of the bank used to receive invoice payments
  in MXN.
- **MXN bank CLABE**: the standardized banking cipher for Mexico of the bank
  used to receive invoice payments in MXN.
- **MXN bank number**: the number of the bank used to receive invoice payments
  in USD.
- **MXN bank CLABE**: the standardized banking cipher for Mexico of the bank
  used to receive invoice payments in USD.

The above values may be easily identified on the template because they are
enclosed in double-hyphens. For instance, the MXN bank name is found as
``--MXN bank name here--``.

Sanmina-SCI Systems de Mexico S.A. DE C.V.
------------------------------------------

This addenda uses the following values:

- **Purchase Order**: the number of the customer's purchase order. This value
  is taken from the invoice's field "Reference/Description".

The following values are static and will need to be set up per issuer on the template:

- **Collection Email**: The collection team's e-mail.

- **Customer Code**: Code used to identify the customer.
  This code is provided by Sanmina.

The above values may be easily identified on the template because they are
enclosed in double-hyphens. For instance, the collection email can be found as

``--Collection email here--``

Sidel de México, S.A. DE C.V.
-----------------------------

This addenda uses only one field:

- **Purchase Order**: the number of the customer's purchase order. This value
  is taken from the invoice's field "Reference/Description".

Vallen
------

This addenda uses only one field:

- **Purchase Order**: The number of the customer's purchase order. This value 
  is taken from the invoice's field "Reference/Description".

Yanfeng Mexico Interiors, S de RL de CV
----------------------------------------

This addenda uses only one field:

- **Purchase Order**: The number of the customer's purchase order. This value
  is taken from the invoice's field "Reference/Description".

ZF Suspension Technology Guadalajara, S.A. de C.V. (ZF Mexico)
--------------------------------------------------------------

This addenda uses only one field:

- **Purchase Order**: the number of the customer's purchase order. This value
  is taken from the invoice's field "Reference/Description".

SAMS Mexico
___________

This addenda is added automatically if the partner has the addenda selected, You should provide some values which are
configured in the invoice's Internal Reference field with the format
`|po_date`:

- The field `Date Purchase Order` is The Purchase order confirmation date.

A button with name ``ADDENDA SAMS`` is added in invoice view. This button opens
the following wizard:

    .. figure:: ../l10n_mx_edi_addendas/static/src/img/wizard_addenda_sams.png
        :width: 600pt

In the wizard is provided the information corresponding to each field needed.
The attribute SuppCode were added in the Addenda. Please be sure to set up this value in the company.
The barcode in product is required for this addenda.

Airbus
------

This addenda is added automatically if the partner has the addenda selected. A 
button with name ``ADDENDA AIRBUS`` is added in the invoice view.

Uses the following values:

- **Concept**: Concept that is being invoiced, according to the catalog defined by Airbus.
- **Description**: Text that briefly describes the invoice.
- **Purchase Order**: The number of the customer's purchase order. This value is taken from the invoice's field 
  "Reference/Description".
- **Reception Number**: It is receiving number in the customer system.
- **Delivery Number**: It is the remission number or delivery note of the supplier.
- **Lines**: 
  * *Sap Sequence*: Position of the item in the purchase order.
  * *Material*: Airbus material number, when it is material or consumables (optional).
  * *UoM*: Airbus Helicopters unit of measure.
- **Attached File (xls, xlsx, pdf, jpg)**: Indicate the attached file if necessary (optional).
- **Type Operation**: Required for expense accounts / notes position with customs (optional).
- **Custom**: The number of the invoice's pedimentos. This value is taken from the invoice line's field 
  "Customs number" (optional).

Some values are static and will need to be set up per issuer on the template:

- **Num Supplier**: Number, assigned to partner, as found in SAP. It is
  enclosed in double-hyphens. For instance, the field is found as: 
  ``--Supplier num here--``.


Technical:
==========

To install this module go to ``Apps`` search ``l10n_mx_edi_addendas`` and click
in button ``Install``.

When the module is installed it is necessary activate the required addendas. To do
that go to Invoicing configuration settings and search by ``MX EDI addendas``. There
you can find the available addendas in the sistem.

     .. figure:: ../l10n_mx_edi_addendas/static/src/img/l10n_mx_edi_addendas_conf.png
        :width: 600pt


Contributors
------------

* Yennifer Santiago <yennifer@vauxoo.com>
* Nhomar Hernández <nhomar@vauxoo.com>
* Julio Serna Hernández <julio@vauxoo.com>
* Arturo Flores <arturo@vauxoo.com>
* Luis González <lgonzalez@vauxoo.com>
* Deivis Laya <deivis@vauxoo.com>

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

