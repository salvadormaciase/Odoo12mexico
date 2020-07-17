from odoo import models, fields, api, _
from odoo.exceptions import Warning as UserError


class WizardMassInvoiceSending(models.TransientModel):
    _name = 'wizard.mass.invoice.sending'
    _description = 'Mass invoice sending'

    invoice_ids = fields.Many2many(
        'account.invoice', 'account_invoice_wizard_mass_invoice_sending_rel',
        string='Invoices')
    template_id = fields.Many2one(
        'mail.template', 'Use template',
        domain="[('model', '=', 'account.invoice')]")
    partner_id = fields.Many2one('res.partner', 'Customer')
    body = fields.Html('Contents', default='', sanitize_style=True)
    attachment_ids = fields.Many2many(
        'ir.attachment', string='Attachments',
        help='Attachments are linked to a document through model / res_id '
        'and to the message through this field.')

    @api.multi
    def generate_email_for_composer(self):
        mail_fields = ['body_html', 'email_from', 'email_to',
                       'partner_to', 'email_cc', 'reply_to', 'attachment_ids']
        returned_fields = mail_fields + ['partner_ids', 'attachments']
        invoices = self.env['account.invoice'].search([
            ('id', 'in', self._context.get('active_ids')),
        ])
        values = dict.fromkeys(invoices.ids, False)
        template_values = self.with_context(
            invoices=invoices).template_id.generate_email(invoices.ids)

        for res_id in invoices.ids:
            res_id_values = dict(
                (field, template_values[res_id][field])
                for field in returned_fields
                if template_values[res_id].get(field))
            res_id_values['body'] = res_id_values.pop('body_html', '')
            values[res_id] = res_id_values
        return values

    @api.model
    def default_get(self, res_fields):
        res = super(WizardMassInvoiceSending, self).default_get(res_fields)
        res_ids = self._context.get('active_ids')
        invoices = self.env['account.invoice'].browse(res_ids)
        partner_id = invoices.mapped('partner_id')
        if len(partner_id) > 1:
            raise UserError(_(
                "Please select invoices that belongs to only one customer.\n"
                "This feature works only with a set of invoices that belong "
                "to 1 customer at a time, please pre-filter accordingly."))
        res.update({
            'invoice_ids': res_ids,
            'partner_id': partner_id.id,
        })
        return res

    @api.multi
    @api.model
    def send_email(self):
        partner = self.partner_id
        email = partner.browse(
            partner.address_get(['invoice'])['invoice']).email
        if not (email and email.strip()):
            raise UserError(_(
                'Could not send mail to partner because it does '
                'not have any email address defined'))
        msg = _('Follow-up email sent to %s\n %s') % (email, self.body)
        mail_values = {
            'subject': _('%s Payment Reminder') % (
                self.env.user.company_id.name) + ' - ' + partner.name,
            'body': msg,
            'attachment_ids': [attach.id for attach in self.attachment_ids],
            'author_id': self.env.user.id,
            'model': 'res.partner',
            'email_from': self.env.user.email or '',
        }
        subtype_id = self.env['ir.model.data'].xmlid_to_res_id(
            'mail.mt_comment')
        post_params = dict(
            message_type='comment',
            subtype_id=subtype_id,
            mail_auto_delete=self.template_id.auto_delete,
            **mail_values)
        partner.message_post(**post_params)
        partner.message_subscribe([partner.id])
        return {'type': 'ir.actions.act_window_close', 'infos': 'mail_sent'}

    @api.multi
    @api.onchange('template_id')
    def onchange_template_id(self):
        self.ensure_one()
        inv_id = self._context.get('active_id')
        values = {}
        if not self.template_id:
            return {'value': values}
        res = self.generate_email_for_composer()
        attachment_ids = []
        attachment = self.env['ir.attachment']
        for vals in res.values():
            for attach_fname, attach_datas in vals.pop('attachments', []):
                data_attach = {
                    'name': attach_fname,
                    'datas': attach_datas,
                    'datas_fname': attach_fname,
                    'res_model': 'mail.compose.message',
                    'res_id': 0,
                    'type': 'binary',
                }
                attachment_ids.append(attachment.create(data_attach).id)
            if vals.get('attachment_ids', []) or attachment_ids:
                values['attachment_ids'] = [(5,)] + vals.get(
                    'attachment_ids', []) + attachment_ids
        values['body'] = res[inv_id].pop('body')
        values = self._convert_to_write(values)
        return {'value': values}
