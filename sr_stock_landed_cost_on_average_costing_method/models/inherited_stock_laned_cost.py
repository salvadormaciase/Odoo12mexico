# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2017-Today Sitaram
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from odoo import api, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero

class srInheritedLandedCost(models.Model):
    _inherit = 'stock.landed.cost'


    def get_valuation_lines(self):
        lines = []

        for move in self.mapped('picking_ids').mapped('move_lines'):
            # it doesn't make sense to make a landed cost for a product that isn't set as being valuated in real time at real cost
            if move.product_id.valuation != 'real_time' or move.product_id.cost_method not in ['fifo','average']:
                continue
            vals = {
                'product_id': move.product_id.id,
                'move_id': move.id,
                'quantity': move.product_qty,
                'former_cost': move.value,
                'weight': move.product_id.weight * move.product_qty,
                'volume': move.product_id.volume * move.product_qty
            }
            lines.append(vals)

        if not lines and self.mapped('picking_ids'):
            raise UserError(_("You cannot apply landed costs on the chosen transfer(s). Landed costs can only be applied for products with automated inventory valuation and FIFO Or Average costing method."))
        return lines

    @api.multi
    def button_validate(self):
        result = super(srInheritedLandedCost, self).button_validate()
        for line in self.valuation_adjustment_lines:
            if not line.move_id:
                continue
            if line.move_id.picking_id.picking_type_id.code == 'incoming' :
                formar_cost = 0
                if line.quantity > 0 :
                    formar_cost += line.additional_landed_cost
                if line.product_id.cost_method == 'average'  and not float_is_zero(line.product_id.qty_available, precision_rounding=line.product_id.uom_id.rounding):
                    line.product_id.with_context(force_company=self.company_id.id).sudo().standard_price += formar_cost/line.product_id.qty_available
        return result