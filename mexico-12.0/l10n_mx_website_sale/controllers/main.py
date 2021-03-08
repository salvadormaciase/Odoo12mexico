# Copyright 2016 Vauxoo Oscar Alcala <oscar@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo.addons.portal.controllers.portal import CustomerPortal as CP
from odoo.addons.website_sale.controllers.main import WebsiteSale as WS
from odoo import http
from odoo.http import request
from werkzeug.exceptions import Forbidden
import logging

_logger = logging.getLogger(__name__)


class CustomerPortal(CP):

    OPTIONAL_BILLING_FIELDS = ["zipcode", "state_id", "vat", "company_name", "city_id"]

    def __init__(self, **args):
        self.MANDATORY_BILLING_FIELDS.extend((
            'street_name',
            'street_number'))
        self.OPTIONAL_BILLING_FIELDS.extend((
            'street_number2',
            'l10n_mx_edi_locality',
            'l10n_mx_edi_colony',
        ))
        if 'street' in self.MANDATORY_BILLING_FIELDS:
            self.MANDATORY_BILLING_FIELDS.remove('street')
        super(CustomerPortal, self).__init__(**args)

    @http.route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values.update({
            'error': {},
            'error_message': [],
        })

        if post and request.httprequest.method == 'POST':
            country = post.get('country_id') and request.env['res.country'].browse(int(post['country_id']))
            if country.code == 'MX' and 'city_id' not in self.MANDATORY_BILLING_FIELDS:
                self.MANDATORY_BILLING_FIELDS.append('city_id')
            elif 'city_id' in self.MANDATORY_BILLING_FIELDS:
                self.MANDATORY_BILLING_FIELDS.remove('city_id')

            city = post.get('city_id') and request.env['res.city'].browse(int(post['city_id']))
            if city and city.country_id == country:
                post['city'] = city.name
            else:
                post['city'] = post['city'].strip()

            error, error_message = self.details_form_validate(post)
            values.update({'error': error, 'error_message': error_message})
            values.update(post)
            if not error:
                values = {key: post[key] for key in self.MANDATORY_BILLING_FIELDS}
                values.update({key: post[key] for key in self.OPTIONAL_BILLING_FIELDS if key in post})
                values.update({'zip': values.pop('zipcode', '')})
                partner.sudo().write(values)
                if redirect:
                    return request.redirect(redirect)
                return request.redirect('/my/home')

        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])
        cities = request.env['res.city'].sudo().search([])

        values.update({
            'partner': partner,
            'countries': countries,
            'states': states,
            'cities': cities,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'redirect': redirect,
            'page_name': 'my_details',
        })
        response = request.render("portal.portal_my_details", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response


class WebsiteSale(WS):

    def _get_mandatory_billing_fields(self):
        flds = super(WebsiteSale, self)._get_mandatory_billing_fields()
        flds.extend(('street_number', 'street_name'))
        if 'street' in flds:
            flds.remove('street')
        return flds

    def _get_mandatory_shipping_fields(self):
        flds = super(WebsiteSale, self)._get_mandatory_shipping_fields()
        flds.extend(('street_number', 'street_name'))
        if 'street' in flds:
            flds.remove('street')
        return flds

    @http.route(
        ['/shop/city_infos/<model("res.city"):state>'], type='json', auth="public", methods=['POST'], website=True)
    def city_infos(self, state, **kw):
        cities_per_state = request.env['res.city'].search([('state_id', '=', state.id)])
        return dict(
            cities=[(c.id, c.name) for c in cities_per_state],
        )

    def values_postprocess(self, order, mode, values, errors, error_msg):
        new_values = {}
        authorized_fields = request.env['ir.model']._get('res.partner')._get_form_writable_fields()
        for k, v in values.items():
            if k in authorized_fields and v is not None:
                new_values[k] = v
            else:
                if k not in ('field_required', 'partner_id', 'callback', 'submitted'):
                    _logger.debug("website_sale postprocess: %s value has been dropped (empty or not writable)" % k)

        new_values['city_id'] = values['city_id']
        new_values['customer'] = True
        new_values['team_id'] = request.website.salesteam_id and request.website.salesteam_id.id
        new_values['user_id'] = request.website.salesperson_id and request.website.salesperson_id.id

        if request.website.specific_user_account:
            new_values['website_id'] = request.website.id

        if mode[0] == 'new':
            new_values['company_id'] = request.website.company_id.id

        lang = request.lang if request.lang in request.website.mapped('language_ids.code') else None
        if lang:
            new_values['lang'] = lang
        if mode == ('edit', 'billing') and order.partner_id.type == 'contact':
            new_values['type'] = 'other'
        if mode[1] == 'shipping':
            new_values['parent_id'] = order.partner_id.commercial_partner_id.id
            new_values['type'] = 'delivery'

        return new_values, errors, error_msg

    # pylint: disable=too-complex
    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def address(self, **kw):
        Partner = request.env['res.partner'].with_context(show_address=1).sudo()
        order = request.website.sale_get_order()

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        mode = (False, False)
        can_edit_vat = False
        def_country_id = order.partner_id.country_id
        values, errors = {}, {}

        partner_id = int(kw.get('partner_id', -1))

        # IF PUBLIC ORDER
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            mode = ('new', 'billing')
            can_edit_vat = True
            country_code = request.session['geoip'].get('country_code')
            if country_code:
                def_country_id = request.env['res.country'].search([('code', '=', country_code)], limit=1)
            else:
                def_country_id = request.website.user_id.sudo().country_id
        # IF ORDER LINKED TO A PARTNER
        else:
            if partner_id > 0:
                if partner_id == order.partner_id.id:
                    mode = ('edit', 'billing')
                    can_edit_vat = order.partner_id.can_edit_vat()
                else:
                    shippings = Partner.search([('id', 'child_of', order.partner_id.commercial_partner_id.ids)])
                    if partner_id in shippings.mapped('id'):
                        mode = ('edit', 'shipping')
                    else:
                        return Forbidden()
                if mode:
                    values = Partner.browse(partner_id)
            elif partner_id == -1:
                mode = ('new', 'shipping')
            else:  # no mode - refresh without post?
                return request.redirect('/shop/checkout')

        # IF POSTED
        if 'submitted' in kw:
            pre_values = self.values_preprocess(order, mode, kw)
            country = pre_values.get('country_id') and request.env['res.country'].browse(int(pre_values['country_id']))
            city = pre_values.get('city_id') and request.env['res.city'].browse(int(pre_values['city_id']))
            if city and city.country_id == country:
                pre_values['city'] = city.name
            else:
                pre_values['city'] = pre_values['city'].strip()
            errors, error_msg = self.checkout_form_validate(mode, kw, pre_values)
            post, errors, error_msg = self.values_postprocess(order, mode, pre_values, errors, error_msg)

            if errors:
                errors['error_message'] = error_msg
                values = kw
            else:
                partner_id = self._checkout_form_save(mode, post, kw)
                if mode[1] == 'billing':
                    order.partner_id = partner_id
                    order.onchange_partner_id()
                    #  This is the *only* thing that the front end user will see/edit anyway when choosing billing
                    #  address
                    order.partner_invoice_id = partner_id
                    if not kw.get('use_same'):
                        kw['callback'] = kw.get('callback') or \
                            (not order.only_services and (mode[0] == 'edit' and '/shop/checkout' or '/shop/address'))
                elif mode[1] == 'shipping':
                    order.partner_shipping_id = partner_id

                order.message_partner_ids = [(4, partner_id), (3, request.website.partner_id.id)]
                if not errors:
                    return request.redirect(kw.get('callback') or '/shop/confirm_order')
        country = 'country_id' in values and values['country_id'] != '' and request.env['res.country'].browse(
            int(values['country_id']))
        country = country and country.exists() or def_country_id
        partner = request.env['res.partner'].browse(partner_id)
        render_values = {
            'website_sale_order': order,
            'partner': partner,
            'partner_id': partner_id,
            'mode': mode,
            'checkout': values,
            'can_edit_vat': can_edit_vat,
            'country': country,
            'countries': country.get_website_sale_countries(mode=mode[1]),
            "states": country.get_website_sale_states(mode=mode[1]),
            'error': errors,
            'callback': kw.get('callback'),
            'only_services': order and order.only_services,
        }
        return request.render("website_sale.address", render_values)
