Complements for Fuel Consumption
================================

This module manages the complements:

* **Fuel account statement** (EstadoDeCuentaCombustible) this is needed when:

  - The company is only an authorized issuer of electronic purses
  - The company is an authorized issuer of electronic purses but also a 
    service station.

|

* **Fuel consumption** (ConsumoDeCombustibles) this is needed when:

  - The company is only an authorized issuer of electronic purses
  - The company is only a service station.

The next fields are needed for this complements to work:

- **Company** field: `Is Electronic Purse Issuer?`

  This identifies when the company is an authorized issuer of electronic purses.

|

  .. figure:: ../l10n_mx_edi_fuel/static/src/fuel_company.png

|


- **Partner** fields: `Tags` and `Internal Reference`

  The `Tags` identifies the partner as a service station, here the tag `Service
  Station` should be selected if you wanto to identify a partner as a service
  station. If the company is the service station this fields works the in same
  way, this time in the company's partner.

  The `Internal Reference` field is the service station number (it is the
  `claveEstacion` or `ClaveEstacion` field in the complements).

|

  .. figure:: ../l10n_mx_edi_fuel/static/src/fuel_partner.png
     :align: center
     :width: 300pt

|


- **Product** fields: `Need Fuel Billing?` and `Internal Reference`

  The `Need Fuel Billing?` identifies the products that should be included in
  the complement.
 
|

  .. figure:: ../l10n_mx_edi_fuel/static/src/fuel_product2.png
     :align: center
     :width: 700pt

|

  Also, you have to set the proper type in the `Internal Reference` field having
  the following in mind (it is the `TipoCombustible` or `tipoCombustible` field
  in the complements):

  - 1 : Gasoline less than 92 octane
  - 2 : Gasoline greater than or equal to 92 octane
  - 3 : Diesel
  - 4 : Marine Diesel
  - 5 : Other

|

  .. figure:: ../l10n_mx_edi_fuel/static/src/fuel_product3.png
     :align: center
     :width: 700pt

|

- **Invoice** field: `Electronic Purse Issuer Reference`

  This is used when the company is only a service station to identify:

  * The electronic purse number (it is the `Identificador` or `identificador`
    field in the complements)
  * The electronic purse owner bank account (it is the `NumeroDeCuenta` or
    `numeroDeCuenta` field in the complements)

  With the format: electronic purse number|electronic purse owner bank account

|

  .. figure:: ../l10n_mx_edi_fuel/static/src/fuel_reference.png
     :align: center
     :width: 700pt

|

THE COMPANY IS ONLY AN ELECTRONIC PURSE ISSUER
----------------------------------------------

When the company is only an electronic purse issuer you have to make sure:

  - Set the field `Is an Electronic purse issuer?`

In this case, the company will have to issue two complements:

  * A CFDI of entry with EstadoDeCuentaCombustible (this is a normal Invoice)
  * A CFDI of egress with ConsumoDeCombustibles (this is a credit note)

So, when the company receives a notification that a person has paid some fuel
with an electronic purse, the company have to issue an Invoice with the complement
**EstadoDeCuentaCombustible** for this, you have to make sure:

  - The Client has an electronic purse number set in the `Internal Reference`
    field (it is the `Identificador` field in the complement).
  - In the invoice lines, you have to select the `Service Station` which have to 
    have the `Internal Reference` field set and the tag 'Service Station' selected
    in the `Tags` field. You can even select a different service station per line.
  - The invoice lines should have a fuel product with `Need Fuel Billing` field
    set to true, and the fuel type set in `Internal Reference` field.

|

  .. figure:: ../l10n_mx_edi_fuel/static/src/fuel_partner1.png
     :align: center
     :width: 700pt

|

Once the Invoice is validated and signed you can issue the CFDI of egress with
the complement **ConsumoDeCombustibles**, this is done with a Credit Note (right
now this credit note have to be created by the user).

To issue this complement you have to make sure:

  - The Client is the Service Station
  - The `Partner Bank` field in the credit note is set (this is the `numerDeCuenta`
    field in the complement)
  - The invoice lines have a fuel product with `Need Fuel Billing` field set
    to True and the `Internal Reference` with the fuel type
  - The `CFDI Origin` field have the folio number from the Invoice with the
    EstadoDeCuentaCombustible (this is the `folioOperacion` field in the complement)

|

  .. figure:: ../l10n_mx_edi_fuel/static/src/fuel_credit_note1.png
     :align: center
     :width: 700pt

|

    - The electronic purse number is set (this is the `identificador` field in
      the complement), you can set this using the `Reference/Description`
      field in the Invoice.

|

  .. figure:: ../l10n_mx_edi_fuel/static/src/fuel_credit_note2.png
     :align: center
     :width: 700pt

|

**Note**

Here the `Service Station` field in the invoice lines is not needed because the
service station data will be taken from the partner (which is the Service Station).


Once the credit note is validated and signed, it has to be sent to the Service
Station.

|

THE COMPANY IS ONLY A SERVICE STATION
-------------------------------------

When the company is only a service station you have to make sure:

  - `Electronic Purse Issuer` is set to False in company
  - Make sure the fiel `Internal Reference` in the company's partner is set
    with the service station number (this is the `claveEstacion` in the
    compement)

In this case, the company has to issue an income CFDI with **ConsumoDeCombustibles**
complement, but this is only possible once the company receives the egress CFDI
with the same complement (ConsumoDeCombustibles) from the Electronic Purse Issuer.
This is so because the CFDI issued for the service station have to match the 
egress CFDI sent by the Electronic Purse Issuer, like the Fiscal Folio, the
amounts, etc.

To issue the CFDI with the `ConsumoDeCombustibles` complement, you have to make
sure:

  - The Client is General Public with a generic RFC
  - The field `CFDI Origin` is set with the credit note Folio number issued by
    the Electronic Purse Issuer (this is the `folioOperacion` field in the complement)
  - The invoice lines should have a fuel product with `Need Fuel Billing` field
    set to true, and the fuel type set in `Internal Reference` field.

|

  .. figure:: ../l10n_mx_edi_fuel/static/src/fuel_reference1.png
     :align: center
     :width: 700pt

|

- The Electronic `Purse Issuer Reference` field should be filled following the 
  instructions described before.

|

  .. figure:: ../l10n_mx_edi_fuel/static/src/fuel_reference2.png
     :align: center
     :width: 700pt

|

**Note**

Here the `Service Station` field in invoice lines is not needed because the service
station data will be taken from the company (which is the service station).

|

THE COMPANY IS AN ELECTRONIC PURSE ISSUER AND A SERVICE STATION
---------------------------------------------------------------

When the company is an electronic purse issuer and a service station you have
to make sure:

  - The company's partner has a 'Service Station' tag in `Tags` field.
  - The company's partner has a service station number in `Internal Reference`
    field.
  - The `Electronic Purse Issuer` is set to True in the company

In this case, the company will only need to issue the EstadoDeCuentaCombustible
complement, following the same instructions when the company is only an electronic
purse issuer.

|

For more information in the `SAT page for EstadoDeCuentaCombustible <http://www.sat.gob.mx/informacion_fiscal/factura_electronica/Paginas/EstadoDeCuentaCombustible.aspx>`_.

For more information in the `SAT page for ConsumoDeCombustibles <http://www.sat.gob.mx/informacion_fiscal/factura_electronica/Paginas/complemento_consumocombustibles.aspx>`_.

