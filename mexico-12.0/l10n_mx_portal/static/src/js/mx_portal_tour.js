odoo.define('l10n_mx_portal.tour', function (require) {
'use strict';

var tour = require('web_tour.tour');
var base = require('web_editor.base');

tour.register('mx_portal_tour', {
    test: true,
    url: '/my/invoices',
    wait_for: base.ready()
    },
    [
        {
            content:  "Send email",
            trigger: "a[title='Send Email']:first()",
        },
        {
            content:  "Wait Confirmation",
            trigger: 'h3.alert.alert-success',
        }
    ]
);

});
