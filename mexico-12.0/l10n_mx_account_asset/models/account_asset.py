# Copyright 2019 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare


class AccountAssetCategory(models.Model):
    _inherit = 'account.asset.category'

    account_cogs_id = fields.Many2one(
        'account.account', string='COGS Account',
        domain=[('internal_type', '=', 'other'), ('deprecated', '=', False)],
        help="Account used to record sale of the asset.")


class AccountAssetDepreciationLine(models.Model):
    _inherit = 'account.asset.depreciation.line'

    def _prepare_sale_move(self, line):
        """This method creates an account move that has the following lines:
           - Line with the cogs account of the asset, whose amount is the
           residual value of the asset.
           - Line with the accumulated depreciation account, whose amount is
           the difference between gross value and the residual of the asset.
            Line with the asset account, whose amount is the gross value.
        """
        category_id = line.asset_id.category_id
        account_analytic_id = line.asset_id.account_analytic_id
        analytic_tag_ids = line.asset_id.analytic_tag_ids
        depreciation_date = (
            self.env.context.get('depreciation_date')
            or line.depreciation_date
            or line.asset_id.get_mx_current_datetime())
        company_currency = line.asset_id.company_id.currency_id
        current_currency = line.asset_id.currency_id
        prec = company_currency.decimal_places
        asset_name = '%s (%s/%s)' % (
            line.asset_id.name, line.sequence,
            len(line.asset_id.depreciation_line_ids))

        amount = current_currency._convert(
            line.amount, company_currency, line.asset_id.company_id,
            depreciation_date)
        value = current_currency._convert(
            line.asset_id.value, company_currency, line.asset_id.company_id,
            depreciation_date)

        # /!\ NOTE: Reverse Asset Account
        move_line_1 = {
            'name': asset_name,
            'account_id': category_id.account_asset_id.id,
            'debit':
                0.0 if float_compare(value, 0.0, precision_digits=prec) > 0
                else -value,
            'credit':
                value if float_compare(value, 0.0, precision_digits=prec) > 0
                else 0.0,
            'partner_id': line.asset_id.partner_id.id,
            'analytic_account_id':
                category_id.type == 'sale' and account_analytic_id.id,
            'analytic_tag_ids':
                category_id.type == 'sale' and [(6, 0, analytic_tag_ids.ids)],
            'currency_id':
                company_currency != current_currency and current_currency.id,
            'amount_currency':
                -line.asset_id.value if company_currency != current_currency
                else 0.0,
        }
        # /!\ NOTE: Reverse Cumulative Account
        move_line_2 = {
            'name': asset_name,
            'account_id': category_id.account_depreciation_id.id,
            'debit':
                (value - amount) if float_compare(
                    value - amount, 0.0, precision_digits=prec) > 0
                else 0.0,
            'credit':
                0.0 if float_compare(
                    value - amount, 0.0, precision_digits=prec) > 0
                else -(value - amount),
            'partner_id': line.asset_id.partner_id.id,
            'analytic_account_id':
                category_id.type == 'sale' and account_analytic_id.id,
            'analytic_tag_ids':
                category_id.type == 'sale' and [(6, 0, analytic_tag_ids.ids)],
            'currency_id':
                company_currency != current_currency and current_currency.id,
            'amount_currency':
                (line.asset_id.value - line.amount)
                if company_currency != current_currency
                else 0.0,
        }
        # /!\ NOTE: Cogs Account
        move_line_3 = {
            'name': asset_name,
            'account_id': category_id.account_cogs_id.id,
            'debit':
                amount if float_compare(amount, 0.0, precision_digits=prec) > 0
                else 0.0,
            'credit':
                0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0
                else -amount,
            'partner_id': line.asset_id.partner_id.id,
            'analytic_account_id':
                category_id.type == 'purchase' and account_analytic_id.id,
            'analytic_tag_ids': category_id.type == 'purchase' and [
                (6, 0, analytic_tag_ids.ids)],
            'currency_id':
                company_currency != current_currency and current_currency.id,
            'amount_currency':
                line.amount if company_currency != current_currency else 0.0,
        }
        move_vals = {
            'ref': line.asset_id.code,
            'date': depreciation_date or False,
            'journal_id': category_id.journal_id.id,
            'line_ids': [
                (0, 0, move_line_1), (0, 0, move_line_2), (0, 0, move_line_3)],
        }
        return move_vals

    @api.multi
    def create_sale_move(self, post_move=True):
        if self.mapped('move_id'):
            raise UserError(_(
                'This depreciation is already linked to a journal entry. '
                'Please post or delete it.'))
        cogs_not_configured = self.mapped('asset_id.category_id').filtered(
            lambda x: not x.account_cogs_id)
        if cogs_not_configured:
            raise UserError(_(
                'COGS account of asset category needs to be configured. '
                'Please check the asset category.'))
        created_moves = self.env['account.move']
        for line in self:
            move_vals = self._prepare_sale_move(line)
            move = self.env['account.move'].create(move_vals)
            line.write({'move_id': move.id, 'move_check': True})
            created_moves |= move

        if post_move and created_moves:
            with_opened_assets = created_moves.filtered(
                lambda m:
                any(m.asset_depreciation_ids.mapped(
                    'asset_id.category_id.open_asset')))
            with_opened_assets.post()
        return created_moves.ids


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    def get_mx_current_datetime(self):
        return fields.Datetime.context_timestamp(
            self.with_context(tz='America/Mexico_City'), fields.Datetime.now())

    def _get_sale_moves(self):
        move_ids = []
        for asset in self:
            unposted_depreciation_line_ids = (
                asset.depreciation_line_ids.filtered(
                    lambda x: not x.move_check))
            if not unposted_depreciation_line_ids:
                continue

            old_values = {
                'method_end': asset.method_end,
                'method_number': asset.method_number,
            }

            # Remove all unposted depr. lines
            commands = [
                (2, line_id.id, False)
                for line_id in unposted_depreciation_line_ids]

            # Create a new depr. line with the residual amount and post it
            sequence = len(asset.depreciation_line_ids) - len(
                unposted_depreciation_line_ids) + 1
            today = self.get_mx_current_datetime()
            vals = {
                'amount': asset.value_residual,
                'asset_id': asset.id,
                'sequence': sequence,
                'name': (asset.code or '') + '/' + str(sequence),
                'remaining_value': 0,
                # the asset is completely depreciated
                'depreciated_value': asset.value - asset.salvage_value,
                'depreciation_date': today,
            }
            commands.append((0, False, vals))
            asset.write({
                'depreciation_line_ids': commands,
                'method_end': today,
                'method_number': sequence
            })
            tracked_fields = self.env['account.asset.asset'].fields_get(
                ['method_number', 'method_end'])
            changes, tracking_value_ids = asset._message_track(
                tracked_fields, old_values)
            if changes:
                asset.message_post(
                    body=_('Asset sold. '
                           'Accounting entry awaiting for validation.'),
                    tracking_value_ids=tracking_value_ids)
            move_ids += asset.depreciation_line_ids[-1].create_sale_move(
                post_move=False)

        return move_ids

    @api.multi
    def sale_and_set_to_close(self):
        move_ids = self._get_sale_moves()
        if move_ids:
            name = _('Sale Move')
            view_mode = 'form'
            if len(move_ids) > 1:
                name = _('Sale Moves')
                view_mode = 'tree,form'
            return {
                'name': name,
                'view_type': 'form',
                'view_mode': view_mode,
                'res_model': 'account.move',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'res_id': move_ids[0],
            }
        # Fallback, as if we just clicked on the smartbutton
        return self.open_entries()

    @api.multi
    def execute_depreciation(self):
        if self.filtered(lambda asset: asset.state != 'open'):
            raise UserError(_(
                'This action can only be executed in confirmed fixed assets.'))
        self._cron_generate_entries()

    @api.multi
    def validate_entries(self):
        open_assets = self.filtered(lambda a: a.state == 'open')
        open_assets.mapped('depreciation_line_ids.move_id').filtered(
            lambda d: d.state == 'draft').post()

    @api.multi
    def reopen_asset(self):
        self.write({'state': 'open'})
        self.message_post(body=_('This fixed asset has been reopened.'))
