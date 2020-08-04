# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from os import listdir
from os.path import join

from odoo import fields, models
from odoo.modules import get_module_path
from odoo.tools.convert import convert_file


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    l10n_mx_addenda = fields.Selection([
        ('amazon', 'Amazon'),
        ('airbus', 'Airbus'),
        ('chrysler', 'Chrysler'),
        ('ford', 'Ford'),
        ('porcelanite', 'Porcelanite'),
        ('bosh', 'Bosh'),
        ('nissan', 'Nissan'),
        ('femsa', 'Femsa'),
        ('fresko', 'Comercial City Fresko'),
        ('mabe', 'Mabe'),
        ('calsonic_kansei', 'Calsonic Kansei'),
        ('ahmsa', 'AHMSA'),
        ('faurecia', 'Faurecia'),
        ('pepsico', 'PepsiCo'),
        ('aam', 'AAM'),
        ('agnico', 'Agnico'),
        ('edumex', 'Edumex'),
        ('encinas', 'Encinas'),
        ('envases', 'Envases'),
        ('flextronics', 'Flextronics'),
        ('nestle', 'Nestle'),
        ('sanmina', 'Sanmina'),
        ('sidel', 'Sidel'),
        ('vallen', 'Vallen'),
        ('zfmexico', 'ZF Mexico'),
        ('yanfeng', 'Yanfeng'),
        ('sams', 'SAMS'),
    ], default='')

    def install_addenda(self):
        """Helper to load addendas.

        Look for inside files data/*.xml inside with the name on the
        selection field, then import such xml as addenda view in order to have
        them as data inside odoo itself

        return view_id"""
        self.ensure_one()
        addenda = self.l10n_mx_addenda
        if not addenda:
            return {}
        addendas = join(get_module_path('l10n_mx_edi_addendas'), 'data')
        availables = listdir(addendas)
        addenda_fname = '.'.join([addenda, 'xml'])
        if addenda_fname not in availables:
            return
        pathname = join(addendas, addenda_fname)
        convert_file(
            self._cr, 'l10n_mx_edi_addendas', pathname, {},
            pathname=pathname
        )

    def open_installed_addendas(self):
        return {}
