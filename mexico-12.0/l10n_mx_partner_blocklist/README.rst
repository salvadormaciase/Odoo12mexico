Partner Blocklist for Mexican Localization
==========================================

This module allow to know if a company or person is somehow blocked by the SAT 
because of ilegal operations with CFDIs, and it avoid to sell or buy to those 
companies or person.

This module provides a method that will download the blocked partners list and
process it to be save it in Odoo, so it can be consulted every time needed.

Configure
=========

To be able to download the list you have to set the URL, this can be found in 
http://omawww.sat.gob.mx/cifras_sat/Paginas/datos/vinculo.html?page=ListCompleta69B.html
and copy the 'Definitivos' URL link and set 'l10n_mx_partner_blocklist_url'
field in System Parameters.

After that the Schedule Action 'Partner Blacklist Process' will download and
process the list automatically every day.

Also make sure to create the contextual action in the 'Partner Blocklist Status'
Server Action, to be able to check the partners status.

Usage
=====

If all the configuration was done you can go to any partner and check if it is
blocked or not. Every partner will have a color (grey, green or red) point in 
the field Partner Status.

.. image:: l10n_mx_partner_blocklist/static/src/partner_blocklist_partner_state.png
   :align: center
   :width: 200pt

The grey color means there is no information about that partner or the partner
VAT is not set. The green color means that the partner is not blocked and the 
red color means that partner is blocked and you should not do commertial 
transactions with that partner.

This information will also be use to block a sale, purchase or invoice to a
blocked partner. If you still want to allow this operations with that partner
you will have to remove the corresponding record and try to confirm the document.

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

* Luis Torres <luis_t@vauxoo.com> (reviewer)
* Germana Oliveira <germana@vauxoo.com> (developer)

Maintainer
==========

  .. figure:: https://www.vauxoo.com/logo.png
     :alt: Vauxoo
     :target: https://vauxoo.com


