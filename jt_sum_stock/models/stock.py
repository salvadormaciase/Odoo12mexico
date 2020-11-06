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

from odoo.tools.float_utils import float_round
from odoo.addons import decimal_precision as dp
from odoo.tools.float_utils import float_round

from odoo import models, api, fields


class StockLocation(models.Model):
    _inherit = "stock.location"

    location_to_add = fields.Boolean('¿Ubicación a sumar?')


class Product(models.Model):
    _inherit = "product.product"

    @api.depends('min_qty', 'max_qty', 'qty_transito')
    def _compute_recovery(self):
        for product in self:
            stock = product.qty_transito
            min = product.min_qty
            max = product.max_qty
            if stock >= min:
                product.recovery = 0
            else:
                product.recovery = max - stock

    sum_of_stock = fields.Float(
        'Suma de ubicaciones', compute='_compute_quantities', search='_search_qty_available')
    recovery = fields.Float("Recuperación", compute='_compute_recovery', store=True)

    @api.depends('stock_move_ids.product_qty', 'stock_move_ids.state')
    def _compute_quantities(self):
        res = self._compute_quantities_dict(self._context.get('lot_id'), self._context.get('owner_id'),
                                            self._context.get('package_id'), self._context.get('from_date'),
                                            self._context.get('to_date'))
        for product in self:
            product.qty_available = res[product.id]['qty_available']
            product.incoming_qty = res[product.id]['incoming_qty']
            product.outgoing_qty = res[product.id]['outgoing_qty']
            product.virtual_available = res[product.id]['virtual_available']
            product.sum_of_stock = res[product.id]['sum_of_stock']

    def _compute_quantities_dict(self, lot_id, owner_id, package_id, from_date=False, to_date=False):
        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = self._get_domain_locations()
        domain_quant = [('product_id', 'in', self.ids)] + domain_quant_loc
        sum_stock_domain_quant = domain_quant + [('location_id.location_to_add', '=', True)]
        dates_in_the_past = False
        # only to_date as to_date will correspond to qty_available
        to_date = fields.Datetime.to_datetime(to_date)
        if to_date and to_date < fields.Datetime.now():
            dates_in_the_past = True

        domain_move_in = [('product_id', 'in', self.ids)] + domain_move_in_loc
        domain_move_out = [('product_id', 'in', self.ids)] + domain_move_out_loc
        if lot_id is not None:
            domain_quant += [('lot_id', '=', lot_id)]
            sum_stock_domain_quant += [('lot_id', '=', lot_id)]
        if owner_id is not None:
            domain_quant += [('owner_id', '=', owner_id)]
            sum_stock_domain_quant += [('owner_id', '=', owner_id)]
            domain_move_in += [('restrict_partner_id', '=', owner_id)]
            domain_move_out += [('restrict_partner_id', '=', owner_id)]
        if package_id is not None:
            domain_quant += [('package_id', '=', package_id)]
            sum_stock_domain_quant += [('package_id', '=', package_id)]
        if dates_in_the_past:
            domain_move_in_done = list(domain_move_in)
            domain_move_out_done = list(domain_move_out)
        if from_date:
            domain_move_in += [('date', '>=', from_date)]
            domain_move_out += [('date', '>=', from_date)]
        if to_date:
            domain_move_in += [('date', '<=', to_date)]
            domain_move_out += [('date', '<=', to_date)]

        Move = self.env['stock.move']
        Quant = self.env['stock.quant']
        domain_move_in_todo = [('state', 'in',
                                ('waiting', 'confirmed', 'assigned', 'partially_available'))] + domain_move_in
        domain_move_out_todo = [('state', 'in',
                                 ('waiting', 'confirmed', 'assigned', 'partially_available'))] + domain_move_out
        moves_in_res = dict((item['product_id'][0], item['product_qty']) for item in
                            Move.read_group(domain_move_in_todo, ['product_id', 'product_qty'], ['product_id'],
                                            orderby='id'))
        moves_out_res = dict((item['product_id'][0], item['product_qty']) for item in
                             Move.read_group(domain_move_out_todo, ['product_id', 'product_qty'], ['product_id'],
                                             orderby='id'))
        quants_res = dict((item['product_id'][0], item['quantity']) for item in
                          Quant.read_group(domain_quant, ['product_id', 'quantity'], ['product_id'], orderby='id'))
        quant_res_sum_stock = dict((item['product_id'][0], item['quantity']) for item in
                          Quant.read_group(sum_stock_domain_quant, ['product_id', 'quantity'], ['product_id'], orderby='id'))
        if dates_in_the_past:
            # Calculate the moves that were done before now to calculate back in time (as most questions will be recent ones)
            domain_move_in_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_in_done
            domain_move_out_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_out_done
            moves_in_res_past = dict((item['product_id'][0], item['product_qty']) for item in
                                     Move.read_group(domain_move_in_done, ['product_id', 'product_qty'], ['product_id'],
                                                     orderby='id'))
            moves_out_res_past = dict((item['product_id'][0], item['product_qty']) for item in
                                      Move.read_group(domain_move_out_done, ['product_id', 'product_qty'],
                                                      ['product_id'], orderby='id'))

        res = dict()
        for product in self.with_context(prefetch_fields=False):
            product_id = product.id
            rounding = product.uom_id.rounding
            res[product_id] = {}
            if dates_in_the_past:
                qty_available = quants_res.get(product_id, 0.0) - moves_in_res_past.get(product_id,
                                                                                        0.0) + moves_out_res_past.get(
                    product_id, 0.0)
                sum_stock = quant_res_sum_stock.get(product_id, 0.0) - moves_in_res_past.get(product_id,
                                                                                        0.0) + moves_out_res_past.get(
                    product_id, 0.0)
            else:
                qty_available = quants_res.get(product_id, 0.0)
                sum_stock = quant_res_sum_stock.get(product_id, 0.0)
            res[product_id]['qty_available'] = float_round(qty_available, precision_rounding=rounding)
            res[product_id]['sum_of_stock'] = float_round(sum_stock, precision_rounding=rounding)
            res[product_id]['incoming_qty'] = float_round(moves_in_res.get(product_id, 0.0),
                                                          precision_rounding=rounding)
            res[product_id]['outgoing_qty'] = float_round(moves_out_res.get(product_id, 0.0),
                                                          precision_rounding=rounding)
            res[product_id]['virtual_available'] = float_round(
                qty_available + res[product_id]['incoming_qty'] - res[product_id]['outgoing_qty'],
                precision_rounding=rounding)
        return res


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.depends(
        'product_variant_ids',
        'product_variant_ids.stock_move_ids.product_qty',
        'product_variant_ids.stock_move_ids.state',
    )
    def _compute_quantities(self):
        res = self._compute_quantities_dict()
        for template in self:
            template.qty_available = res[template.id]['qty_available']
            template.virtual_available = res[template.id]['virtual_available']
            template.incoming_qty = res[template.id]['incoming_qty']
            template.outgoing_qty = res[template.id]['outgoing_qty']
            template.sum_of_stock = res[template.id]['sum_of_stock']

    def _compute_quantities_dict(self):
        # TDE FIXME: why not using directly the function fields ?
        variants_available = self.mapped('product_variant_ids')._product_available()
        prod_available = {}
        for template in self:
            qty_available = 0
            virtual_available = 0
            incoming_qty = 0
            outgoing_qty = 0
            sum_of_stock = 0
            for p in template.product_variant_ids:
                qty_available += variants_available[p.id]["qty_available"]
                sum_of_stock += variants_available[p.id]["sum_of_stock"]
                virtual_available += variants_available[p.id]["virtual_available"]
                incoming_qty += variants_available[p.id]["incoming_qty"]
                outgoing_qty += variants_available[p.id]["outgoing_qty"]
            prod_available[template.id] = {
                "qty_available": qty_available,
                "virtual_available": virtual_available,
                "incoming_qty": incoming_qty,
                "outgoing_qty": outgoing_qty,
                "sum_of_stock": sum_of_stock,
            }
        return prod_available

    @api.depends('sum_of_stock', 'transito')
    @api.multi
    def _compute_qty_transito(self):
        for template in self:
            template.qty_transito = template.sum_of_stock + template.transito

    @api.depends('product_variant_ids.recovery')
    @api.multi
    def _compute_recovery(self):
        for template in self:
            template.recovery = float_round(
                sum([p.recovery for p in template.product_variant_ids]),
                precision_rounding=template.uom_id.rounding)

    sum_of_stock = fields.Float(
        'Suma de ubicaciones', compute='_compute_quantities', search='_search_qty_available',
        digits=dp.get_precision('Product Unit of Measure'))
    transito = fields.Float(string='Tránsito', related='product_variant_id.incoming_qty', store=True)
    qty_transito = fields.Float(string="Qty + Tránsito", compute="_compute_qty_transito", store=True)
    recovery = fields.Float("Recuperación", compute='_compute_recovery', store=True)
    min_qty = fields.Float("Min")
    max_qty = fields.Float("Max")