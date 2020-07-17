# -*- coding: utf-8 -*-

import base64
import re
import logging
import requests
from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class ResPartnerBlacklist(models.Model):
    _name = 'res.partner.blacklist'
    _description = 'Partner Blacklist'

    number = fields.Char()
    vat = fields.Char(index=True, required=True)
    taxpayer_name = fields.Char(required=True)
    taxpayer_status = fields.Char(
        help="Taxpayer Status, if the status is set it means the taxpayer "
        "status is 'Definitivo' and this partner is not in a legal situation",
    )
    global_presumption = fields.Char(
        string="Presumption trade number and date",
    )
    sat_presumption = fields.Char(
        string="Presumption trade number and date from SAT",
    )
    sat_presumption_release = fields.Char(
        string="SAT date presumptions publication",
        help="This is the date when the SAT published in its website the "
        "presumed",
    )
    dof_presumption = fields.Char(
        string="Presumption trade number and date from DOF",
    )
    global_definitive = fields.Char(
        string="Definitive trade number and date",
    )
    sat_definitive_release = fields.Char(
        string="SAT date definitive publication",
        help="This is the date when the SAT published in its website the "
        "definitive",
    )
    dof_definitive_release = fields.Char(
        string="DOF date definitive publication",
        help="This is the date when the DOF published in its website the "
        "definitive",
    )

    def download_csv_partner_list(self):
        url = self.env['ir.config_parameter'].sudo().get_param(
            'l10n_mx_partner_blocklist_url')
        _logger.info(_("Partner blocklist URL: " + url if url else "None URL"))
        if not url:
            return False
        file_content = b''
        file_name = 'l10n_mx_partner_blocklist_res_partner_blacklist.csv'
        self.env['ir.attachment'].search([('name', '=', file_name)]).unlink()
        try:
            list_file = requests.get(url)
            for count, line in enumerate(list_file.iter_lines()):
                if line[line.index(b','):] not in file_content and \
                        count not in [0, 1] and line != b'':
                    line = line.decode(
                        'utf-8', errors="ignore").replace('""', '')
                    sub_line = re.search('"[A-Za-z0-9 .,&-/_]+', line)
                    if sub_line and count > 2:
                        line = line.replace(
                            sub_line.group(0),
                            sub_line.group(0).replace(',', ' '))
                    # copy only the cols that are not empty
                    cols = line.split(",")
                    line = (",").join(
                        ((",").join(cols[0:8]), (",").join(cols[11:14])))
                    file_content += line.encode() + b'\r\n'
        except Exception as e:
            _logger.info(_("Unexpected: " + str(e)))

        attachment_id = self.env['ir.attachment'].create({
            'name': file_name,
            'datas_fname': file_name,
            'datas': base64.encodestring(file_content),
            'type': 'binary',
            'mimetype': 'text/csv',
            'description': 'Partner Blocklist CSV'
        })
        self.definitive_partner_list(attachment_id)
        return True

    @api.multi
    def definitive_partner_list(self, attachment_id):
        """Download CSV data from SAT and update data in Odoo database"""
        if not attachment_id:
            _logger.info(_("Please check the blocklist attachment exists."))
            return False
        cr = self.env.cr
        cr.execute("DELETE FROM res_partner_blacklist;")
        cr.execute("DELETE FROM ir_model_data WHERE "
                   "model='l10n_mx_partner_blocklist.res.partner.blacklist';")
        csv_path = attachment_id._full_path(attachment_id.store_fname)
        csv_file = open(csv_path, 'rb')
        cr.copy_expert(
            """COPY res_partner_blacklist(
            number, vat, taxpayer_name, taxpayer_status, global_presumption,
            sat_presumption, sat_presumption_release, dof_presumption,
            global_definitive, sat_definitive_release, dof_definitive_release)
            FROM STDIN WITH DELIMITER ','""", csv_file)
        # Create xml_id, to allow make reference to this data
        # Avoid save duplicated data
        try:
            cr.execute(
                """INSERT INTO ir_model_data
                (name, res_id, module, model, noupdate)
                SELECT concat('partner_code', vat), id,
                'l10n_mx_partner_blocklist',
                'l10n_mx_partner_blocklist.res.partner.blacklist', true
                FROM res_partner_blacklist
                ON CONFLICT (module, name) DO NOTHING""")
        except Exception as e:
            _logger.info(_("Unexpected: " + str(e)))
