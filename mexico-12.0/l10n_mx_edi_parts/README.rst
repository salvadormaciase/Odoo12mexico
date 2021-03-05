Invoiced Product Units
======================


This module helps to show in the invoice the product units that have been sold,
to do this it is necessary that the product tracking system is set to "By Unique
Serial Number".

The appropriate workflow should be:

- Set the traceability of the product as "By Unique Serial Number"
- Create a Sale Order with the product you just configure
- Confirm the sale order
- Go to the picking and set the lot/serials, and validate the picking
- Create the invoice and validate it

When the invoice is validated a tag 'cfdi:Parte' will be added in the XML for
each product that has a lot/serial number and this unique number will be set
as the 'NoIdentificacion' in the XML. This lot/serial number will be displayed
in the printed document too.

Contributors
------------
* Luis Torres <luis_t@vauxoo.com>
* Germana Oliveira <germana@vauxoo.com>

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
