from odoo.addons.l10n_mx_edi.tests.common import InvoiceTransactionCase
from odoo.tests import tagged


@tagged('download_zipped_cfdi')
class TestDownloadZippedCFDI(InvoiceTransactionCase):

    def setUp(self):
        super(TestDownloadZippedCFDI, self).setUp()
        self.fiscal_position.l10n_mx_edi_code = '601'
        self.product.l10n_mx_edi_code_sat_id = self.ref(
            'l10n_mx_edi.prod_code_sat_01010101')
        self.isr_tag = self.env['account.account.tag'].search(
            [('name', '=', 'ISR')])
        self.tax_negative.tag_ids |= self.isr_tag
        self.tax_negative.l10n_mx_cfdi_tax_type = 'Tasa'
        self.tax_positive.l10n_mx_cfdi_tax_type = 'Tasa'
        self.company.partner_id.write({
            'vat': 'EKU9003173C9',
            'property_account_position_id': self.fiscal_position.id,
        })

    def test_01_download_zipped_invoice(self):
        """Test case: a user clicks the DOWNLOAD ZIP button located at my/invoices, the result is the authomatic
        download of a folder containing the pdf and xml of the current invoice"""
        invoice = self.create_invoice()
        invoice.action_invoice_open()
        url = "/my/invoices/%s" % invoice.id
        tour = 'check_download_zipped_cfdi'
        self.phantom_js(
            url_path=url,
            code="odoo.__DEBUG__.services['web_tour.tour'].run('%s')" % tour,
            ready="odoo.__DEBUG__.services['web_tour.tour'].tours.%s.ready" % tour,
            login="admin")
