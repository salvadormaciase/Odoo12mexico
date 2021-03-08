# Copyright 2018 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import base64
from codecs import BOM_UTF8
from lxml import objectify
from odoo import models, api

BOM_UTF8U = BOM_UTF8.decode('UTF-8')


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    def parse_xml(self, xml_file):
        """Simple wrapper to the wizard that runs the whole process of the
        importation of documents on the backend, some extra steps are done
        here:
        - Creation of custom filename: rfc-emisor_folio_serie_AnoMesDia
        - Validate if the CFDI is v 3.3

        :param xml_file (string): The filestorage itself.
        :return filename: The new filename which will be used to store the
        attachment.
        :rtype string:
        :return (dict): A dictionary with the following attributes
            - key.- If all is OK return True, else False
            - xml64.- The same CFDI in base64
            - where.- The file on which the process was executed
            - error.- If it's found, return the message
            - invoice_id.- The newly created invoice
        :rtype dict:
        """

        # Instancing the wizard that will import the xml file
        wiz = self.env['attach.xmls.wizard'].sudo()
        xml_string = xml_file.read()
        data = base64.b64encode(xml_string)
        res = wiz.check_xml({xml_file.filename: data})
        xml = objectify.fromstring(xml_string)

        # early return if errors found
        if not res.get(xml_file.filename, True):
            return res, xml_file.filename

        # Extract data from xml file
        doc_number = xml.get('Folio', False)
        serial = xml.get('Serie', False)
        date = xml.get('Fecha', False)
        supplier_vat = xml.Emisor.get('Rfc', False)

        # create base filename
        filename = '%s_%s_%s_%s' % (
            supplier_vat, doc_number, serial, date[:10])

        return res, filename
