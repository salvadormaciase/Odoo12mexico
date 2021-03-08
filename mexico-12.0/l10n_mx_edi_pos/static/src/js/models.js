odoo.define('l10n_mx_edi_pos.models', function (require) {
"use strict";

    var Models = require('point_of_sale.models');
    var Session = require('web.session');


    // Load the new SAT fields of the client to the POS
    Models.load_fields('res.partner', ['l10n_mx_edi_payment_method_id', 'l10n_mx_edi_usage']);

    Models.load_models([
        {   // Load the values of l10n_mx_edi_payment_method_id
            model:  'l10n_mx_edi.payment.method',
            fields: ['name'],
            loaded: function(self, payment_methods){
                self.payment_methods = payment_methods;
            },
        },
        {   // Load the values of l10n_mx_edi_usage
            label:  'edi_usages',
            loaded: function(self){
                return Session.rpc('/web/dataset/call_kw',{
                    args: [], model: "account.invoice",
                    method: "fields_get", kwargs: {}
                }).done(function(fields) {
                    self.edi_usages = fields.l10n_mx_edi_usage.selection;
                    self.edi_usages_by_id = {};
                    _.each(self.edi_usages, function(usage){
                        self.edi_usages_by_id[usage[0]] = usage[1];
                    });
                });
            },
        }
    ]);

});
