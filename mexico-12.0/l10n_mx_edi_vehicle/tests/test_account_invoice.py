import base64

from lxml import objectify

from odoo.addons.l10n_mx_edi.tests.common import InvoiceTransactionCase


class TestL10nMxEdiInvoiceVehicle(InvoiceTransactionCase):

    def setUp(self):
        super(TestL10nMxEdiInvoiceVehicle, self).setUp()
        self.manager_billing.write({
            'groups_id': [(4, self.ref('fleet.fleet_group_manager'))]
        })
        self.user_billing.write({
            'groups_id': [(4, self.ref('fleet.fleet_group_manager'))]
        })

    def test_l10n_mx_edi_invoice_cd(self):
        isr_tag = self.env['account.account.tag'].search(
            [('name', '=', 'ISR')])
        self.tax_negative.tag_ids |= isr_tag
        self.company.partner_id.write({
            'property_account_position_id': self.fiscal_position.id,
        })
        vehicle_id = self.env.ref('fleet.vehicle_3')
        vehicle_id.write({
            'model_year': '2000',
            'l10n_mx_edi_niv': 'YU76YI',
            'l10n_mx_edi_motor': '567MOTORN087',
            'l10n_mx_edi_circulation_no': 'MEX6467HGTO',
            'l10n_mx_edi_landing': '15 000 435',
            'l10n_mx_edi_landing_date': '2000/06/06',
            'l10n_mx_edi_aduana': 'Aduana',
            'vin_sn': '1234567ASDF12V67W',
        })
        invoice = self.create_invoice()
        invoice.sudo().company_id.l10n_mx_edi_complement_type = 'destruction'
        invoice.write({
            'l10n_mx_edi_serie_cd': 'serie_a',
            'l10n_mx_edi_folio_cd': '123456GFD',
            'l10n_mx_edi_vehicle_id': vehicle_id.id,
        })
        invoice.action_invoice_open()
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed",
                         invoice.message_ids.mapped('body'))
        xml = invoice.l10n_mx_edi_get_xml_etree()
        namespaces = {
            'destruccion': 'http://www.sat.gob.mx/certificadodestruccion'}
        comp = xml.Complemento.xpath('//destruccion:certificadodedestruccion',
                                     namespaces=namespaces)
        self.assertTrue(comp, 'Complement to EAPA not added correctly')

    def test_l10n_mx_edi_xsd(self):
        """Verify that xsd file is downloaded"""
        self.company._load_xsd_attachments()
        xsd_file = self.ref(
            'l10n_mx_edi.xsd_cached_certificadodedestruccion_xsd')
        self.assertTrue(xsd_file, 'XSD file not load')

    def test_invoice_renew_and_substitution(self):
        isr_tag = self.env['account.account.tag'].search(
            [('name', '=', 'ISR')])
        self.tax_negative.tag_ids |= isr_tag
        self.company.partner_id.write({
            'property_account_position_id': self.fiscal_position.id,
        })
        vehicle_id = self.env.ref('fleet.vehicle_3')
        vehicle_id.write({
            'vin_sn': '1234567ASDF12V67W',
            'model_year': '2016',
        })
        substitute_vehicle_id = self.env.ref('fleet.vehicle_1')
        vehicle_type_tag = self.env['fleet.vehicle.tag'].search(
            [('name', '=', '01 - Fifth wheel tractor')])
        if not vehicle_type_tag:
            vehicle_type_tag = self.env['fleet.vehicle.tag'].create({
                'name': '01 - Fifth wheel tractor'})
        substitute_vehicle_id.tag_ids.unlink()
        substitute_vehicle_id.tag_ids = [
            self.env.ref('fleet.vehicle_3').tag_ids[0].id,
            vehicle_type_tag.id
        ]
        substitute_vehicle_id.write({
            'model_year': '2000',
            'vin_sn': '1234567ASDF12V67Y',
            'l10n_mx_edi_circulation_no': 'MEX6467HGTO',
            'l10n_mx_edi_fiscal_folio': '123-ABCDE-4567-FGHI',
            'l10n_mx_edi_int_advice': '89-JKL-09-MN',
            'l10n_mx_edi_landing': '1234567',
            'l10n_mx_edi_landing_date': '2000-01-01',
            'l10n_mx_edi_aduana': 'Aduana Prueba',
        })
        invoice = self.create_invoice()
        invoice.sudo().company_id.l10n_mx_edi_complement_type = 'renew'
        invoice.write({
            'l10n_mx_edi_decree_type': '02',
            'l10n_mx_edi_substitute_id': substitute_vehicle_id.id,
            'l10n_mx_edi_vehicle_id': vehicle_id.id,
        })
        invoice.action_invoice_open()
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed",
                         invoice.message_ids.mapped('body'))
        xml = invoice.l10n_mx_edi_get_xml_etree()
        namespaces = {
            'decreto': 'http://www.sat.gob.mx/renovacionysustitucionvehiculos'}
        comp = xml.Complemento.xpath('//decreto:renovacionysustitucionvehiculos', # noqa
                                     namespaces=namespaces)
        self.assertTrue(comp, 'Complement to Renew ans Substitution not added '
                        'correctly')

    def test_used_vehicle(self):
        isr_tag = self.env['account.account.tag'].search(
            [('name', '=', 'ISR')])
        self.tax_negative.tag_ids |= isr_tag
        self.company.partner_id.write({
            'property_account_position_id': self.fiscal_position.id,
        })
        vehicle_id = self.env.ref('fleet.vehicle_3')
        vehicle_model_brand = self.env['fleet.vehicle.model.brand'].create({
            'name': 'Nissan', })
        vehicle_model = self.env['fleet.vehicle.model'].create({
            'name': 'Aprio',
            'brand_id': vehicle_model_brand.id,
        })
        vehicle_id.write({
            'license_plate': '1BMW001',
            'model_id': vehicle_model.id,
            'residual_value': 1000.00,
            'l10n_mx_edi_motor': '1234JN90LNX',
            'l10n_mx_edi_niv': '123456789',
            'model_year': '2008',
            'odometer': 10345,
            'car_value': 131100,
            'vin_sn': '1234567ASDF12V67Y',
            'l10n_mx_edi_landing': '33227007095',
            'l10n_mx_edi_landing_date': '11/07/2007',
            'l10n_mx_edi_aduana': 'Int. del Edo. de Ags.'
        })
        invoice = self.create_invoice()
        invoice.sudo().company_id.l10n_mx_edi_complement_type = 'sale'
        invoice.write({'l10n_mx_edi_vehicle_id': vehicle_id.id})
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
            '<vehiculousado:VehiculoUsado '
            'xmlns:vehiculousado="http://www.sat.gob.mx/vehiculousado" '
            'Version="1.0" montoAdquisicion="131100.0" '
            'montoEnajenacion="477.0" claveVehicular="1BMW001" marca="Nissan" '
            'tipo="Aprio" modelo="2008" numeroMotor="1234JN90LNX" '
            'numeroSerie="1234567ASDF12V67Y" NIV="123456789" '
            'valor="1000.0"><vehiculousado:InformacionAduanera '
            'numero="33227007095" fecha="2007-11-07" '
            'aduana="Int. del Edo. de Ags."/></vehiculousado:VehiculoUsado>'
        )
        namespaces = {'vehiculousado': 'http://www.sat.gob.mx/vehiculousado'}
        comp = xml.Complemento.xpath('//vehiculousado:VehiculoUsado',
                                     namespaces=namespaces)
        self.assertEqualXML(comp[0], xml_expected)

    def test_pfic(self):
        isr_tag = self.env['account.account.tag'].search(
            [('name', '=', 'ISR')])
        self.tax_negative.tag_ids |= isr_tag
        self.company.partner_id.write({
            'property_account_position_id': self.fiscal_position.id,
        })
        vehicle_id = self.env.ref('fleet.vehicle_3')
        vehicle_id.write({'l10n_mx_edi_niv': '0101011'})
        invoice = self.create_invoice()
        invoice.sudo().company_id.l10n_mx_edi_complement_type = 'pfic'
        invoice.write({'l10n_mx_edi_vehicle_id': vehicle_id.id})
        invoice.action_invoice_open()
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed",
                         invoice.message_ids.mapped('body'))
        xml = invoice.l10n_mx_edi_get_xml_etree()
        namespaces = {'pfic': 'http://www.sat.gob.mx/pfic'}
        comp = xml.Complemento.xpath('//pfic:PFintegranteCoordinado',
                                     namespaces=namespaces)
        self.assertTrue(comp, 'Complement for PFIC not added correctly')

    def test_new_vehicle(self):
        isr_tag = self.env['account.account.tag'].search(
            [('name', '=', 'ISR')])
        self.tax_negative.tag_ids |= isr_tag
        self.company.partner_id.write({
            'property_account_position_id': self.fiscal_position.id,
        })
        vehicle_id = self.env.ref('fleet.vehicle_3')
        vehicle_model_brand = self.env['fleet.vehicle.model.brand'].create({
            'name': '01', })
        vehicle_model = self.env['fleet.vehicle.model'].create({
            'name': '1234',
            'brand_id': vehicle_model_brand.id,
        })
        vehicle_id.write({
            'license_plate': '1BMW0017',
            'model_id': vehicle_model.id,
            'l10n_mx_edi_niv': '123456789',
            'odometer': 0.0,
        })
        cost_type = self.env['fleet.service.type'].search(
            [('name', '=', 'Sale Extra')])
        if not cost_type:
            cost_type = self.env['fleet.service.type'].create({
                'name': 'Sale Extra',
                'category': 'contract',
            })
        self.env['fleet.vehicle.cost'].create({
            'vehicle_id': vehicle_id.id,
            'cost_subtype_id': cost_type.id,
            'amount': 4000.00,
            'description': '3/PZ/12345/09876/test aduana',
            'date': '03/15/2018',
        })
        invoice = self.create_invoice()
        invoice.sudo().company_id.l10n_mx_edi_complement_type = 'sale'
        invoice.write({'l10n_mx_edi_vehicle_id': vehicle_id.id})
        invoice.action_invoice_open()
        self.assertEqual(invoice.l10n_mx_edi_pac_status, "signed",
                         invoice.message_ids.mapped('body'))
        xml = invoice.l10n_mx_edi_get_xml_etree()
        namespaces = {'ventavehiculos': 'http://www.sat.gob.mx/ventavehiculos'}
        comp = xml.Complemento.xpath('//ventavehiculos:VentaVehiculos',
                                     namespaces=namespaces)
        self.assertTrue(comp, 'Concept Complement for New Vehicle not added '
                        'correctly')
