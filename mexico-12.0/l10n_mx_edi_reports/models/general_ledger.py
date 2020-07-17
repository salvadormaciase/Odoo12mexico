# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from odoo import fields, models, _, tools
from odoo.tools.xml_utils import _check_with_xsd
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.web.controllers.main import clean_action

MX_NS_REFACTORING = {
    'PLZ_': 'PLZ',
}

CFDIPLZ_TEMPLATE = 'l10n_mx_edi_reports.cfdimoves'
CFDIPLZ_XSD = 'l10n_mx_edi_reports/data/xsd/%s/cfdimoves.xsd'
CFDIPLZ_XSLT = 'l10n_mx_edi_reports/data/xslt/%s/PolizasPeriodo_1_2.xslt'


class MxReportJournalEntries(models.AbstractModel):
    _name = "l10n_mx.general.ledger.report"
    _inherit = "account.general.ledger"
    _description = "Mexican General Ledger Report"

    filter_request_type = 'AF'
    filter_order_number = ''
    filter_process_number = ''
    filter_move_name = ''

    def _get_reports_buttons(self):
        """Create the buttons to be used to download the required files"""
        buttons = super(MxReportJournalEntries, self)._get_reports_buttons()
        buttons += [
            {'name': _('Export For SAT (XML)'), 'action': 'print_xml'}]
        return buttons

    def _get_templates(self):
        templates = super(MxReportJournalEntries, self)._get_templates()
        templates['line_template'] = 'l10n_mx_edi_reports.new_line_template_general_ledger_report'  # noqa
        return templates

    def _get_columns_name(self, options):
        return [{'name': ''},
                {'name': _("Date"), 'class': 'date'},
                {'name': _("Acc. Number"), 'class': 'text'},
                {'name': _("Acc. Name"), 'class': 'text'},
                {'name': _("Debit"), 'class': 'number'},
                {'name': _("Credit"), 'class': 'number'}]

    def group_by_journal_id(self, options, line_id):
        journals = {}
        context = self.env.context
        move_obj = self.env['account.move.line']
        entry_obj = self.env['account.move']
        domain = []
        if context.get('journal_ids'):
            domain = [('id', 'in', context.get('journal_ids'))]
        journal_ids = self.env['account.journal'].search(domain)
        if options.get('move_name'):
            move = entry_obj.search([
                ('ref', 'ilike', options.get('move_name'))])
            journal_ids = move.mapped('journal_id')
        for journal in journal_ids:
            journals[journal] = {}
            domain = [
                ('date', '<=', context['date_to']),
                ('company_id', 'in', context['company_ids']),
                ('journal_id', '=', journal.id)]
            if context['date_from_aml']:
                domain.append(('date', '>=', context['date_from_aml']))
            if context['state'] == 'posted':
                domain.append(('move_id.state', '=', 'posted'))
            if context.get('account_tag_ids'):
                domain += [('account_id.tag_ids', 'in', context[
                    'account_tag_ids'].ids)]
            if context.get('analytic_tag_ids'):
                domain += [
                    '|', ('analytic_account_id.tag_ids', 'in', context[
                        'analytic_tag_ids'].ids),
                    ('analytic_tag_ids', 'in', context[
                        'analytic_tag_ids'].ids)]
            if context.get('analytic_account_ids'):
                domain += [('analytic_account_id', 'in', context[
                    'analytic_account_ids'].ids)]
            if options.get('move_name'):
                domain += [('move_id', 'in', move.ids)]
            if not context.get('print_mode'):
                move_ids = [
                    m['move_id'][0] for m in move_obj.read_group(
                        domain, ['move_id'], 'move_id', limit=81)]
            else:
                move_ids = [
                    m['move_id'][0] for m in move_obj.read_group(
                        domain, ['move_id'], 'move_id')]
            journals[journal]['lines'] = entry_obj.search(
                [('id', 'in', move_ids)], order='date')
        return journals

    def _get_lines(self, options, line_id=None):
        # update filter_date to get report name
        self.filter_date.update({
            'date_to': options.get('date').get('date_to'),
            'date_from': options.get('date').get('date_from')})

        lines = []
        line_id = int(line_id.split('_')[1]) if line_id else None
        if line_id:
            lines.extend(self._get_lines_second_level(
                options, self.env['account.move'].browse(line_id)))
            return lines
        context = self.env.context
        company_id = context.get('company_id') or self.env.user.company_id
        dt_from = options['date'].get('date_from')
        grouped_journals = self.with_context(
            date_from_aml=dt_from,
            date_from=dt_from and
            company_id.compute_fiscalyear_dates(datetime.strptime(
                dt_from, "%Y-%m-%d"))['date_from'] or None
        ).group_by_journal_id(options, line_id)
        sorted_journals = sorted(grouped_journals, key=lambda a: a.code)
        for journal in sorted_journals:
            if not grouped_journals[journal].get('lines', []):
                continue
            lines.append({
                'id': 'journal_%s' % journal.id,
                'type': 'journal',
                'name': journal.name,
                'footnotes': {},
                'columns': [],
                'level': 1,
                'unfoldable': False,
                'unfolded': True,
                'colspan': 6,
            })
            lines.extend(self._get_lines_second_level(
                options, grouped_journals[journal].get('lines', [])))
        return lines

    def _get_lines_second_level(self, options, move_ids):
        lines = []
        context = self.env.context
        unfold_all = context.get('print_mode') and len(
            options.get('unfolded_lines')) == 0
        too_many = False
        moves = move_ids
        if len(move_ids) > 80 and not context.get('print_mode'):
            too_many = True
            moves = move_ids[:80]
        for move in moves:
            name = move.name
            name = name[:33] + "..." if len(name) > 35 else name
            line_id = 'move_%s' % move.id
            lines.append({
                'id': line_id,
                'type': 'line',
                'name': name,
                'parent_id': 'journal_%s' % move.journal_id,
                'footnotes': {},
                'columns': [{'name': v} for v in [move.date, '', '', '', '']],
                'level': 2,
                'unfoldable': True,
                'unfolded': line_id in options.get(
                    'unfolded_lines') or unfold_all
            })
            if line_id in options.get('unfolded_lines') or unfold_all:
                lines.extend(self._get_lines_third_level(move))
        if too_many:
            lines.append({
                'id': 'too_many%s' % move_ids[0].journal_id.id,
                'parent_id': 'journal_%s' % move_ids[0].journal_id,
                'name': _('There are more than 80 items in this list, click here to see all of them'),  # noqa
                'columns': [{'name': v} for v in ['', '', '', '', '']],
                'action': 'view_too_many',
                'action_id': 'journal,%s' % (move_ids[0].journal_id.id,),
            })
        return lines

    def _get_lines_third_level(self, move):
        lines = []
        basis_account_ids = self.env['account.tax'].search_read(
            [('cash_basis_base_account_id', '!=', False)],
            ['cash_basis_base_account_id'])
        basis_account_ids = list(set([account[
            'cash_basis_base_account_id'][0] for account in basis_account_ids]
        ))
        for line in move.line_ids.filtered(
                lambda l: l.account_id.id not in basis_account_ids):
            name = line.name or line.move_id.name
            name = name[:43] + "..." if len(name) > 45 else name
            lines.append({
                'id': line.id,
                'move_id': move.id,
                'caret_options': self._get_caret_type(line),
                'type': 'move_line_id',
                'name': name,
                'parent_id': 'move_%s' % move.id,
                'footnotes': {},
                'columns': [{'name': v} for v in [
                    '', line.account_id.code, line.account_id.name,
                    self.format_value(line.debit),
                    self.format_value(line.credit)]],
                'level': 3,
            })
        return lines

    def _get_caret_type(self, line):
        caret_type = 'account.move'
        if line.invoice_id:
            caret_type = 'account.invoice.in' if line.invoice_id.type in (
                'in_refund', 'in_invoice') else 'account.invoice.out'
        elif line.payment_id:
            caret_type = 'account.payment'
        return caret_type

    def view_too_many(self, options, params=None):
        model, active_id = params.get('actionId').split(',')
        ctx = self.env.context.copy()
        if model == 'journal':
            action = self.env.ref('account.action_move_line_select').read()[0]
            ctx.update({
                'search_default_journal_id': [int(active_id)],
                'default_journal_id': [int(active_id)],
                'active_id': int(active_id),
            })
            action = clean_action(action)
            action['context'] = ctx
            return action
        return super().view_too_many(options, params)

    def get_bce_dict(self, options):
        company = self.env.user.company_id
        xml_data = self._get_lines(options)
        lines = [int(l['id'][5:]) for l in xml_data if l['level'] == 2]
        moves = self.env['account.move'].browse(lines)
        date = fields.datetime.strptime(
            self.env.context['date_from'], DEFAULT_SERVER_DATE_FORMAT)
        basis_account_ids = self.env['account.tax'].search_read(
            [('cash_basis_base_account_id', '!=', False)],
            ['cash_basis_base_account_id'])
        basis_account_ids = list(set([account[
            'cash_basis_base_account_id'][0] for account in basis_account_ids]
        ))
        moves_to_exclude = [
            value.move_id.id for value in moves.mapped('line_ids').filtered(
                lambda m: m.account_id.id in basis_account_ids)]
        chart = {
            'month': str(date.month).zfill(2),
            'year': date.year,
            'moves': moves.filtered(lambda l: l.id not in moves_to_exclude),
            'company': company,
            'basis_account_ids': basis_account_ids,
        }
        return chart

    def get_xml(self, options):
        qweb = self.env['ir.qweb']
        version = '1.3'
        ctx = self._set_context(options)
        if not ctx.get('date_to'):
            return False
        ctx['no_format'] = True
        ctx['print_mode'] = True
        values = self.with_context(ctx).get_bce_dict(options)
        values.update({
            'request_type': options.get('request_type'),
            'order_number': options.get('order_number') or False,
            'process_number': options.get('process_number') or False,
        })
        cfdimoves = qweb.render(CFDIPLZ_TEMPLATE, values=values)
        for key, value in MX_NS_REFACTORING.items():
            cfdimoves = cfdimoves.replace(key.encode('UTF-8'),
                                          value.encode('UTF-8') + b':')
        cfdimoves = self.l10n_mx_edi_add_digital_stamp(
            CFDIPLZ_XSLT % version, cfdimoves)
        with tools.file_open(CFDIPLZ_XSD % version, "rb") as xsd:
            _check_with_xsd(cfdimoves, xsd)
        return cfdimoves

    def _get_report_name(self):
        """The structure to name the report is: VAT + YEAR + MONTH + PL"""
        date_report = fields.datetime.strptime(
            self.filter_date.get('date_to'), "%Y-%m-%d") if \
            self.filter_date.get('date_to', False) else fields.date.today()
        name = '%s%s%sPL' % (
            self.env.user.company_id.vat or '',
            date_report.year,
            str(date_report.month).zfill(2))
        return name.upper()
