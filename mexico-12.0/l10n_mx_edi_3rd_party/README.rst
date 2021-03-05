Third Party Complement for the Mexican Localization
===================================================

This module adds to the mexican localization the possibility of selling
products on behalf of third parties, and to issue electronic invoices using
that feature.

This module implements the Third Party complement, whose specifications are
given by the SAT. Such specifications may be consulted at
`the SAT's reference page <https://www.sat.gob.mx/consulta/50103/genera-tu-factura-con-el-complemento-concepto-por-cuenta-de-terceros>`_.


Usage
=====

Instructions
------------


To use this module, you only need to create a customer invoice and fill the
field `On Behalf of`, in the line containing the product you would like to sell
on behalf of a third party.

  .. figure:: l10n_mx_edi_3rd_party/static/description/common.png
    :width: 600pt
    :alt: Creating an Invoice

When the invoice is validated, the complement node will automatically be
inserted in the CFDI for all products whose line has that field set. This
means, several products may be sold on behalf of third parties in the same
invoice, and they even could be sold each one on behalf of a different third
party.

In addition, this module supports all three variants described on the
complement's specifications:

- **The product is imported and sold first hand**:
  To specify the product is imported, fill the fields `Customs Number`,
  `Customs Expedition Date` and, optionally, `Customs Name`.

    .. figure:: l10n_mx_edi_3rd_party/static/description/case1.png
      :width: 600pt
      :alt: Invoice with imported product

- **The product is made from other products**:
  When a product is made from other products (parts or components) you may
  specify which ones are those sub-products. To do so, simply create a Bill of
  Materials for the product you are selling, and the first list for that
  product will be automatically taken when validating the invoice.

    .. figure:: l10n_mx_edi_3rd_party/static/description/case2.1.png
      :width: 600pt
      :alt: Creating a Bill of Materials

  Note that, as in the product, you may specify a part is imported by filling
  the fields `Customs Number`, `Customs Expedition Date` and, optionally,
  `Customs Name` in the Bill of Materials's line for that part.

    .. figure:: l10n_mx_edi_3rd_party/static/description/case2.2.png
      :width: 600pt
      :alt: Setting an imported part

- **The product is a lease**:
  If the product is a lease, e.g. it's a house's rent charge, you may specify
  so by setting the field `Property Taxes Account` in the product you would
  like to use as a lease, under the tab `Invoicing`.

    .. figure:: l10n_mx_edi_3rd_party/static/description/case3.png
      :width: 600pt
      :alt: Creating a lease product


Considerations
--------------

- In case of an imported product or part, take into account the fields
  `Customs Number` and `Customs Date` are required. If you fill only one of
  them, an error will occur.

- Some fields should be set in the third party, namely:

  - `Street Name`
  - `City`
  - `State`
  - `Zip`
  - `Country`,

  If some of the above fields are not set, no errors will occur, but no
  address information will be included into the complement node for that third
  party. If that happens, a warning message will be shown.

    .. figure:: l10n_mx_edi_3rd_party/static/description/consideration2.png
      :width: 600pt
      :alt: Warning message about required fields

- Products always need to have set the field `Code SAT`. However, that field is
  not taken into account when dealing with parts, so it's not required in such
  a case.


Bug Tracker
===========

Bugs are tracked on
`GitLab Issues <https://git.vauxoo.com/Vauxoo/mexico/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and
welcomed feedback.

Credits
=======


Contributors
------------

* Luis González <lgonzalez@vauxoo.com> (developer)
* Luis Torres <luis_t@vauxoo.com> (reviewer)

Maintainer
==========

.. figure:: https://www.vauxoo.com/logo.png
   :alt: Vauxoo
   :target: https://vauxoo.com
