import base64

from lxml import objectify

from odoo.addons.l10n_mx_edi.tests.common import InvoiceTransactionCase


class TestL10nMxEdiInvoiceTPE(InvoiceTransactionCase):

    def test_l10n_mx_edi_invoice_tpe(self):
        self.env['base.language.install'].create(
            {'lang': 'es_MX', 'overwrite': 0}).lang_install()
        isr_tag = self.env['account.account.tag'].search(
            [('name', '=', 'ISR')])
        self.tax_negative.tag_ids |= isr_tag
        self.company.partner_id.write({
            'property_account_position_id': self.fiscal_position.id,
        })
        self.product.sudo().write({
            'l10n_mx_edi_tpe_track': 'seaway'
        })
        invoice = self.create_invoice()
        invoice.partner_id.sudo().write({
            'country_id': self.ref('base.aw'),
            'ref': 'passport|EGA93812273-PLM3821'
        })
        invoice.l10n_mx_edi_tpe_transit_date = '2018-05-12'
        invoice.l10n_mx_edi_tpe_transit_time = 5.16666666666667
        invoice.l10n_mx_edi_tpe_transit_type = 'departure'
        invoice.name = 'MX8321/GC9328'
        invoice.l10n_mx_edi_tpe_partner_id = self.ref('base.res_partner_3')
        invoice.message_ids.unlink()
        invoice.action_invoice_open()
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed",
                         invoice.message_ids.mapped('body'))
        attach = self.env['ir.attachment'].search(
            [('res_model', '=', 'account.invoice'),
             ('res_id', '=', invoice.id)], limit=1)
        xml_str = base64.b64decode(attach.datas)
        xml = objectify.fromstring(xml_str)
        xml_expected = objectify.fromstring(
            '<tpe:TuristaPasajeroExtranjero '
            'xmlns:tpe="http://www.sat.gob.mx/TuristaPasajeroExtranjero" '
            'version="1.0" fechadeTransito="2018-05-12T05:10:00" '
            'tipoTransito="Salida"><tpe:datosTransito Via="Marítima" '
            'TipoId="passport" NumeroId="EGA93812273-PLM3821" '
            'Nacionalidad="Aruba" EmpresaTransporte="Gemini Furniture" '
            'IdTransporte="MX8321/GC9328"/></tpe:TuristaPasajeroExtranjero>')
        namespace = {'tpe': 'http://www.sat.gob.mx/TuristaPasajeroExtranjero'}
        xml_tpe = xml.Complemento.xpath('//tpe:TuristaPasajeroExtranjero',
                                        namespaces=namespace)
        self.assertEqualXML(xml_tpe[0], xml_expected)
