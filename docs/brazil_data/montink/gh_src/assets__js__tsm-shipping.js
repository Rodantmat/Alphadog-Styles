/**
 * Product-page Montink shipping calculator.
 *
 * Queries the Montink API through the plugin REST endpoint (tsm/v1/shipping)
 * and renders the delivery options (price + delivery time) without relying on
 * the AJAX endpoints blocked by the WAF.
 */
(function ($) {
    'use strict';

    $(function () {
        var $box = $('#tsm-shipping-calculator');
        if (!$box.length || typeof tsmShipping === 'undefined') {
            return;
        }

        var $input = $('#tsm-cep-input', $box);
        var $button = $('#tsm-cep-button', $box);
        var $result = $('#tsm-shipping-result', $box);

        // Simple CEP mask: 00000-000
        $input.on('input', function () {
            var digits = this.value.replace(/\D/g, '').slice(0, 8);
            var formatted = digits;
            if (digits.length > 5) {
                formatted = digits.slice(0, 5) + '-' + digits.slice(5);
            }
            this.value = formatted;
        });

        $button.on('click', function () {
            var cep = $input.val().replace(/\D/g, '');
            if (cep.length !== 8) {
                setError(tsmShipping.labels.error);
                return;
            }
            quote(cep);
        });

        $input.on('keydown', function (e) {
            if (e.which === 13) {
                e.preventDefault();
                $button.trigger('click');
            }
        });

        function quote(cep) {
            var qty = 1;
            var $qty = $('.quantity .qty:visible');
            if ($qty.length) {
                var v = parseInt($qty.val(), 10);
                if (!isNaN(v) && v > 0) {
                    qty = v;
                }
            }

            $result.show().html('<p class="tsm-shipping-loading">' + tsmShipping.labels.loading + '</p>');
            $button.prop('disabled', true);

            $.getJSON(tsmShipping.endpoint, { cep: cep, qty: qty })
                .done(function (res) {
                    if (!res.success || !res.options || !res.options.length) {
                        setError(res.msg || tsmShipping.labels.error);
                        return;
                    }
                    var rows = '';
                    $.each(res.options, function (i, opt) {
                        var time = opt.business_days
                            ? '<span class="tsm-shipping-days">' + opt.business_days + ' ' + tsmShipping.labels.days + '</span>'
                            : '';
                        rows += '<div class="tsm-shipping-option">'
                            + '<span class="tsm-shipping-name">' + opt.name + '</span>'
                            + '<span class="tsm-shipping-value">' + opt.value_fmt + '</span>'
                            + time
                            + '</div>';
                    });
                    $result.html(rows).addClass('tsm-shipping-ok');
                })
                .fail(function () {
                    setError(tsmShipping.labels.error);
                })
                .always(function () {
                    $button.prop('disabled', false);
                });
        }

        function setError(msg) {
            $result.removeClass('tsm-shipping-ok')
                .html('<p class="tsm-shipping-error">' + msg + '</p>')
                .show();
        }
    });
})(jQuery);