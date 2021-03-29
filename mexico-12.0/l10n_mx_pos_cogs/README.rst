.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

POS with COGS moves
=====================

- When a order from point of sale is generated with products that have
  perpetual inventory valuation, it is needed create a journal entry for the
  cost of this products at the moment to the order is created(COGS).

To complete with this we extend the process of order creation(from point of sale)
to create and post the journal entry for cost concept. This process work the following way.


- Orders will continue to be created in the original way

  .. image:: https://drive.google.com/uc?export=view&id=0B2kzKLGF6ZvLUmZsMkpNOEYyZzA
  .. image:: https://drive.google.com/uc?export=view&id=0B2kzKLGF6ZvLZlQtcnppQ2xaY0k
  .. image:: https://drive.google.com/uc?export=view&id=0B2kzKLGF6ZvLQUthSjRqbUg2dXc

- The only difference that you will see is in the order view, a new field in Extra Info page with
  the new journal entry created by cost concept.

  .. image:: https://drive.google.com/uc?export=view&id=0B2kzKLGF6ZvLTWNBamxEUTlEeW8
  .. image:: https://drive.google.com/uc?export=view&id=0B2kzKLGF6ZvLbGdYUmppVGZHM0U

- The Journal Entry is created in draft state, this is posted automatically when the sesion is closed

  .. image:: https://drive.google.com/uc?export=view&id=0B2kzKLGF6ZvLZ0NIVE5obDNhQ1U

- This is the normal way. Now we have three variants in the process. We will
  explain the three variants that we can have in the order

   - When an invoice is created for the order this journal entry by cost
     concept is redundant, this because the journal entry created by the
     invoice considers the cost in their journal items. To avoid the redundant
     explained before, the Journal Entry for COGS created in the order is
     removed when a invoice is created.

  .. image:: https://drive.google.com/uc?export=view&id=0B2kzKLGF6ZvLV3Z4czBOZkhqNUU

- When a return is created is needed to revert the Journal Entry(COGS)
  created in the main order. To solve that, we created a new Journal Entry
  by cost concept but changing the value of the credit and debit  with
  respect to the Journal Entry created in the main order.

  .. image:: https://drive.google.com/uc?export=view&id=0B2kzKLGF6ZvLV3UyQVBaaXg4Nms

  .. image:: https://drive.google.com/uc?export=view&id=0B2kzKLGF6ZvLcU5KRTBZTWdJNlE

  .. image:: https://drive.google.com/uc?export=view&id=0B2kzKLGF6ZvLQ0Fxbmw2Nmd6MGc

- The third variation is a mix between the two explained before.
  When you generate a return but the main order has an invoice we do not
  need to create a Journal Entry for the return because the invoice will be
  manage the Journal Items when the refund of the invoice will be created.
  This means that we will not generate Journal Entry by cost concept for
  those returns that have an invoice in their main orders.

  .. image:: https://drive.google.com/uc?export=view&id=0B2kzKLGF6ZvLZHBLT2hNZnlyNTA

  .. image:: https://drive.google.com/uc?export=view&id=0B2kzKLGF6ZvLbDhzSHJjVXZoeFk

- When the sesion is closed all Journal Entry by cost concept(COGS) will be posted automatically

  .. image:: https://drive.google.com/uc?export=view&id=0B2kzKLGF6ZvLSXVGZW9iY3l4ckU

  .. image:: https://drive.google.com/uc?export=view&id=0B2kzKLGF6ZvLdy1jNVNZQ1QwZlU

  .. image:: https://drive.google.com/uc?export=view&id=0B2kzKLGF6ZvLdzBORnBfaEVPQ1k


.. contents::

Installation
============

To install this module, you need to:


  - Download this module from `Vauxoo/mexico
    <https://github.com/vauxoo/mexico>`_
  - Add the repository folder into your odoo addons-path.
  - Go to ``Settings > Module list`` search for the current name and click in
    ``Install`` button.

Configuration
=============

To configure this module, you need to:

- The valuation of the product or category must be perpetual.

  .. image:: https://drive.google.com/uc?export=view&id=0B2kzKLGF6ZvLeC1KUUktX1dpbEk

- Configure the needed accounts in the category or the product to create the Journal Entries for cost(COGS) in the POS order.
  - Expense Account
  - Stock Input Account
  - Stock Ouput Account

  .. image:: https://drive.google.com/uc?export=view&id=0B2kzKLGF6ZvLUm9Ec01VYkpqSGc

- Allow Canceling Entries in the Journal used for the POS orders.

  .. image:: https://drive.google.com/uc?export=view&id=0B2kzKLGF6ZvLaVlfNVpYdEE2Sm8

Bug Tracker
===========

Bugs are tracked on
`GitHub Issues <https://github.com/Vauxoo/mexico/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and
welcomed feedback
`here <https://github.com/Vauxoo/mexico/issues/new?body=module:%20
l10n_mx_edi_pos%0Aversion:%20
8.0.2.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_

Credits
=======

**Contributors**

* Nhomar Hernandez <nhomar@vauxoo.com> (Planner/Auditor)
* Jose Morales <jose@vauxoo.com> (Developer)

Maintainer
==========

.. image:: https://s3.amazonaws.com/s3.vauxoo.com/description_logo.png
   :alt: Vauxoo
