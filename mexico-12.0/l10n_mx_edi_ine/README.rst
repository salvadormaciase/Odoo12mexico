CFDI complement for Mexico National Electoral Institute (INE)
=============================================================

This supplement must be used by individuals or corporations that provide some 
good or provide some service to Political Parties and Civil Associations that 
are related to people who are independent candidates and candidates.

This complement add some fields in Invoice:

- **Process Type**
  The type of process, it can be: ordinary, pre-campaign or campaign.

- **Committe Type**
  The type of committe, it can be: national executive, state executive, state manager.

- **Accounting**
  The key of accounting of aspiring precandidates, candidates and concentrators.

- **Entity Code**
  The key of the entity to which the expense is applied.

- **Scope**
  Type of scope of a campaign or pre-campaign process type.


Some considerations to keep in mind:

- If **Process Type** is 'Ordinary'
  A Committee Type should be selected

- If **Process Type** is 'Campaign' or 'Pre-campaign'
  Committee Type and Accounting fields are not necessary, but it should exists at 
  least one Entity and Scope.

- If **Committee Type** is 'National Executive'
  The Accounting field should be fill, and there is no need for an Entity.

- If **Committee Type** is 'State Executive'
  The Accounting field is not needed. It should exist at least one Entity but without
  Scope.

- if **Committee Type** is 'State Manager'
  The Accounting field can be fill and it should exist at least one Entity but without
  Scope.

- **Accounting** field with Entity and Scope
  This field can be used when Process Type is 'Ordinary' and Committee Type is
  'State Executive', or when Process Type is 'Campaign' or 'Pre-campaign'.

** Important note **
   In the case an invoice is validated and some fields were missed and the sign
   process does not complete but the xml is generated, the invoice should be 
   cancel and reset to draft so the fields can be update and the invoice can be
   validated.
