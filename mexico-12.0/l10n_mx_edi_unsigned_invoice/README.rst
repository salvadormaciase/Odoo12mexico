.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
    :alt: License: LGPL-3

Payments on Unsigned Invoices
=============================

This module allows users to apply payments on invoices that are not signed yet.

The default behavior of the Mexican localization is to validate that the invoices
are paid before users can apply payments on it. With this module you don't have that
restriction. Intead, you will be able to make payments on unsigned invoices, Odoo will
just post a note on the invoice as a notification that the invoice is paid before
being signed.

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


Bug Tracker
===========

Bugs are tracked on
`GitHub Issues <https://github.com/Vauxoo/mexico/issues>`_.
In case of trouble, please check there if your issue has already been reported.

Credits
=======

**Contributors**

* Sabrina Romero <sabrina@vauxoo.com> (Planner)
* Erick Birbe <erick@vauxoo.com> (Developer)

Maintainer
==========

.. image:: https://s3.amazonaws.com/s3.vauxoo.com/description_logo.png
   :alt: Vauxoo
