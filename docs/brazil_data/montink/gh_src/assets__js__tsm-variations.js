/**
 * Tshirtness Montink — filter Tamanho/Cor dropdowns based on the selected
 * Modelo, so e.g. quadro sizes (20x30) never appear when a t-shirt is chosen.
 *
 * Works with the variations JSON embedded in the form (data-product_variations),
 * so it functions even when the server blocks the get_variations AJAX call.
 */
(function ($) {
	'use strict';

	var MODELO_ATTR = 'pa_modelo';
	var TAMANHO_ATTR = 'pa_tamanho';
	var COR_ATTR = 'pa_cor';

	$(function () {
		$(document).on('wc_variation_form', '.variations_form', function () {
			tsmFilterAttributes($(this));
		});

		$(document).on('change', '.variations_form select[data-attribute_name^="attribute_pa_modelo"]', function () {
			var $form = $(this).closest('.variations_form');
			// Reset dependent selects so stale values (e.g. a quadro size) never
			// persist after switching models.
			var $tamanho = $form.find('select[data-attribute_name="attribute_pa_tamanho"]');
			var $cor = $form.find('select[data-attribute_name="attribute_pa_cor"]');
			$tamanho.val('');
			$cor.val('');
			$tamanho.trigger('change');
			$cor.trigger('change');
			tsmFilterAttributes($form);
		});

		$(document).on('reset_data', '.variations_form', function () {
			tsmFilterAttributes($(this), true);
		});
	});

	function tsmFilterAttributes($form, reset) {
		var raw = $form.attr('data-product_variations');
		if (!raw || raw === 'false') {
			return;
		}

		var variations;
		try {
			variations = JSON.parse(raw);
		} catch (err) {
			return;
		}
		if (!variations || !variations.length) {
			return;
		}

		var $modeloSelect = $form.find('select[data-attribute_name="attribute_pa_modelo"]');
		var $tamanhoSelect = $form.find('select[data-attribute_name="attribute_pa_tamanho"]');
		var $corSelect = $form.find('select[data-attribute_name="attribute_pa_cor"]');
		var modeloVal = $modeloSelect.val();

		// No model chosen yet — restore all options.
		if (reset || !modeloVal) {
			$tamanhoSelect.find('option').show();
			$corSelect.find('option').show();
			return;
		}

		var tamanhos = {};
		var cores = {};

		variations.forEach(function (v) {
			var attrs = tsmNormalizeAttributes(v.attributes);
			if (attrs[MODELO_ATTR] !== modeloVal) {
				return;
			}
			if (attrs[TAMANHO_ATTR]) {
				tamanhos[attrs[TAMANHO_ATTR]] = true;
			}
			if (attrs[COR_ATTR]) {
				cores[attrs[COR_ATTR]] = true;
			}
		});

		filterOptions($tamanhoSelect, tamanhos, reset);
		filterOptions($corSelect, cores, reset);
	}

	/**
	 * Normalize variation attributes into a taxonomy-slug => value map.
	 * The embedded variations JSON uses { pa_modelo: "t-shirt-quality" } while
	 * the Store API uses [{ name: "Modelo", value: "..." }] — handle both.
	 */
	function tsmNormalizeAttributes(attributes) {
		var out = {};
		if (!attributes) {
			return out;
		}
		if ($.isArray(attributes)) {
			attributes.forEach(function (a) {
				var key = a.slug || a.name || '';
				out[key] = a.value || a.option || '';
			});
			return out;
		}
		if (typeof attributes === 'object') {
			$.each(attributes, function (key, value) {
				out[key] = value;
			});
		}
		return out;
	}

	function filterOptions($select, allowed, reset) {
		$select.find('option').each(function () {
			var $opt = $(this);
			var val = $opt.val();
			// Always keep the empty "Escolha uma opção" placeholder.
			if (val === '') {
				$opt.show();
				return;
			}
			if (reset || allowed[val]) {
				$opt.show();
			} else {
				$opt.hide();
			}
		});
	}
})(jQuery);