# Copyright 2018 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models, fields


class L10nMXEdiCustoms(models.Model):
    _name = 'l10n_mx_edi.customs'
    _inherit = ['mail.thread']

    _description = """In MX customs == Pedimento, this is a model to
    administer such information in order to relate the proper VAT with the
    Invoices"""

    name = fields.Char(
        "Customs Number", help="Example: 19 24 3420 9000104",
        track_visibility='onchange', required=True, copy=False,
        readonly=True, states={'draft': [('readonly', False)]})
    display_name = fields.Char(
        compute='_compute_display_name', store=True)
    date = fields.Date(track_visibility='onchange',
                       readonly=True, states={'draft': [('readonly', False)]},
                       help='Custom Date, will be used in the '
                       'invoice to create.')
    payment_date = fields.Date(
        track_visibility='onchange', readonly=True,
        states={'draft': [('readonly', False)]},
        help='Custom Payment Date, will be used in the payment to create, use '
        'only if the payment date is different to the customs date, then if '
        'is empty, will be used the customs date.')
    other_increments = fields.Float(
        track_visibility='onchange',
        readonly=True, states={'draft': [('readonly', False)]})
    other_taxes = fields.Float(
        track_visibility='onchange',
        readonly=True, states={'draft': [('readonly', False)]})
    cnt = fields.Float(
        track_visibility='onchange', help='Consideration for pre-validation '
        'purposes',
        readonly=True, states={'draft': [('readonly', False)]})
    dta = fields.Float(track_visibility='onchange', help='Customs Procedure '
                       'Law',
                       readonly=True, states={'draft': [('readonly', False)]})
    igi = fields.Float(
        track_visibility='onchange', help='General '
        'Importation Tax',
        readonly=True, states={'draft': [('readonly', False)]})
    prv = fields.Float(
        track_visibility='onchange', help='Application pre-validation',
        readonly=True, states={'draft': [('readonly', False)]})
    iva = fields.Float(
        track_visibility='onchange',
        readonly=True, states={'draft': [('readonly', False)]})
    cc = fields.Float(
        track_visibility='onchange',
        readonly=True, states={'draft': [('readonly', False)]})
    freight = fields.Float(
        track_visibility='onchange',
        readonly=True, states={'draft': [('readonly', False)]})
    cc = fields.Float(
        track_visibility='onchange',
        readonly=True, states={'draft': [('readonly', False)]})
    rate = fields.Float(
        track_visibility='onchange', digits=(16, 5),
        readonly=True, states={'draft': [('readonly', False)]})
    operation = fields.Char(
        track_visibility='onchange',
        readonly=True, states={'draft': [('readonly', False)]})
    key_custom = fields.Char(
        track_visibility='onchange',
        readonly=True, states={'draft': [('readonly', False)]})
    regime = fields.Char(
        track_visibility='onchange',
        readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], track_visibility='onchange', default="draft",
        help="Draft when you are just creating it, confirmed to block it and"
             "done it will affect the DIOT")
    invoice_ids = fields.One2many(
        'account.invoice', 'l10n_mx_edi_customs_id', help='Customs related '
        'with this invoice.')
    invoice_extra_ids = fields.One2many(
        'account.invoice', 'l10n_mx_edi_customs_extra_id',
        help='Customs related with this invoice, for extra expenses.')
    amount_total = fields.Float(
        compute='_compute_amount_total', help='Get the amount total of the '
        'invoices related.',
        readonly=True, states={'draft': [('readonly', False)]})
    journal_payment_id = fields.Many2one(
        'account.journal', help='Journal used to pay this custom.',
        domain=[('type', 'in', ['cash', 'bank'])], track_visibility='onchange',
        default=True, readonly=True, states={'draft': [('readonly', False)]})
    journal_invoice_id = fields.Many2one(
        'account.journal', help='Journal to use in the invoice to create.',
        domain=[('type', '=', 'purchase')], track_visibility='onchange',
        default=True, readonly=True, states={'draft': [('readonly', False)]}
    )
    sat_partner_id = fields.Many2one(
        'res.partner', help='Supplier that will be used to create the SAT '
        'invoice.', track_visibility='onchange', default=True,
        readonly=True, states={'draft': [('readonly', False)]},
    )
    account_dta_id = fields.Many2one(
        'account.account', help='Account that will be used for the DTA line.',
        track_visibility='onchange', default=True,
        readonly=True, states={'draft': [('readonly', False)]},
    )
    account_igi_id = fields.Many2one(
        'account.account', help='Account that will be used for the IGI line.',
        track_visibility='onchange', default=True,
        readonly=True, states={'draft': [('readonly', False)]},
    )
    account_other_id = fields.Many2one(
        'account.account', 'Account PRV-CNT', help='Account that will be used '
        'for the PRV and CNT line.', track_visibility='onchange', default=True,
        readonly=True, states={'draft': [('readonly', False)]},
    )
    account_cc_id = fields.Many2one(
        'account.account', help='Account that will be used for the CC line.',
        track_visibility='onchange', default=True,
        readonly=True, states={'draft': [('readonly', False)]},
    )
    account_other_taxes_id = fields.Many2one(
        'account.account', help='Account that will be used for '
        'Other Taxes line.', track_visibility='onchange', default=True,
        readonly=True, states={'draft': [('readonly', False)]},
    )
    sat_invoice_id = fields.Many2one(
        'account.invoice', help='Invoice generated to this custom.',
        readonly=True, copy=False
    )
    partner_id = fields.Many2one(
        'res.partner', 'Broker', help='Indicate the broker of this customs.',
        track_visibility='onchange', ondelete='restrict')
    company_id = fields.Many2one(
        'res.company', change_default=True,
        required=True, readonly=True, states={'draft': [('readonly', False)]},
        default=lambda self: self.env['res.company']._company_default_get(
            'account.invoice'))

    _sql_constraints = [
        ('custom_number_unique', 'unique (name)', _(
            'The name must be unique !'))
    ]

    @api.depends('name')
    def _compute_display_name(self):
        for custom in self:
            name = custom.name
            try:
                custom.display_name = '%s  %s  %s  %s' % (
                    name[:2], name[2:4], name[4:8], name[8:])
            except Exception:
                custom.display_name = name

    @api.depends('invoice_ids.amount_total')
    def _compute_amount(self):
        for record in self:
            record.amount_total = sum(record.invoice_ids.mapped(
                'amount_total'))

    @api.multi
    def action_open_custom_invoice(self):
        self.ensure_one()
        return {
            'name': _('Customs invoice'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', '=', self.sat_invoice_id.id)],
            'context': {
                'type': 'in_invoice',
            }
        }

    @api.multi
    def action_open_invoices(self):
        self.ensure_one()
        return {
            'name': _('Invoices'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.invoice_ids.ids)],
            'context': {
                'type': 'in_invoice',
            }
        }

    @api.depends('cnt', 'dta', 'igi', 'iva', 'prv', 'cc', 'freight',
                 'other_increments')
    def _compute_amount_total(self):
        for record in self:
            record.amount_total = sum([
                record.cnt, record.dta, record.igi, record.iva, record.prv,
                record.cc, record.other_taxes])

    @api.multi
    def approve_custom(self):
        """Create the customs invoice with data from the custom.
        The lines to freight, Other increments, IGI, DTA and CC could be join
        in a line by each partner of the customs. To this, is necessary create
        a system parameter with the key 'customs_line_apportionment'. This will
        to allow get the amounts in the DIOT report for each vendor."""
        invoice = self.env['account.invoice']
        payment = self.env['account.register.payments']
        invoice_line = self.env['account.invoice.line']
        tag_imp = self.env.ref('l10n_mx.tag_diot_16_imp')
        imp_local = self.env['account.tax'].search(
            [('tag_ids', 'in', tag_imp.ids)], limit=1).ids
        product_tax = self.env.ref(
            'l10n_mx_edi_customs_diot.l10n_mx_edi_tax_product')
        account_tax = (
            product_tax.property_account_expense_id.id or
            product_tax.categ_id.property_account_expense_categ_id.id)
        join_lines = self.env['ir.config_parameter'].sudo().get_param(
            'customs_line_apportionment', False)
        for record in self:
            invoice_line_ids = []
            if record.prv or record.cnt:
                invoice_line_ids.append((0, 0, {
                    'account_id': record.account_other_id.id,
                    'name': 'PRV + CNT',
                    'quantity': 1,
                    'price_unit': sum([record.prv, record.cnt]),
                }))
            if record.cc:
                invoice_line_ids.append((0, 0, {
                    'account_id': record.account_other_id.id,
                    'name': 'CC',
                    'quantity': 1,
                    'price_unit': record.cc,
                }))
            if record.other_taxes:
                invoice_line_ids.append((0, 0, {
                    'account_id': record.account_other_id.id,
                    'name': 'OTROS IMPUESTOS',
                    'quantity': 1,
                    'price_unit': record.other_taxes,
                }))
            if record.dta:
                invoice_line_ids.append((0, 0, {
                    'account_id': record.account_dta_id.id,
                    'name': 'DTA',
                    'quantity': 1,
                    'invoice_line_tax_ids': [
                        (6, 0, imp_local if record.iva and not join_lines else [])],  # noqa
                    'price_unit': record.dta,
                }))
            if record.igi:
                invoice_line_ids.append((0, 0, {
                    'account_id': record.account_igi_id.id,
                    'name': 'IGI',
                    'quantity': 1,
                    'invoice_line_tax_ids': [(6, 0, imp_local if not join_lines else [])],  # noqa
                    'price_unit': record.igi,
                }))
            total_lines = sum([
                record.cc, record.dta, record.igi, record.freight, record.other_increments])
            for invoice in record.invoice_ids:
                invoice_line_ids.append((0, 0, {
                    'product_id': product_tax.id,
                    'account_id': account_tax,
                    'name': '%s' % (invoice.number or product_tax.name),
                    'quantity': 0,
                    'price_unit': invoice.l10n_mx_edi_customs_total - (
                        invoice.l10n_mx_edi_freight * record.rate),
                    'invoice_line_tax_ids': [
                        (6, 0, product_tax.supplier_taxes_id.ids)],
                    'x_l10n_mx_edi_invoice_broker_id': invoice.id,
                }))
                if join_lines:
                    invoice_line_ids.append((0, 0, {
                        'product_id': product_tax.id,
                        'account_id': account_tax,
                        'name': '%s' % _(
                            'Apportioning Line %s') % invoice.partner_id.name,
                        'quantity': 0,
                        'price_unit': total_lines / len(record.invoice_ids),
                        'invoice_line_tax_ids': [
                            (6, 0, product_tax.supplier_taxes_id.ids)],
                        'x_l10n_mx_edi_invoice_broker_id': invoice.id,
                    }))

            inv = invoice.create({
                'partner_id': record.sat_partner_id.id,
                'date_invoice': record.date,
                'invoice_line_ids': invoice_line_ids,
                'type': 'in_invoice',
                'journal_id': record.journal_invoice_id.id,
            })
            if not join_lines and record.other_increments:
                inv.tax_line_ids[-1].copy({
                    'amount': record.other_increments * 0.16,
                    'name': _('Tax Other Increments'),
                    'manual': True,
                })
            if not join_lines and record.freight:
                inv.tax_line_ids[-1].copy({
                    'amount': record.freight * 0.16,
                    'name': _('Tax Freight'),
                    'manual': True,
                })
            inv.compute_taxes()
            if record.amount_total != inv.amount_total:
                difference_account = (int(
                    self.env['ir.config_parameter'].sudo().get_param(
                        'customs_difference_account', False)) or
                    invoice_line.with_context({
                        'journal_id': record.journal_invoice_id.id,
                        'type': 'in_invoice'})._default_account())
                inv.invoice_line_ids = [(0, 0, {
                    'account_id': difference_account,
                    'name': _('Difference adjustment'),
                    'quantity': 0,
                    'price_unit': (record.amount_total - inv.amount_total) / 0.16,
                    'invoice_line_tax_ids': [(6, 0, imp_local)],
                })]
                inv.compute_taxes()
            inv.action_invoice_open()
            record.sat_invoice_id = inv
            self.fix_invoice_customs_entry()
            ctx = {'active_model': 'account.invoice',
                   'active_ids': inv.ids}
            payment_method = record.journal_payment_id.outbound_payment_method_ids  # noqa
            payment.with_context(ctx).create({
                'payment_date': record.payment_date or record.date,
                'payment_method_id': payment_method[
                    0].id if payment_method else False,
                'journal_id': record.journal_payment_id.id,
                'communication': _('Payment SAT'),
                'amount': inv.amount_total,
            }).create_payments()
            record.state = 'confirmed'

    @api.multi
    def fix_invoice_customs_entry(self):
        # TODO - Move to base automation
        self.ensure_one()
        move = self.sat_invoice_id.move_id
        partner = self.company_id.l10n_mx_edi_customs_partner_id or self.partner_id  # noqa
        move.line_ids.filtered(
            lambda l: l.partner_id == self.sat_partner_id and
            (l.tax_ids or l.name in (
                _('Tax Other Increments'), _('Difference adjustment'),
                _('Tax Freight')))
        ).write({'partner_id': partner.id})

    @api.multi
    def revert_custom(self):
        move_ids = self.env['account.move']
        for record in self.filtered('sat_invoice_id'):
            inv = record.sat_invoice_id
            if inv.state == 'cancel':
                continue
            moves = inv.payment_move_line_ids
            moves.mapped('payment_id').cancel()
            inv.mapped('move_id.line_ids').remove_move_reconcile()
            move_ids |= inv.move_id
            inv.action_cancel()
            inv.write({
                'move_name': False,
                'reference': '%s-cancelled' % (inv.reference or ''),
            })
        self.write({'state': 'draft'})
        move_ids.exists().unlink()

    @api.onchange('name')
    def onchange_name(self):
        """Search a partner with the same customs pattent"""
        name = (self.name or '').replace(' ', '')
        if len(name) >= 8:
            self.partner_id = self.env['res.partner'].search([
                ('l10n_mx_edi_customs_patent', '=', name[4:8])], limit=1)
