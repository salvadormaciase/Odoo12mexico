CDFI to Transfers with External Trade
=====================================

This modulo support the generation of CFDI(s) to transfer your merchandise with the External Trade Complement.

Usage
=====

- Create an invoice with the same partner that the company.

  .. image:: l10n_mx_edi_transfer_external_trade/static/src/img/partner.png
    :width: 400pt
    :alt: Partner

- Use a discount of 100 % in all invoice lines (Invoice's Total must be equal to 0).

  .. image:: l10n_mx_edi_transfer_external_trade/static/src/img/total.png
    :width: 400pt
    :alt: Total

- Check as true the invoice field "Need external trade?" and fill the other necessary fields for external trade.

  .. image:: l10n_mx_edi_transfer_external_trade/static/src/img/external_trade.png
    :width: 400pt
    :alt: External Trade

- The attribute MotivoTraslado will be set following this rules:
  
  * 01 (Envío de mercancías facturadas con anterioridad): When the invoice has a related document with the type of relation '05'.

    .. image:: l10n_mx_edi_transfer_external_trade/static/src/img/motivo_traslado01.png
      :width: 400pt
      :alt: MotivoTraslado 01

  * 02 (Reubicación de mercancías propias): otherwise.

    .. image:: l10n_mx_edi_transfer_external_trade/static/src/img/motivo_traslado02.png
      :width: 400pt
      :alt: MotivoTraslado 02

   Another kind of "MotivoTraslado" is not supported.


Maintainer
==========

.. image:: https://s3.amazonaws.com/s3.vauxoo.com/description_logo.png
   :alt: Vauxoo
   :target: https://vauxoo.com
