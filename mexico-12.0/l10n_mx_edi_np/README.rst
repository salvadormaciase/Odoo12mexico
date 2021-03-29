This module manage the Notary Public complement.

Management of the sale of real estate or rights of way with compensation or
consideration in a single exhibition.

At the Invoice you have to fill the following fields:

- *Buyer*: is the buyer or buyers who are going to buy the property (or properties).


The **Buyer** can be a person, or a co-ownership or conjugal partnership. To indicate
a co-ownership or conjugal partnership a tag with the same name should be set at
the partner Tags field. When the buyer is a co-ownership or conjugal partnership
some contacts should be added at Partner's Contacts & Address with type 'Contact.
This contacts are going to represent the property buyers.

Also, the buyer needs the following information:

- *Nombre*: it is the buyer name.
- *ApellidoPaterno*: it is an optional field which represents the Father's name
  of the buyer. If you want to set this split the name and last name with a comma (,).
- *ApellidoMaterno*: it is an optional fiel which represent the Mother's name
  of the buyer. If you want to set this split the name and last name with a comma (,).
- *RFC*: Key of the Federal Register of Taxpayers, it is the Partner's VAT field.
- *CURP*: it is the Partner's CURP field.
- *Porcentaje*: this is the percentage that corresponds to each acquirer and it
  is needed when there is multiple buyers like a co-ownership or conjugal 
  partnership. You can set this in the comment field.

The following is an example of a multiple buyers, it means it has the co-ownership /
conjugal partnership tag associated:

.. image:: l10n_mx_edi_np/static/src/multi_buyer_example.png
   :align: center
   :width: 550pt

As the buyer the **Client** can be a person, or a co-ownership or conjugal
partnership. The settings and information is the same as the buyer.

The following is an example of a multiple salers, it means it has the co-ownership /
conjugal partnership tag associated, and it has a property assigned:

.. image:: l10n_mx_edi_np/static/src/multi_saler_example.png
   :align: center
   :width: 550pt

The **Property** or Properties that are going to be sell have to be set in the
Client as a Contact with type 'Other Address' and must have the following
information:

- *TipoInmueble*: it is the code of the property acording to SAT catalog. And you
  just have to put only the type code in the Property's Internal Note like: 02
  The Property type code can be:

  - 01: if it is a Land
  - 02: if it is a Commercial land
  - 03: if it is a housing construction
  - 04: if it is a construction of commercial use
  - 05: if it is mixed use

- *Calle*: the street where the property is located, it is the Partner's Address field.
- *NoExterior*: this is an optional field to locate the property precisely, it is the
  Partner's House Number field.
- *NoInterior*: this is an optional field to locate the property when 'NoExterior'
  is not enough, it is the Partner's Door Number field.
- *Colonia*: this is an optional field to set the colony where the property is
  located, is the Partner's Colony field.
- *Localidad*: this is an optional field to indicate the village or town where 
  the property is located, it is the Partner's Locality field.
- *Refencia*: this is an optional field to add more information about the property
  location, You can add this in the Partner's Internal Notes. Because the Internal
  Notes is also used for the property type code you can split the content like this:
  property type code|reference text (02|next to the shoping center)
- *Municipio*: it is the city where the property is located, and it is the Partener's
  City field.
- *Estado*: it is the state where the property is located, and it is the Partner's
  State field.
- *Pais*: it is the country where the porperty is located, it is the Partner's
  Country field.
- *CodigoPostal*: it is the property zip code, it is the Partner's Zip field.
- *Subtotal*: it is the amount without tax, you should set each prorperty cost in the
  Property's Internal Refenrence field.
- *IVA*: it is the tax, expressed like: 16 for 16%, or 20 for 20%. As the subtotal,
  you have to set this in the Property's Internal Reference field, with the format:
  Subtotal|IVA (ex.: 156000|10)

The following is an example of a property:

.. image:: l10n_mx_edi_np/static/src/property_example.png
   :align: center
   :width: 550pt

This complement also need information about the **operation** that is being
carried out. For this you have to set the following information:

- *InstrumentoNotarial*: it is the the document number that identify the operation,
  you can set this at the Invoice's Reference/Description field.
- *FechaInsNotarial*: it is the invoice date.
- *MontoOperacion*: it is the operation total amount with tax (You don't have to set this).

And information about the **notary public**, which is set using the Invoice's Salesperson
field. The following information should be set:

- *CUPR*: the notary public's CURP number, this have to be set at partner model.
- *NumNotaria*: this is the notary number, and have to be indicated using the
  Company's Company Registry field, this have to be set in the company model.
- *EntidadFederativa*: this is the state where the company is located.
- *Adscripcion*: it is an optional field to indicate the notification of the
  notary to the place to which he is attached. This have to be set in the Partner's
  Internal Notes, refering the notary public.

For more information in the `SAT page for Notary Public Complement <http://www.sat.gob.mx/informacion_fiscal/factura_electronica/Paginas/complemento_notarios.aspx>`_.
