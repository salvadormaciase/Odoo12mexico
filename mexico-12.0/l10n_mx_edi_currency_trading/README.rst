EDI Currency Trading Complement for the Mexican Localization
============================================================

This module adds to the mexican localization the possibility of generating
electronic invoices for selling and purchasing foreign currencies, so it may be
used by brokers and currency exchanges.

This module implements the currency trading complement, whose specifications
are given by the SAT. Such complement is required for all invoices issued for
purchasing or selling currencies, and its specifications may be consulted at
`the SAT's reference page`_.

.. _the SAT's reference page: http://www.sat.gob.mx/informacion_fiscal/factura_electronica/Paginas/complemento_divisas.aspx


Additional Notes
================

When this module could not be installed and all their records must be manually
inserted, an additional step is required. Since the Python constraint wouldn't
be installed, an automated action record must be inserted taking the content of
the file ``doc/base_automation.xml`` to fit that purpose. Themodule
``base_automation`` must also be installed in order to the automated action to
be able to run.


Credits
=======


Contributors
------------

* Luis González <lgonzalez@vauxoo.com>
* Luis Torres <luis_t@vauxoo.com>

Maintainer
==========

.. image:: https://www.vauxoo.com/logo.png
   :alt: Vauxoo
   :target: https://vauxoo.com
