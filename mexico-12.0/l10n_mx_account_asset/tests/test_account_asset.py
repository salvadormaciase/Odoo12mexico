# Copyright 2019 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime
from odoo.addons.l10n_mx_edi.tests.common import InvoiceTransactionCase


class TestL10nMxAccountAsset(InvoiceTransactionCase):

    def test_00_account_asset_asset(self):
        asset = self.env.ref('l10n_mx_account_asset.account_asset_test_mx')
        # Compute depreciation lines for asset
        asset.compute_depreciation_board()
        self.assertEqual(asset.method_number, len(asset.depreciation_line_ids),
                         'Depreciation lines not created correctly')
        asset.compute_generated_entries(datetime.datetime(2019, 1, 1))
        asset.compute_generated_entries(datetime.datetime(2019, 2, 1))
        asset.compute_generated_entries(datetime.datetime(2019, 3, 1))
        value_residual = asset.value_residual
        gross_value = asset.value
        accum_depreciation = gross_value - value_residual
        # The sale_and_set_to_close method returns a view of the moves.
        # The method that really makes the moves is _get_sale_moves
        sale_move = self.env['account.move'].browse(asset._get_sale_moves())
        sale_move.post()

        # There is a line in the move that contains the asset's cogs account
        # with the residual amount of the asset.
        cogs_line = sale_move.mapped('line_ids').filtered(
            lambda a: a.account_id == asset.category_id.account_cogs_id)
        self.assertTrue(cogs_line)
        self.assertEqual(
            cogs_line.debit or cogs_line.credit, value_residual)

        # There is a line in the move that contains the asset's Asset Account
        # with the gross value of the asset
        asset_line = sale_move.mapped('line_ids').filtered(
            lambda a: a.account_id == asset.category_id.account_asset_id)
        self.assertTrue(asset_line)
        self.assertEqual(asset_line.credit or asset_line.debit, gross_value)

        # There is a line in the move that contains the asset's
        # Depreciation Account with the difference between gross value and
        # the residual of the asset
        depreciation_line = sale_move.mapped('line_ids').filtered(
            lambda a: a.account_id == asset.category_id.account_depreciation_id)  # noqa
        self.assertTrue(depreciation_line)
        self.assertEqual(
            depreciation_line.debit or depreciation_line.credit, accum_depreciation)  # noqa

        # The asset is close after sell it
        self.assertEqual(asset.state, 'close')
        # Reopen asset
        asset.reopen_asset()
        self.assertEqual(asset.state, 'open')
