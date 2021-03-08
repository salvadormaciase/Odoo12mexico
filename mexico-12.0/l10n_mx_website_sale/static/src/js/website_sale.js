odoo.define('l10n_mx_website_sale.website_sale', (require) => {
    'use strict';

    require('web.dom_ready');
    var sAnimations = require('website.content.snippets.animation');
    var WebsiteSale = sAnimations.registry.WebsiteSale;

    delete WebsiteSale.prototype.read_events['change select[name="country_id"]'];
    WebsiteSale.include({
        read_events: _.extend({}, WebsiteSale.prototype.read_events, {
            'change select[name="country_id"]': '_onChangeCountry',
            'change select[name="state_id"]': '_onChangeState',
        }),

        /**
         * This function was overriden to avoid altered the fields position in the
         * address template when the value of country_id changes
         * @override
         *
         * @private
         */
        _changeCountry: function () {
            self = this;
            if (!$("#country_id").val()) {
                return;
            }
            var country_code = $('#country_id option:selected').data('country-code');
            if (country_code == 'MX') {
                $('.div_city_name').hide();
                $('input[name="city"]').val('');
            } else {
                $('.div_city_name').show();
            }
            this._rpc({
                route: "/shop/country_infos/" + $("#country_id").val(),
                params: {
                    mode: 'shipping',
                },
            }).then(function (data) {
                var selectStates = $("select[name='state_id']");
                if (selectStates.data('init')===0 || selectStates.find('option').length===1) {
                    if (data.states.length) {
                        selectStates.html('');
                        _.each(data.states, function (x) {
                            var opt = $('<option>').text(x[1])
                                .attr('value', x[0])
                                .attr('data-code', x[2]);
                            selectStates.append(opt);
                        });
                        selectStates.parent('div').show();
                        $('.div_city').show();
                    } else {
                        selectStates.val('').parent('div').hide();
                        $('.div_city').hide();
                    }
                    selectStates.data('init', 0);
                } else {
                    selectStates.data('init', 0);

                }
                if (data.fields) {
                    var all_fields = ["street", "zip", "country_name"];
                    _.each(all_fields, function (field) {
                        $(".checkout_autoformat .div_" + field.split('_')[0]).toggle($.inArray(field, data.fields)>=0);
                    });
                }
                self._onChangeState();
            });
        },

        /**
         * @private
         */
        _onChangeState: function () {
            var selectCities = $("select[name='city_id']");
            if (!$("#state_id").val()){
                return;
            }
            this._rpc({
                route: "/shop/city_infos/" + $("#state_id").val(),
            }).then(function (data) {
                if (selectCities.data('init')===0 || selectCities.find('option').length===1) {
                    if (data.cities.length) {
                        selectCities.html('');
                        _.each(data.cities, function (x) {
                            var opt = $('<option>').text(x[1]).attr('value', x[0]);
                            selectCities.append(opt);
                        });
                        selectCities.parent('div').show();
                    } else {
                        selectCities.parent('div').hide();
                    }
                    selectCities.data('init', 0);
                }
            });
        },
    });
});
