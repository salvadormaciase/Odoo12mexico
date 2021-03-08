odoo.define('l10n_mx_portal_vendor_bills.upload_attachments', function (require) {
'use strict';

    require('web.dom_ready');
    var core = require('web.core');
    var ajax = require('web.ajax');
    var snippet_animation = require('website.content.snippets.animation');

    var _t = core._t;
    snippet_animation.registry.form_builder_send = snippet_animation.Class.extend({
        selector: '.s_upload_attachments',
        start: function(){
            var self = this;
            this.$target.find('.btn_upload_attachments').on('click', function (e) {
                self.send(e);
            });
            return this._super.apply(this, arguments);
        },
        send: function (e) {
            e.preventDefault();  // Prevent the default submit behavior
            this.$target.find('.btn_upload_attachments').off();  // Prevent users from crazy clicking
            var self = this;
            var form_values = {};
            this.form_fields = this.$target.serializeArray();
            self.$target.find('#o_website_form_result').empty();

            if (!self.check_error_fields([])) {
                self.update_status('error', {'error_messages': {'required_fields':'Missing Required Fields'}});
                return false;
            }

            _.each(this.$target.find('input[type=file]'), function (input) {
                $.each($(input).prop('files'), function (index, file) {
                    self.form_fields.push({
                        name: input.name,
                        value: file
                    });
                });
            });

            _.each(this.form_fields, function (input) {
                if (input.name in form_values) {
                    if (Array.isArray(form_values[input.name])) {
                        form_values[input.name].push(input.value);
                    } else {
                        form_values[input.name] = [form_values[input.name], input.value];
                    }
                } else if (input.value !== '') {
                    form_values[input.name] = input.value;
                }
            });

            ajax.post(this.$target.attr('action'), form_values)
            .then(function (result_data) {
                result_data = $.parseJSON(result_data);
                if (!result_data.id) {
                    // Failure, the server didn't return the created record ID
                    self.update_status('error', result_data);
                    if (result_data.error_fields) {
                        // If the server return a list of bad fields, show these fields for users
                        self.check_error_fields(result_data.error_fields);
                    }
                } else {
                    // Success, redirect or update status
                    var success_page = self.$target.attr('data-success_page');
                    if (success_page) {
                        $(window.location).attr('href', success_page);
                    } else {
                        self.update_status('success', result_data);
                    }
                    // Reset the form
                    self.$target[0].reset();
                }
            })
            .fail(function (result_data){
                self.update_status('error', result_data);
            });
        },
        update_status: function (status, data) {
            var self = this,
                $result = this.$('#o_website_form_result');
            if (status !== 'success') {  // Restore send button behavior if result is an error
                this.$target.find('.btn_upload_attachments').on('click', function (e) {
                    self.send(e);
                });
            }
            var errors = self.wrongMsgXml(data);
            $result.replaceWith('<div class="alert-danger mt16" id="o_website_form_result">'+errors+'</div>');
        },

        check_error_fields: function(error_fields) {
            var self = this;
            var form_valid = true;
            // Loop on all fields
            this.$target.find('.form-field').each(function(k, field){
                var $field = $(field);
                var field_name = $field.find('.control-label').attr('for');

                // Validate inputs for this field
                var inputs = $field.find('.o_website_form_input:not(#editable_select)');
                var invalid_inputs = inputs.toArray().filter(function(input, k, inputs) {
                    // Special check for multiple required checkbox for same
                    // field as it seems checkValidity forces every required
                    // checkbox to be checked, instead of looking at other
                    // checkboxes with the same name and only requiring one
                    // of them to be checked.
                    if (input.required && input.type === 'checkbox') {
                        // Considering we are currently processing a single
                        // field, we can assume that all checkboxes in the
                        // inputs variable have the same name
                        var checkboxes = _.filter(inputs, function(input){
                            return input.required && input.type === 'checkbox';
                        });
                        return !_.any(checkboxes, function(checkbox) {
                            return checkbox.checked;
                        });

                    // Special cases for dates and datetimes
                    } else if ($(input).hasClass('o_website_form_date')) {
                        return !self.is_datetime_valid(input.value, 'date');
                    } else if ($(input).hasClass('o_website_form_datetime')) {
                        return !self.is_datetime_valid(input.value, 'datetime');

                    }
                    return !input.checkValidity();
                });

                // Update field color if invalid or erroneous
                $field.removeClass('has-error');
                if(invalid_inputs.length || error_fields.indexOf(field_name) >= 0){
                    $field.addClass('has-error');
                    form_valid = false;
                }
            });
            return form_valid;
        },

        wrongMsgXml: function(errorData){
            /* Prepares the message to the xml errors */
            var errorMessages = '';
            var wrongFiles = errorData.error_messages.wrongfiles;
            // Wrong files are in the form:
            // {'file_name1': {'error_code1': error_values, ...}, ...}
            // so we put all errors from all files into a single object
            var allErrors = _.values(wrongFiles).reduce(function (errors, errsFile){
                _.assign(errors, errsFile);
                return errors;
            }, {});
            $.each(allErrors, function(ikey, val){
                if(ikey === 'xml64'){
                    // This is not an error, so we ignore it by skipping the iteration
                    return true;
                }else if(ikey === 'supplier'){
                    errorMessages += _t('<div><span level="1">The XML Supplier</span> was not found: <span level="2">') + val + '</span>.</div>';
                }else if(ikey === 'rfc'){
                    errorMessages += _t('<div><span level="1">The XML Receptor RFC</span> does not match with <span level="1">your Company RFC</span>: ') +
                        _t('XML Receptor RFC: <span level="2">') + val[0] + _t(', </span> Your Company RFC: <span level="2">') + val[1] + '</span></div>';
                }else if(ikey === 'currency'){
                    errorMessages += _t('<div><span level="1">The XML Currency</span> <span level="2">') + val + _t('</span> was not found or is disabled.</div>');
                }else if(ikey === 'taxes'){
                    errorMessages += _t('<div><span level="1">Some taxes</span> do not exist for purchases: <span level="2">') + val.join(', ') + '</span>.</div>';
                }else if(ikey === 'signed'){
                    errorMessages += _t('<div><span level="1">UUID</span> not found in the XML.</div>');
                }else if(ikey === 'cancel'){
                    errorMessages += _t('<div><span level="1">The XML state</span> is CANCELED in the SAT system.</div>');
                }else if(ikey === 'discount'){
                    errorMessages += _t('<div><span level="1">Unable to generate invoices with discounts from an XML with version 3.2.</span>You can create the invoice manually and then attach the xml.</div>');
                }else if(ikey === 'folio'){
                    errorMessages += _t('<div><span level="1">The XML Folio</span> does not match with <span level="1">Supplier Invoice Number</span>: ') +
                        _t('XML Folio: <span level="2">') + val[0] + _t(', </span> Supplier invoice number: <span level="2">') + val[1] + '</span></div>';
                }else if(ikey === 'rfc_supplier'){
                    errorMessages += _t('<div><span level="1">The XML Emitter RFC</span> does not match with <span level="1">Customer RFC</span>: ') +
                        _t('XML Emitter RFC: <span level="2">') + val[0] + _t(', </span> Customer RFC: <span level="2">') + val[1] + '</span></div>';
                }else if(ikey === 'amount'){
                    errorMessages += _t('<div><span level="1">The XML amount total</span> does not match with <span level="1">Invoice total</span>: ') +
                        _t('XML amount total: <span level="2">') + val[0] + _t(', </span> Invoice Total: <span level="2">') + val[1] + '</span></div>';
                }else if(ikey === 'uuid_duplicate'){
                    errorMessages += _t('<div><span level="1">The XML UUID</span> belongs to other invoice. <span level="1">UUID: </span>') + val +'</div>';
                }else if(ikey === 'reference'){
                    errorMessages += _t('<div><span level="1">The invoice reference</span> belongs to other invoice of the same partner. <span level="1">Partner: </span>') + val[0] + _t('<span level="1"> Reference: </span>') + val[1] +'</div>';
                }else if(ikey === 'cfdi_version'){
                    errorMessages += _t('<div><span level="1">XML CFDI Version different than 3.3</span></div>');
                }else if(ikey === 'required_fields'){
                    errorMessages += _t('<div><span level="1">Missing Required Fields</span></div>');
                }else if(ikey === 'nothing'){
                    errorMessages += _t('<div><strong>Info!</strong> XML data could not be read correctly.</div>');
                }else{
                    errorMessages += _t('<div><span level="1">Unknown error: </span>') + ikey + '</div>';
                }
            });
            return [errorMessages];
        },
    });
});
