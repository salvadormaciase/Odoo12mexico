from odoo import _, api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _l10n_mx_edi_prepare_refund_sale_coupon(self, invoice_ids):
        """Avoid Odoo feature for this method"""
        return []


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _prepare_invoice_line(self, qty):
        """Coupons for the order are considered.
        The price unit in te coupon line is updated to 0, and the discount is
        applied in the other lines."""
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty=qty)
        order = self.order_id
        program = order.applied_coupon_ids.program_id or order.no_code_promo_program_ids or order.code_promo_program_id
        if self.is_reward_line and program.discount_apply_on == 'on_order':
            res.update({
                'name': _('%s\nTotal Discount:%s\nCoupon:%s') % (
                    res.get('name'),
                    res.get('price_unit', 0),
                    order.applied_coupon_ids.display_name),
                'price_unit': 0,
            })
        if not self.is_reward_line and program.discount_apply_on == 'on_order':
            reward = order.order_line.filtered('is_reward_line')
            total = sum((order.order_line - reward).mapped('price_total'))
            factor = abs(reward.price_total) / total if total else 1
            res.update({
                'l10n_mx_edi_amount_discount': factor * self.price_unit,
            })
        return res
