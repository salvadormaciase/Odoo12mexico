odoo.define('l10n_mx_website_sale.portal', function (require) {
    'use strict';
    require('web.dom_ready');

    if (!$('.o_portal_details').length) {
        return $.Deferred().reject("DOM doesn't contain '.o_portal_details'");
    }

    if ($('.o_portal_details').length) {
        var city_options = $("select[name='city_id']:enabled option:not(:first)");
        $('.o_portal_details').on('change', "select[name='state_id']", function () {
            var selec = $("select[name='city_id']");
            city_options.detach();
            var displayed_city = city_options.filter("[data-state_id="+($(this).val() || 0)+"]");
            var nb = displayed_city.appendTo(selec).show().size();
            selec.parent().toggle(nb>=1);
        });
        $('.o_portal_details').find("select[name='state_id']").change();
        $('.o_portal_details').on('change', "select[name='country_id']", function () {
            var country_code = $('#country_id option:selected').data('country-code');
            if (country_code === 'MX') {
                $('.div_city_name').hide();
                $('input[name="city"]').val('');
                $('.div_city').show();
            } else {
                $('.div_city_name').show();
                $('.div_city').hide();
            }
        });
        $('.o_portal_details').find("select[name='country_id']").change();
    }
});
