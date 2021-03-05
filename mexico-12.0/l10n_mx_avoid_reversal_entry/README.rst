
.. figure:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
    :alt: License: LGPL-3

Avoid Reversal Entries
======================

When removing a full reconciliation, we need to delete any eventual
journal entry that was created to book the fluctuation of the foreign
currency's exchange rate.

When removing a partial reconciliation, also unlink its full
reconciliation if it exists.

.. contents::

Installation
============

To install this module, you need to:

- Not special pre-installation is required, just install as a regular Odoo
  module:

  - Download this module from `Vauxoo/mexico
    <https://github.com/vauxoo/mexico>`_
  - Add the repository folder into your odoo addons-path.
  - Go to ``Settings > Module list`` search for the current name and click in
    ``Install`` button.

Configuration
=============

To configure this module, you need to:

* The cash basis and exchange difference journal must allow cancel entries.

Bug Tracker
===========

Bugs are tracked on
`GitHub Issues <https://github.com/Vauxoo/mexico/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and
welcomed feedback
`here <https://github.com/Vauxoo/mexico/issues/new?body=module:%20
l10n_mx_avoid_reversal_entry%0Aversion:%20
11.0.1.0.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_

Credits
=======

**Contributors**

* Humberto Arocha <hbto@vauxoo.com> (Planner/Auditor)
* José Robles <josemanuel@vauxoo.com> (Developer)

Maintainer
==========

.. figure:: https://s3.amazonaws.com/s3.vauxoo.com/description_logo.png
   :alt: Vauxoo
