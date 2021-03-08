Customs DIOT
============

This module allows generate the entries required to get the DIOT report for
customs payments.

To get this, is necessary create a new record with the same data that in
the custom, and relate all the invoices that was importad with it.

Notes:

*In some cases there may be a difference between the amount of the customs and
the amount of the bill of customs.*

When this happens, an auxiliary line is created on the invoice with the
difference amount.

To set up the accounting account to which that amount of difference will go:

Should create a system parameter ``Settings / Technical / System parameters``

The parameter must have the key ``customs_difference_account`` and the value
must be the id of the accounting account.

If this parameter does not exist, the invoice journal account will be use.

*Line apportionment*

When is add a custom for importation, are added all the invoices that was
imported with that document. And could be different vendors, then, could be
reported in the DIOT the taxes amount between all the vendors or could be used
a global vendor. By default is used the global vendor, but could be add a
system parameter with the key ``customs_line_apportionment`` and the amounts
for Freight, Other increments, IGI, DTA and CC could be join in a line by
each vendor in the customs.


Installation
============

  - Download this module from `Vauxoo/mexico
    <https://github.com/vauxoo/mexico>`_
  - Add the repository folder into your odoo addons-path.
  - Go to ``Settings > Module list``, search for the current name and click in
    ``Install`` button.

Configuration
=============


Bug Tracker
===========

Bugs are tracked on
`GitHub Issues <https://github.com/Vauxoo/mexico/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and
welcomed feedback
`here <https://github.com/Vauxoo/mexico/issues/new?body=module:%20
l10n_mx_edi_customs_diot%0Aversion:%20
10.0.1.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_

Credits
=======

**Contributors**

* Nhomar Hernández <nhomar@vauxoo.com> (Planner/Auditor)
* Luis Torres <luis_t@vauxoo.com> (Developer)

Maintainer
==========

.. image:: https://s3.amazonaws.com/s3.vauxoo.com/description_logo.png
   :alt: Vauxoo
