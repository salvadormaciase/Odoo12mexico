# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Jupical Technologies(<http://www.jupical.com>).
#    Author: Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, api


class StockPicking(models.Model):

    _inherit = "stock.picking"

    def button_validate(self):
        self.ensure_one()
        res = super(StockPicking, self).button_validate()
        for picking in self:
            quants_to_delete = self.env['stock.quant'].sudo().search([('picking_id', '=', picking.id), ('flag_import_quant', '=', True)]).unlink()
        return res

    # Function to open import screen
    @api.multi
    def action_assign_serial(self):
        self.ensure_one()

        # Check availability of quantity to create lines
        if self.show_check_availability:
            self.action_assign()

        # Set picking reference to context as a flag
        context = self._context.copy()
        context['picking_id'] = self.id

        # Action to open import wizard dashboard
        return {
            'type': 'ir.actions.client',
            'tag': 'import',
            'params': {
                'model': 'stock.production.lot',
                'context': context,
            }
        }
