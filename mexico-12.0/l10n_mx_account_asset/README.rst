Account Asset - Sale of Assets According to IFRS
================================================

This module adds a new button on Asset that will allow to sell it according
to IFRS standards.

Considering that it have an asset of 1500 as initial value and that it has
already depreciated 750.

Odoo's module at Disposing or Selling of the asset fully depreciates the asset.

.. figure:: l10n_mx_account_asset/static/src/img/fullydepreciation.png
   :width: 600pt


IFRS / IAS 16 - Derecognition - Paragraph 67 & 71.
--------------------------------------------------

-    67: The gain or loss arising from the derecognition of an item of property,
     plant and equipment shall be included in profit or loss when the item
     is derecognised (unless IFRS 16 Leases requires otherwise on a sale and
     leaseback). Gains shall not be classified as revenue.

-    71: The gain or loss arising from the derecognition of an item of property,
     plant and equipment shall be determined as the difference between the
     net disposal proceeds, if any, and the carrying amount of the item.

To comply with the aforementioned, a journal entry is created as follows:

.. figure:: l10n_mx_account_asset/static/src/img/journalentry.png
   :width: 600pt

Use
===

Before selling or disposing of the asset, the cogs account must be set up
in the asset category. **See the configuration section**

To sell or dispose of an asset according to IFRS, use the button **Sell Asset**

.. figure:: l10n_mx_account_asset/static/src/img/sellasset.png
   :width: 600pt

Extra features
--------------

Additionally, this module includes some useful actions for the management
of fixed assets.


* Action to automatically generate journal entries for depreciations (in draft),
  from the initial depreciation date to the current day.

   **To execute this action the asset must be confirmed before.**

.. figure:: l10n_mx_account_asset/static/src/img/before.png
   :width: 600pt


.. figure:: l10n_mx_account_asset/static/src/img/after.png
   :width: 600pt


.. figure:: l10n_mx_account_asset/static/src/img/journalentries.png
   :width: 600pt


*  Validate journal entries in draft.

.. figure:: l10n_mx_account_asset/static/src/img/validatejournalentries.png
   :width: 600pt


This action post all journal entries in draft status.

.. figure:: l10n_mx_account_asset/static/src/img/entriesvalidate.png
   :width: 600pt

*  Reopen Asset

   After sell or dispose an asset this button allows to pass the asset
   from the closed status to the open status.

   This button is only visible when the asset is in state "close".

.. figure:: l10n_mx_account_asset/static/src/img/reopenasset.png
   :width: 600pt



Installation
============

To install this module, you need to:

- Not special pre-installation is required, just install as a regular Odoo
  module:

  - Download this module from `Vauxoo/mexico
    <https://github.com/vauxoo/mexico>`_
  - Add the repository folder into your odoo addons-path.
  - Go to **Settings > Module list** search for the current name and click in
    **Install** button.

Configuration
=============

- The COGS Account must be configured in the asset category.

.. figure:: l10n_mx_account_asset/static/src/img/configuration.png
   :width: 600pt


Contributors
------------
* Humberto Arocha <hbto@vauxoo.com>
* Luis Torres <luis_t@vauxoo.com>
* Edilianny Sánchez <esanchez@vauxoo.com>

Maintainer
----------

.. figure:: https://www.vauxoo.com/logo.png
   :alt: Vauxoo
   :target: https://vauxoo.com

   This module is maintained by Vauxoo.

   A latinamerican company that provides training, coaching,
   development and implementation of enterprise management
   sytems and bases its entire operation strategy in the use
   of Open Source Software and its main product is odoo.
