<?php
/**
 * WooCommerce global product attribute helpers.
 *
 * Ensures global attributes (Modelo/Tamanho/Cor) and their terms exist,
 * and provides helpers to convert a product to variable and attach attributes.
 *
 * @package Tshirtness_Montink
 */

defined( 'ABSPATH' ) || exit;

final class TSM_Attributes {

	/** Attribute label => slug (WooCommerce attribute name). */
	const MAP = [
		'Modelo'  => 'modelo',
		'Tamanho' => 'tamanho',
		'Cor'     => 'cor',
	];

	/**
	 * Ensure the global attributes exist (pa_modelo, pa_tamanho, pa_cor).
	 */
	public static function ensure_attributes(): void {
		if ( ! function_exists( 'wc_create_attribute' ) || ! function_exists( 'wc_get_attribute_taxonomies' ) ) {
			return;
		}

		$existing = wc_get_attribute_taxonomies();
		$slugs    = [];
		foreach ( $existing as $tax ) {
			$slugs[] = $tax->attribute_name;
		}

		foreach ( self::MAP as $label => $slug ) {
			if ( ! in_array( $slug, $slugs, true ) ) {
				wc_create_attribute( [
					'name'         => $label,
					'slug'         => $slug,
					'type'         => 'select',
					'order_by'     => 'menu_order',
					'has_archives' => false,
				] );
			}
		}

		// Re-register taxonomies so pa_* are active for term creation.
		if ( function_exists( 'WC' ) && isset( WC()->attributes ) ) {
			WC()->attributes->init_taxonomies();
		}

		// Robust fallback: register any pa_ taxonomy that is still missing.
		foreach ( array_values( self::MAP ) as $slug ) {
			$taxonomy = self::taxonomy( $slug );
			if ( taxonomy_exists( $taxonomy ) ) {
				continue;
			}
			register_taxonomy(
				$taxonomy,
				[ 'product', 'product_variation' ],
				[
					'public'            => false,
					'show_ui'           => false,
					'show_in_nav_menus' => false,
					'show_in_rest'      => true,
					'hierarchical'      => false,
					'rewrite'           => false,
					'query_var'         => false,
				]
			);
		}
	}

	/**
	 * Get the pa_ taxonomy name for a given attribute slug.
	 */
	public static function taxonomy( string $slug ): string {
		return wc_attribute_taxonomy_name( $slug );
	}

	/**
	 * Ensure a term exists inside a pa_ taxonomy and return its term id (or 0).
	 */
	public static function ensure_term( string $taxonomy, string $name ): int {
		if ( ! taxonomy_exists( $taxonomy ) ) {
			return 0;
		}

		$existing = get_term_by( 'name', $name, $taxonomy );
		if ( $existing && ! is_wp_error( $existing ) ) {
			return (int) $existing->term_id;
		}

		$created = wp_insert_term( $name, $taxonomy );
		if ( is_wp_error( $created ) ) {
			return 0;
		}

		return (int) $created['term_id'];
	}

	/**
	 * Ensure a term exists and return its slug.
	 */
	public static function ensure_term_slug( string $taxonomy, string $name ): string {
		$id = self::ensure_term( $taxonomy, $name );
		if ( ! $id ) {
			return sanitize_title( $name );
		}
		$t = get_term( $id, $taxonomy );
		return $t && ! is_wp_error( $t ) ? $t->slug : sanitize_title( $name );
	}

	/**
	 * Convert a product to "variable" (if needed) and attach global variation
	 * attributes. Returns the WC_Product_Variable or a WP_Error.
	 *
	 * Attributes are persisted directly to the _product_attributes meta (the
	 * real storage format) because WC_Product::set_attributes() is unreliable
	 * on some hosts.
	 *
	 * @param int   $product_id
	 * @param array $attrs  Attribute slug => array of term names.
	 *
	 * @return WC_Product_Variable|WP_Error
	 */
	public static function ensure_variable( int $product_id, array $attrs ) {
		$product = wc_get_product( $product_id );
		if ( ! $product ) {
			return new WP_Error( 'tsm_no_product', __( 'Produto não encontrado.', 'tshirtness-montink' ) );
		}

		// Convert simple -> variable using the canonical product-type term swap.
		if ( 'variable' !== $product->get_type() ) {
			wp_set_object_terms( $product_id, 'variable', 'product_type' );
			clean_post_cache( $product_id );
			wc_delete_product_transients( $product_id );

			$product = wc_get_product( $product_id );
			if ( ! $product || 'variable' !== $product->get_type() ) {
				return new WP_Error( 'tsm_convert', __( 'Falha ao converter o produto para variável.', 'tshirtness-montink' ) );
			}
		}

		// Build and persist the _product_attributes meta directly.
		$attributes = [];
		$pos        = 0;
		foreach ( $attrs as $attr_slug => $terms ) {
			$taxonomy = self::taxonomy( $attr_slug );
			$term_ids = [];
			foreach ( $terms as $term_name ) {
				$id = self::ensure_term( $taxonomy, (string) $term_name );
				if ( $id ) {
					$term_ids[] = $id;
				}
			}

			// Attach the terms to the product so the front-end dropdowns (and
			// REST options) reflect every option — same as WC REST does.
			if ( $term_ids ) {
				wp_set_object_terms( $product_id, $term_ids, $taxonomy );
			}

			$attributes[ $taxonomy ] = [
				'name'         => $taxonomy,
				'value'        => $term_ids ? implode( ' ', $term_ids ) : '',
				'position'     => $pos,
				'is_visible'   => 1,
				'is_variation' => 1,
				'is_taxonomy'  => 1,
			];
			$pos++;
		}

		// Persist directly to meta (bypassing set_attributes()).
		update_post_meta( $product_id, '_product_attributes', $attributes );
		wc_delete_product_transients( $product_id );

		return wc_get_product( $product_id );
	}

	/**
	 * Create (or update) a variation with the given term slugs and price.
	 *
	 * Attributes are persisted directly as attribute_pa_* post meta (the real
	 * storage format), bypassing the unreliable WC_Product_Variation::set_attributes().
	 *
	 * @return int|WP_Error Variation id.
	 */
	public static function create_variation( int $product_id, array $attr_slugs, string $price, int $existing_id = 0 ) {
		if ( $existing_id ) {
			$variation = wc_get_product( $existing_id );
		} else {
			$variation = new WC_Product_Variation();
			$variation->set_parent_id( $product_id );
		}

		if ( ! $variation ) {
			return new WP_Error( 'tsm_no_variation', __( 'Variação não encontrada.', 'tshirtness-montink' ) );
		}

		$variation->set_status( 'publish' );
		$variation->set_regular_price( $price );
		$variation->set_manage_stock( false );
		$variation->save();

		$variation_id = $variation->get_id();
		if ( ! $variation_id ) {
			return new WP_Error( 'tsm_no_variation_id', __( 'Falha ao criar a variação.', 'tshirtness-montink' ) );
		}

		// Persist variation attributes as attribute_pa_* post meta.
		foreach ( $attr_slugs as $taxonomy => $slug ) {
			update_post_meta( $variation_id, 'attribute_' . $taxonomy, $slug );
		}

		// Re-read so the WC object reflects the attributes.
		wc_delete_product_transients( $product_id );
		clean_post_cache( $variation_id );

		return $variation_id;
	}
}
