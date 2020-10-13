# Copyright 2016 Vauxoo Oscar Alcala <oscar@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo.addons.portal.controllers.portal import CustomerPortal as CP
from odoo.addons.website_sale.controllers.main import WebsiteSale as WS


class CustomerPortal(CP):

    def __init__(self, **args):
        self.MANDATORY_BILLING_FIELDS.extend((
            'street_name',
            'street_number'))
        self.OPTIONAL_BILLING_FIELDS.extend((
            'street_number2',
            'l10n_mx_edi_locality',
            'l10n_mx_edi_colony',
        ))
        if 'street' in self.MANDATORY_BILLING_FIELDS:
            self.MANDATORY_BILLING_FIELDS.remove('street')
        super(CustomerPortal, self).__init__(**args)


class WebsiteSale(WS):

    def _get_mandatory_billing_fields(self):
        flds = super(WebsiteSale, self)._get_mandatory_billing_fields()
        flds.extend(('street_number', 'street_name'))
        if 'street' in flds:
            flds.remove('street')
        return flds

    def _get_mandatory_shipping_fields(self):
        flds = super(WebsiteSale, self)._get_mandatory_shipping_fields()
        flds.extend(('street_number', 'street_name'))
        if 'street' in flds:
            flds.remove('street')
        return flds
