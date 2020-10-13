
from odoo.tests.common import TransactionCase

from ..controllers.main import CustomerPortal, WebsiteSale


class TestWebsiteSale(TransactionCase):
    def test_required_and_optional_fields(self):
        portal = CustomerPortal()
        website_sale = WebsiteSale()
        # Customer Portal's mandatory fields
        self.assertIn('street_name', portal.MANDATORY_BILLING_FIELDS)
        self.assertIn('street_number', portal.MANDATORY_BILLING_FIELDS)
        self.assertNotIn('street', portal.MANDATORY_BILLING_FIELDS)
        # Customer Portal's mandatory fields
        self.assertIn('street_number2', portal.OPTIONAL_BILLING_FIELDS)
        self.assertIn('l10n_mx_edi_locality', portal.OPTIONAL_BILLING_FIELDS)
        self.assertIn('l10n_mx_edi_colony', portal.OPTIONAL_BILLING_FIELDS)
        # Website Sale's billing fields
        billing_fields = website_sale._get_mandatory_billing_fields()
        self.assertIn('street_number', billing_fields)
        self.assertIn('street_name', billing_fields)
        self.assertNotIn('street', billing_fields)
        # Website Sale's shipping fields
        shipping_fields = website_sale._get_mandatory_shipping_fields()
        self.assertIn('street_number', shipping_fields)
        self.assertIn('street_name', shipping_fields)
        self.assertNotIn('street', shipping_fields)

        # They shouldn't faild when invoqued a second time, e.g. by trying
        # to delete already deleted fields
        portal = CustomerPortal()
        website_sale = WebsiteSale()
