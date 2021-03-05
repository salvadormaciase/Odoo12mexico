odoo.define('l10n_mx_reports.account_report', function (require) {
'use strict';


var accountReportsWidget = require('account_reports.account_report');

    accountReportsWidget.include({
        render_searchview_buttons: function() {
            this._super();
            var self = this;
            _.each(this.$searchview_buttons.find('.js_account_reports_details'), function(k) {
                $(k).toggleClass('selected', String(self.report_options[$(k).data('filter')]) === String($(k).data('id')));
            });
            this.$searchview_buttons.find('.js_account_reports_details').click(function (event) {
                self.report_options[$(this).data('filter')] = $(this).data('id');
                var order_number = $(this).parent().find('input[name="order"]');
                var process_number = $(this).parent().find('input[name="process"]');
                var move_name = $(this).parent().find('input[name="move"]');
                self.report_options.order_number = order_number.val();
                self.report_options.process_number = process_number.val();
                self.report_options.move_name = move_name.val();
                self.reload();
            });
        }
    });
});
