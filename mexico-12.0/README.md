|**Runbot:**|**CI:**|**Coverage:**|
|-----------|-------|-------------|
|[![Runbot Status](http://runbot.vauxoo.com/runbot/badge/56/12.0.svg)](http://runbot.vauxoo.com/runbot/repo/git-github-com-vauxoo-mexico-git-56)|[![Build Status](https://git.vauxoo.com/vauxoo/mexico/badges/12.0/pipeline.svg)](https://git.vauxoo.com/vauxoo/mexico/commits/12.0)|[![Coverage Status](https://git.vauxoo.com/vauxoo/mexico/badges/12.0/coverage.svg)](https://coverage.vauxoo.com/12.0-mexico)|

Odoo Mexico Localization (Enterprise).
---

This project is to manage the modules not merged yet for odoo/enterprise > 11.0.

# Why a Clean Repository?.

A clean repository is better to add just features that works with Enterprise 
due to the change of licence it must have and due to the refactor we must do 
is several features, in order to propose a cleanest solution for 2016 for our 
biggest customers.

# What will be here as feature?.

Modules preparing their existance for future enterprise.

1. Modules that manage main features of localization on customer side.
3. Modules which add an specific values just if they are related with odoo's 
   enterprise features.

# What is the conceptual structure of work on this repository.

On the diagram bellow we will have main modules, and the objective of this is 
to understand how we expect manage less modules doing more in order to 
introduce global set of features instead complex configuration environments.

Every module which introduce a new improvement of an Odoo App will try to be 
managed in only one module in order to ensure the app itself can work with 
minimal configuration and minimal external dependencies.

# Licencing of new modules.

All modules will be LGPL-v3 + Vauxoo Exceptions, odoo-lint scripts should manage such revision in order to ensure not include incorrect licencing here.

# Installation.

Every single module must be installable ad testeable by itself (or depend on 
modules here or official ones), if there will be an exception to such rule the
explanation of the exception must be done in the README of the module itself.

We need to try to follow [this methodology of design](https://gettingreal.37signals.com/ch06_Avoid_Preferences.php) 
proposed by Fabien, avoiding too much preferences, the objective is that all default 
values should be setted as Data/Data documenting such decisions in the data itself.

# List of features considered.

This titles are only to be considered "Epic Stories", obviously they need huge 
revision in our expert side and in customer side.

For every one of this features we should link them with a tag in an issue and 
marked as "Enhancement".

## Functionalities:

Here is a list of functionalities necesaries to improve Odoo's workflow.

1. **Actual taxes:** All the set of taxes necesaries to work in México, the 
   migration script should be capable of map a set of taxes in a real 
   environment to the created ones.
2. **Invoice Workflow (this include the electronic invoice):** All 
   configurations necesaries to work with invoicing in México, the electronic 
   invoicing is considered a core feature, then everythign we do on this term 
   is considering this must be electronically signed, 1 transaction 1 invoice 
   (B2B), Several transactions 1 Electronic Signature (B2C), everything thought 
   in terms of Suppliers and Customer invoices.
3. **Payment Workflow & Bank Management (Accounting).**: Here we need to 
   considere all improvements around IVA efectivamente pagado.
4. **Supplier Management (DIOT).**
5. **Customer Management (Fiscal Information).**
6. **Accounting**: All the information related to Accounts and Transactions 
   necessary to deliver correct reports following the 
   [electronic format compliance for México](http://www.sat.gob.mx/fichas_tematicas/buzon_tributario/Paginas/contabilidad_electronica.aspx).

## Reports:

All reports must depend on enterprise engine.

1. Accounting reports (P&L, etc). use
   [this](https://github.com/Vauxoo/enterprise/tree/master/l10n_be_reports) 
   technique or way of design.
2. Electronic reports, once the reports above are done, then those human
   readable reports should be able to export electronically.

## Conceptual diagram.

![](http://screenshots.vauxoo.com/oem/Flujo Firma.png)
