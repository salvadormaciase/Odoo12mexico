from odoo import models, fields, api
from ..models.account import get_day_one


class RealizationDateWizard(models.TransientModel):
    _name = 'realization.date.wizard'
    _description = 'Running the realization process'

    @api.onchange('realization_date')
    def onchange_internal_type(self):
        date = self.realization_date
        self.init_date = get_day_one(date)

    realization_date = fields.Date(
        default=lambda self: fields.Date.today(),
        help='Date used to compute the realization to invoices selected')
    init_date = fields.Date(
        string='Initial Date',
        help='Realization Entries will be created from this date onwards.')

    def compute_realization(self):
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')

        if not active_ids:
            return False

        if active_model not in ('account.move', 'account.account'):
            return False

        self.env[active_model].browse(active_ids).create_realization_entries(
            self.realization_date, self.init_date)
        return True
