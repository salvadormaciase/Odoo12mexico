Complement to Retailer Mexican Localization
==========================================================================

To complete the necessary information for this complement is necessary:

1. Create a customer invoice, without validating it, look for the field
   "Reference/Description" in the "Other Info" section and put the number
   of the purchase order there.
   **Note:** If the invoice comes from a sale order, this reference is taken from
   the Customer Reference
2. Once the purchase order number has been placed in the field, call the
   `Complement Retailer` button at the top of the invoice page.
3. In this Wizard we find several fields to complete information required
   for it, where:

   - Document Status: Here must be selected the value for the attribute
     `documentStatus`, (`original`, `copy`, `reemplaza` or `delete`).
   - DeliveryNote: For this node the fields `referenceIdentification`
     (counter-referral) and `ReferenceDate` (counter-referral date) were added,
     which will be used at the CFDI.
   - Purchase Order Date.
   - Purchase Contact Name: In this field the number or name of the purchasing
     contact needs to be placed (Partner's department).
   - Discount/Charge type: Here must be selected the value for the allowance
     charge type (`OFF_INVOICE`, `BILL_BACK`).

   .. figure:: l10n_mx_edi_retailer/static/src/img/wizardretailercomplement.png
      :alt: Wizard Retailer Complement

With debug mode, you need to go to ``Settings -> Technical -> Views`` and search
for the view named `retailer`, there you will find 3 static values that need to
be modified:

- **Buyer's GLN**: Buyer's global localization number.
- **Supplier's GLN**: Supplier's global localization number.
- **Supplier's Number**: Supplier's number.

Static values can be identified in the complement template as they are enclosed
with two dashes. For example the supplier's number is found as
``--Supplier's Number here--``.

**Note**:
The suppliers that its buyer is `Liverpool` need to contact them (Liverpool) to
send some test CFDIs before sending the productive ones.
