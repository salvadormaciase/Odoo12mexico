EDI Educational Institutions (IEDU) Complement for the Mexican Localization
===========================================================================

This module adds IEDU complement for the issuance of CFDI(s) by private educational institutions. This complement allows to make deductible the tuition payment of private educational institutions.

Use
---
- For each educational level managed in the institution, the educational level
  and the institution's code must be configured in the account journal

.. image:: l10n_mx_edi_iedu/static/src/img/journals.png
   :align: center
   :width: 200pt

.. image:: l10n_mx_edi_iedu/static/src/img/education_levels.png
   :align: center
   :width: 200pt

- If these values are not configured, an error will be obtained when generating the CFDI

.. image:: l10n_mx_edi_iedu/static/src/img/error.png
   :align: center
   :width: 200pt

- Create a new invoice and set Student field for all concepts who applies the complement.

.. image:: https://drive.google.com/uc?export=&id=1sTVtF8RcHo-hKK9CCa-lqAVVq0IkAPq4

- Make sure that the student has the CURP and a tag with the educational level.

.. image:: https://drive.google.com/uc?export=&id=1si4sRqbJPiE9fFQp8F7h-pi21Z2tKv-v
