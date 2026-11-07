<?php
/**
 * Montink catalogue sync + WooCommerce cross-reference & variation creation.
 *
 * Aggregates Montink products by display name, cross-references them against
 * WooCommerce products, creates the WooCommerce product when missing, converts
 * it to a variable product and creates any missing variations (Modelo x Tamanho x Cor),
 * each linked to the correct Montink product_id.
 *
 * @package Tshirtness_Montink
 */

defined( 'ABSPATH' ) || exit;

final class TSM_Sync {

	const ACTION    = 'tsm_run_sync';
	const TRANSIENT = 'tsm_sync_result';

	/** Option key that stores the in-progress (chunked) sync state. */
	const STATE_OPTION = 'tsm_sync_state';

	/** Meta key on attachments linking them to their Montink source URL. */
	const META_SOURCE_URL = '_tsm_montink_source_url';

	/** Meta key storing Montink product_ids linked to a WooCommerce product. */
	const META_LINK = '_tsm_montink_product_ids';

	/** Meta key on each variation with the Montink base product_id. */
	const META_VAR_PRODUCT_ID = '_tsm_montink_product_id';

	/** Meta key on each variation with the Montink product id (app_order_products). */
	const META_VAR_SKU = '_tsm_montink_product_sku';

	/** Meta key with the Montink image URL (referenced, not downloaded). */
	const META_IMAGE_URL = '_tsm_montink_image_url';

	public function register(): void {
		add_action( 'admin_post_' . self::ACTION, [ $this, 'handle_run_sync' ] );
		add_action( 'init', [ $this, 'register_meta' ] );
		add_filter( 'woocommerce_product_get_image', [ $this, 'product_image_url' ], 10, 5 );
		add_filter( 'woocommerce_product_get_image_id', [ $this, 'product_image_id' ], 10, 2 );

		// Embed all variations in the page (no AJAX), so the native Modelo →
		// Tamanho/Cor dropdown filtering works even when the server's AJAX
		// endpoint is blocked by the WAF.
		add_filter( 'woocommerce_ajax_variation_threshold', [ $this, 'variation_threshold' ], 99 );

		add_action( 'wp_enqueue_scripts', [ $this, 'enqueue_scripts' ] );
	}

	/**
	 * Enqueue the Modelo → Tamanho/Cor dropdown filter on single products.
	 */
	public function enqueue_scripts(): void {
		if ( ! is_product() ) {
			return;
		}
		wp_enqueue_script(
			'tsm-variations',
			TSM_URL . 'assets/js/tsm-variations.js',
			[ 'jquery', 'wc-add-to-cart-variation' ],
			TSM_VERSION,
			true
		);
	}

	/**
	 * Raise the WooCommerce threshold so variations are embedded in the
	 * variations form instead of being lazy-loaded via ?wc-ajax=get_variations.
	 */
	public function variation_threshold(): int {
		return 500;
	}

	public function register_meta(): void {
		register_post_meta( 'product', self::META_LINK, [
			'type'          => 'array',
			'single'        => true,
			'show_in_rest'  => false,
			'auth_callback' => static fn() => current_user_can( 'manage_woocommerce' ),
		] );
		register_post_meta( 'product_variation', self::META_VAR_PRODUCT_ID, [
			'type'         => 'string',
			'single'       => true,
			'show_in_rest' => false,
		] );
		register_post_meta( 'product_variation', self::META_VAR_SKU, [
			'type'         => 'string',
			'single'       => true,
			'show_in_rest' => false,
		] );
		register_post_meta( 'product_variation', self::META_IMAGE_URL, [
			'type'         => 'string',
			'single'       => true,
			'show_in_rest' => false,
		] );
	}

	/**
	 * Render the Montink image URL (no download) for products/variations that
	 * carry the _tsm_montink_image_url meta.
	 */
	public function product_image_url( $image, $product, $size, $attr, $placeholder ) {
		if ( $image ) {
			return $image;
		}
		$url = $product ? (string) $product->get_meta( self::META_IMAGE_URL ) : '';
		if ( '' === $url ) {
			return $image;
		}
		$alt = $product ? esc_attr( $product->get_name() ) : '';
		return '<img src="' . esc_url( $url ) . '" alt="' . esc_attr( $alt ) . '" ' . ( is_array( $attr ) ? wc_implode_html_attributes( $attr ) : $attr ) . '>';
	}

	/**
	 * Keep get_image_id() returning false so the URL filter takes over.
	 */
	public function product_image_id( $image_id, $product ) {
		return $image_id;
	}

	public function handle_run_sync(): void {
		if ( ! current_user_can( 'manage_woocommerce' ) ) {
			wp_die( esc_html__( 'Permissão negada.', 'tshirtness-montink' ) );
		}
		check_admin_referer( self::ACTION );

		// Kick off a chunked sync: the sync page will poll itself and run one
		// bounded chunk per request, avoiding nginx/PHP timeouts.
		$this->start_sync();

		wp_safe_redirect(
			add_query_arg(
				[ 'page' => TSM_Settings::SYNC_SLUG, 'run' => '1' ],
				admin_url( 'admin.php' )
			)
		);
		exit;
	}

	/**
	 * Initialise the chunked sync state.
	 */
	private function start_sync(): void {
		$state = [
			'step'           => 'prepare',
			'montink'        => [],
			'by_name'        => [],
			'woo_by_name'    => [],
			'groups'         => [],
			'group_keys'     => [],
			'index'          => 0,
			'errors'         => [],
			'created_products' => [],
			'created_variations' => 0,
			'total_units'    => 0,
			'done_units'     => 0,
			'timestamp'      => time(),
		];
		update_option( self::STATE_OPTION, $state, false );
		delete_transient( self::TRANSIENT );
	}

	/**
	 * Run the current chunk and persist progress. Each call does a bounded
	 * amount of work so it stays well under server timeouts.
	 *
	 * @return array{progress:int,done:bool,step:string,label:string}
	 */
	private function run_chunk(): array {
		$state = get_option( self::STATE_OPTION, [] );
		if ( empty( $state ) || empty( $state['step'] ) ) {
			return [ 'progress' => 100, 'done' => true, 'step' => 'done', 'label' => '' ];
		}

		// Safety: give this chunk more room to breathe.
		@set_time_limit( 90 ); // phpcs:ignore

		$step = $state['step'];

		switch ( $step ) {
			case 'prepare':
				$state = $this->chunk_prepare( $state );
				break;
			case 'catalog':
				$state = $this->chunk_catalog( $state );
				break;
			case 'variations':
				$state = $this->chunk_variations( $state );
				break;
			case 'done':
				break;
		}

		$progress = $this->progress( $state );
		$done     = 'done' === $state['step'];

		if ( $done ) {
			$this->store_result( $state );
			delete_option( self::STATE_OPTION );
		} else {
			update_option( self::STATE_OPTION, $state, false );
		}

		return [
			'progress' => $progress,
			'done'     => $done,
			'step'     => $state['step'],
			'label'    => $this->step_label( $state ),
		];
	}

	/**
	 * Chunk "prepare": fetch the Montink catalogue and the WooCommerce product
	 * map, then group Montink products by name.
	 */
	private function chunk_prepare( array $state ): array {
		TSM_Attributes::ensure_attributes();
		$this->cleanup_orphans();

		$montink = TSM_API::get_products();
		if ( is_wp_error( $montink ) ) {
			$state['errors'][] = $montink->get_error_message();
			$state['step']     = 'done';
			return $state;
		}

		$state['montink']     = $montink;
		$state['woo_by_name'] = $this->get_woo_products_by_name();

		// Group by normalized display name.
		$by_name = [];
		foreach ( $montink as $p ) {
			$name = isset( $p['nomeShopify'] ) ? (string) $p['nomeShopify'] : '';
			$key  = self::normalize( $name );
			if ( '' === $key ) {
				continue;
			}
			if ( ! isset( $by_name[ $key ] ) ) {
				$by_name[ $key ] = [ 'name' => $name, 'products' => [] ];
			}
			$by_name[ $key ]['products'][] = $p;
		}

		$state['by_name']    = $by_name;
		$state['group_keys'] = array_keys( $by_name );
		$state['groups']     = [];
		foreach ( $by_name as $key => $g ) {
			$state['groups'][ $key ] = [
				'name'      => $g['name'],
				'woo_id'    => isset( $state['woo_by_name'][ $key ] ) ? $state['woo_by_name'][ $key ]['id'] : null,
				'variants'  => [],
				'created'   => false,
				'variations_added' => 0,
				'errors'    => [],
			];
		}

		$state['step']       = 'catalog';
		$state['index']      = 0;
		$state['total_units'] = count( $state['montink'] );
		$state['done_units']  = 0;

		return $state;
	}

	/**
	 * Chunk "catalog": fetch details for ONE Montink product, parse it into a
	 * variant, download its images and append it to the right group.
	 */
	private function chunk_catalog( array $state ): array {
		if ( $state['index'] >= count( $state['montink'] ) ) {
			$state['step']  = 'variations';
			$state['index'] = 0;
			$state['total_units'] = count( $state['group_keys'] );
			$state['done_units']  = 0;
			return $state;
		}

		$p       = $state['montink'][ $state['index'] ];
		$key     = self::normalize( (string) ( $p['nomeShopify'] ?? '' ) );
		$detail  = TSM_API::get_product( (string) $p['id'] );

		if ( is_wp_error( $detail ) ) {
			$state['errors'][] = $detail->get_error_message();
		} else {
			$variant = $this->parse_variant( $detail );
			if ( $variant ) {
				$this->download_variant_images( $variant );
				$state['groups'][ $key ]['variants'][] = $variant;
			} else {
				$state['groups'][ $key ]['errors'][] = sprintf(
					/* translators: %s: Montink product id. */
					__( 'Sem variante válida (produto #%s).', 'tshirtness-montink' ),
					$p['id']
				);
			}
		}

		$state['index']++;
		$state['done_units']++;

		return $state;
	}

	/**
	 * Chunk "variations": create/update the WooCommerce product and variations
	 * for ONE group.
	 */
	private function chunk_variations( array $state ): array {
		if ( $state['index'] >= count( $state['group_keys'] ) ) {
			// Build the "missing in Montink" list, then finish.
			$by_name = $state['by_name'];
			$missing = [];
			foreach ( $state['woo_by_name'] as $key => $wp ) {
				if ( ! isset( $by_name[ $key ] ) ) {
					$missing[] = $wp;
				}
			}
			$state['missing_in_montink'] = $missing;
			$state['step']               = 'done';
			return $state;
		}

		$key        = $state['group_keys'][ $state['index'] ];
		$group      = &$state['groups'][ $key ];
		$variants   = $group['variants'];

		if ( empty( $variants ) ) {
			if ( empty( $group['errors'] ) ) {
				$group['errors'][] = __( 'Nenhuma variante válida na Montink.', 'tshirtness-montink' );
			}
		} else {
			// Resolve (or create) the WooCommerce product.
			$product_id = $group['woo_id'] ? (int) $group['woo_id'] : 0;
			if ( ! $product_id ) {
				$product_id = $this->create_product( $group['name'] );
				if ( is_wp_error( $product_id ) ) {
					$group['errors'][] = $product_id->get_error_message();
				} else {
					$group['created'] = true;
					$state['created_products'][] = $group['name'];
				}
			}

			if ( ! is_wp_error( $product_id ) && $product_id ) {
				$group['woo_id'] = $product_id;

				// Save the linked Montink product_ids on the product.
				$linked = [];
				foreach ( $variants as $v ) {
					$linked[] = $v['product_id'];
				}
				update_post_meta( $product_id, self::META_LINK, array_values( array_unique( $linked ) ) );

				// Create variations.
				$added = $this->sync_variations( $product_id, $variants, $group['errors'] );
				$group['variations_added'] = $added;
				$state['created_variations'] += $added;
			}
		}

		$state['index']++;
		$state['done_units']++;

		return $state;
	}

	/**
	 * Compute a 0-100 progress value for the current state.
	 */
	private function progress( array $state ): int {
		$step = $state['step'];

		if ( 'prepare' === $step ) {
			return 1;
		}
		if ( 'catalog' === $step ) {
			$total = max( 1, (int) $state['total_units'] );
			return (int) floor( 1 + ( $state['done_units'] / $total ) * 60 );
		}
		if ( 'variations' === $step ) {
			$total = max( 1, (int) $state['total_units'] );
			return (int) floor( 61 + ( $state['done_units'] / $total ) * 38 );
		}
		return 100;
	}

	/**
	 * Human label for the current step (shown next to the progress bar).
	 */
	private function step_label( array $state ): string {
		switch ( $state['step'] ) {
			case 'prepare':
				return __( 'Preparando…', 'tshirtness-montink' );
			case 'catalog':
				return sprintf(
					/* translators: %1$d: done, %2$d: total. */
					__( 'Importando modelos e imagens %1$d/%2$d', 'tshirtness-montink' ),
					$state['done_units'],
					max( 1, (int) $state['total_units'] )
				);
			case 'variations':
				return sprintf(
					/* translators: %1$d: done, %2$d: total. */
					__( 'Criando variações %1$d/%2$d', 'tshirtness-montink' ),
					$state['done_units'],
					max( 1, (int) $state['total_units'] )
				);
			case 'done':
				return __( 'Concluído', 'tshirtness-montink' );
			default:
				return '';
		}
	}

	/**
	 * Persist the final report as a transient so the sync page can render it.
	 */
	private function store_result( array $state ): void {
		$out = [
			'timestamp'          => $state['timestamp'],
			'groups'             => array_values( $state['groups'] ),
			'created_products'   => $state['created_products'],
			'created_variations' => $state['created_variations'],
			'missing_in_montink' => $state['missing_in_montink'] ?? [],
			'errors'             => $state['errors'],
		];
		set_transient( self::TRANSIENT, $out, HOUR_IN_SECONDS );
	}

	/**
	 * Run the full sync.
	 *
	 * @return array Sync report.
	 */
	/**
	 * Parse a Montink product detail into a structured variant.
	 */
	private function parse_variant( array $detail ): ?array {
		$dp = isset( $detail['dadosProduto'] ) && is_array( $detail['dadosProduto'] ) ? $detail['dadosProduto'] : [];
		if ( empty( $dp ) ) {
			return null;
		}

		$model     = isset( $dp['product_name'] ) ? (string) $dp['product_name'] : '';
		$product_id = isset( $dp['product_id'] ) ? (string) $dp['product_id'] : '';
		$sku       = isset( $dp['id'] ) ? (string) $dp['id'] : '';

		$sizes  = $this->decode_map( $dp['tamanhos'] ?? '' );
		$colors = $this->decode_map( $dp['cores'] ?? '' );

		if ( '' === $model || '' === $product_id || empty( $sizes ) ) {
			return null;
		}

		// Price add-ons per size (Montink precosAdicionais), e.g. {"XGG": 3.30}.
		$size_extra = [];
		if ( isset( $dp['precosAdicionais'] ) && is_array( $dp['precosAdicionais'] ) ) {
			foreach ( $dp['precosAdicionais'] as $sz => $val ) {
				$size_extra[ (string) $sz ] = (float) $val;
			}
		}

		// Primary image URL (downloaded into the media library during sync).
		$image_url = '';
		$imgs      = isset( $detail['imagens'] ) && is_array( $detail['imagens'] ) ? $detail['imagens'] : [];
		foreach ( $imgs as $im ) {
			$url = is_array( $im ) ? ( $im['url'] ?? '' ) : '';
			if ( $url ) {
				$image_url = (string) $url;
				break;
			}
		}

		// Per-color mockups, e.g. {"Preto":"https://r2.mont.ink/...","Branco":"https://r2.mont.ink/..."}.
		$color_images = [];
		$iv           = isset( $dp['imgVariacoes'] ) ? $dp['imgVariacoes'] : '';
		if ( is_array( $iv ) ) {
			$color_images = $iv;
		} elseif ( is_string( $iv ) && '' !== $iv ) {
			$decoded = json_decode( $iv, true );
			if ( is_array( $decoded ) ) {
				$color_images = $decoded;
			}
		}
		// Fallback: fill missing colors with the primary image.
		foreach ( $colors as $color ) {
			if ( ! isset( $color_images[ $color ] ) ) {
				$color_images[ $color ] = $image_url;
			}
		}

		return [
			'model'        => $model,
			'product_id'   => $product_id,
			'sku'          => $sku,
			'price'        => isset( $dp['preco_final'] ) ? (string) $dp['preco_final'] : '',
			'sizes'        => $sizes,
			'colors'       => $colors,
			'size_extra'   => $size_extra,
			'image_url'    => $image_url,
			'color_images' => $color_images,
		];
	}

	/**
	 * Download a remote image into the media library. Caches by URL for the
	 * current request and reuses any attachment already linked to the same
	 * Montink source URL (so re-syncs never re-download).
	 *
	 * @return int Attachment id (0 on failure).
	 */
	private function download_image( string $url ): int {
		static $cache = [];

		if ( isset( $cache[ $url ] ) ) {
			return $cache[ $url ];
		}

		if ( '' === $url ) {
			$cache[ $url ] = 0;
			return 0;
		}

		// Reuse an attachment imported for this exact Montink URL in a previous run.
		$existing = get_posts( [
			'post_type'      => 'attachment',
			'post_status'    => 'inherit',
			'posts_per_page' => 1,
			'fields'         => 'ids',
			'meta_key'       => self::META_SOURCE_URL,
			'meta_value'     => $url,
		] );
		if ( ! empty( $existing ) ) {
			$cache[ $url ] = (int) $existing[0];
			return (int) $existing[0];
		}

		if ( ! function_exists( 'media_sideload_image' ) ) {
			require_once ABSPATH . 'wp-admin/includes/media.php';
			require_once ABSPATH . 'wp-admin/includes/file.php';
			require_once ABSPATH . 'wp-admin/includes/image.php';
		}

		$att_id = media_sideload_image( $url, 0, null, 'id' );
		if ( is_wp_error( $att_id ) ) {
			$cache[ $url ] = 0;
			return 0;
		}

		$att_id = (int) $att_id;
		update_post_meta( $att_id, self::META_SOURCE_URL, $url );

		$cache[ $url ] = $att_id;
		return $att_id;
	}

	/**
	 * Download the model mockup and every per-color mockup of a variant,
	 * storing the resulting attachment ids on the variant so sync_variations()
	 * can attach them without further network calls.
	 */
	private function download_variant_images( array &$variant ): void {
		$variant['image_id']      = $this->download_image( $variant['image_url'] ?? '' );
		$variant['color_image_ids'] = [];

		foreach ( $variant['colors'] as $color ) {
			$url = $variant['color_images'][ $color ] ?? $variant['image_url'] ?? '';
			$id  = $this->download_image( (string) $url );
			if ( ! $id ) {
				$id = $variant['image_id'];
			}
			$variant['color_image_ids'][ $color ] = $id;
		}
	}

	/**
	 * Decode a Montink JSON map like {"P":"P","M":"M"} into a list of values.
	 */
	private function decode_map( $json ): array {
		if ( is_array( $json ) ) {
			return array_values( $json );
		}
		$decoded = json_decode( (string) $json, true );
		return is_array( $decoded ) ? array_values( $decoded ) : [];
	}

	/**
	 * Create a new variable WooCommerce product from a Montink display name.
	 *
	 * @return int|WP_Error
	 */
	private function create_product( string $name ) {
		$product = new WC_Product_Variable();
		$product->set_name( $name );
		$product->set_status( 'publish' );
		$product->set_catalog_visibility( 'visible' );
		$product->save();

		$id = $product->get_id();
		if ( ! $id ) {
			return new WP_Error( 'tsm_create', __( 'Falha ao criar o produto WooCommerce.', 'tshirtness-montink' ) );
		}
		return $id;
	}

	/**
	 * Convert product to variable, attach attributes, and create missing variations.
	 * Price = base (parent price or first Montink price) + Montink size add-on.
	 */
	private function sync_variations( int $product_id, array $variants, array &$errors ): int {
		$models = [];
		$sizes  = [];
		$colors = [];
		foreach ( $variants as $v ) {
			$models[ $v['model'] ] = true;
			foreach ( $v['sizes'] as $s ) {
				$sizes[ $s ] = true;
			}
			foreach ( $v['colors'] as $c ) {
				$colors[ $c ] = true;
			}
		}

		// Convert to variable + attach global attributes.
		$product = TSM_Attributes::ensure_variable( $product_id, [
			'modelo'  => array_keys( $models ),
			'tamanho' => array_keys( $sizes ),
			'cor'     => array_keys( $colors ),
		] );
		if ( is_wp_error( $product ) ) {
			$errors[] = $product->get_error_message();
			return 0;
		}

		// Build a lookup of size add-ons per model (Montink precosAdicionais).
		$model_size_extra = [];
		foreach ( $variants as $v ) {
			$model_size_extra[ $v['model'] ] = $v['size_extra'];
		}

		// Variations are 100% derived from Montink — rebuild them deterministically
		// each run so duplicates from earlier runs are never left behind.
		foreach ( $product->get_children() as $child_id ) {
			wp_delete_post( $child_id, true );
		}
		wc_delete_product_transients( $product_id );

		$created = 0;

		foreach ( $variants as $v ) {
			// Images were downloaded during the catalog chunk and are available
			// as attachment ids on the variant.
			$model_img_id = $v['image_id'] ?? 0;

			foreach ( $v['colors'] as $color ) {
				$color_img_id = isset( $v['color_image_ids'][ $color ] ) ? (int) $v['color_image_ids'][ $color ] : $model_img_id;
				if ( ! $color_img_id ) {
					$color_img_id = $model_img_id;
				}

				foreach ( $v['sizes'] as $size ) {
					$modelo_slug = sanitize_title( $v['model'] );
					$cor_slug    = sanitize_title( $color );
					$size_slug   = sanitize_title( $size );

					// Price = model's own Montink price + its size add-on.
					$extras = $model_size_extra[ $v['model'] ] ?? [];
					$extra  = isset( $extras[ $size ] ) ? (float) $extras[ $size ] : 0;
					$price  = (float) $v['price'] + $extra;
					$price  = number_format( $price, 2, '.', '' );

					$res = TSM_Attributes::create_variation(
						$product_id,
						[
							'pa_modelo'  => $modelo_slug,
							'pa_tamanho' => $size_slug,
							'pa_cor'     => $cor_slug,
						],
						$price,
						0
					);

					if ( is_wp_error( $res ) ) {
						$errors[] = $res->get_error_message();
						continue;
					}

					$created++;

					if ( $color_img_id ) {
						update_post_meta( $res, '_thumbnail_id', $color_img_id );
					}

					$this->update_variation_meta( $res, $v );
				}
			}
		}

		// Set the parent product image from the first successfully downloaded model mockup.
		$parent_img = (int) $product->get_image_id();
		if ( ! $parent_img ) {
			$first_img = 0;
			foreach ( $variants as $v ) {
				$first_img = (int) ( $v['image_id'] ?? 0 );
				if ( $first_img ) {
					break;
				}
			}
			if ( $first_img ) {
				update_post_meta( $product_id, '_thumbnail_id', $first_img );
			}
		}

		return $created;
	}

	/**
	 * Write Montink linkage meta onto a variation.
	 */
	private function update_variation_meta( int $variation_id, array $variant ): void {
		update_post_meta( $variation_id, self::META_VAR_PRODUCT_ID, $variant['product_id'] );
		update_post_meta( $variation_id, self::META_VAR_SKU, $variant['sku'] );
		if ( ! empty( $variant['image_url'] ) ) {
			update_post_meta( $variation_id, self::META_IMAGE_URL, $variant['image_url'] );
		}
	}

	/**
	 * Fetch published WooCommerce products as normalized-name => {id, sku, name}.
	 */
	private function get_woo_products_by_name(): array {
		$map = [];
		$q   = new WP_Query( [
			'post_type'      => 'product',
			'post_status'    => 'publish',
			'posts_per_page' => -1,
			'fields'         => 'ids',
			'no_found_rows'  => true,
		] );
		foreach ( $q->posts as $pid ) {
			$product = wc_get_product( $pid );
			if ( ! $product ) {
				continue;
			}
			$key = self::normalize( $product->get_name() );
			if ( '' === $key ) {
				continue;
			}
			$map[ $key ] = [
				'id'   => $product->get_id(),
				'name' => $product->get_name(),
				'sku'  => $product->get_sku(),
			];
		}
		return $map;
	}

	/**
	 * Normalize a display name for cross-referencing.
	 * Removes a leading "Camiseta " (and "Camiseta Castro ") so that
	 * "Camiseta Castro 80's: Madonna" and "Castro 80's: Madonna" match.
	 */
	public static function normalize( string $name ): string {
		$s = mb_strtolower( trim( $name ), 'UTF-8' );
		$s = str_replace( [ '’', '‘', '`', '´' ], "'", $s );
		$s = preg_replace( '/[^\p{L}\p{N}\s-]/u', '', $s );
		$s = preg_replace( '/\s+/u', ' ', $s );
		$s = trim( $s );

		// Drop generic leading tokens to make matching tolerant of "Camiseta ".
		$s = preg_replace( '/^(camiseta castro|camiseta)\s+/u', '', $s );
		$s = preg_replace( '/^castro\s+/u', '', $s );

		return trim( $s );
	}

	/**
	 * Remove orphan/inconsistent WooCommerce products produced by earlier buggy
	 * syncs — i.e. posts of type "product" that are not recognized as a valid
	 * WC_Product, and variable products that are not editable (no valid object).
	 */
	private function cleanup_orphans(): void {
		if ( ! function_exists( 'wc_get_product' ) ) {
			return;
		}

		$q = new WP_Query( [
			'post_type'      => 'product',
			'post_status'    => 'any',
			'posts_per_page' => 500,
			'fields'         => 'ids',
			'no_found_rows'  => true,
			'orderby'        => 'ID',
			'order'          => 'ASC',
		] );

		foreach ( $q->posts as $pid ) {
			$product = wc_get_product( $pid );
			if ( $product ) {
				continue;
			}
			// Not a valid WC_Product object → orphan; force delete.
			wp_delete_post( $pid, true );
		}
	}

	/**
	 * Render the sync page.
	 */
	public function render_page(): void {
		$result  = get_transient( self::TRANSIENT );
		$ran     = isset( $_GET['ran'] ) ? sanitize_key( wp_unslash( $_GET['ran'] ) ) : ''; // phpcs:ignore WordPress.Security.NonceVerification.Recommended
		$run     = isset( $_GET['run'] ) ? sanitize_key( wp_unslash( $_GET['run'] ) ) : ''; // phpcs:ignore WordPress.Security.NonceVerification.Recommended
		$running = $this->is_running();

		// Chunked run in progress: process one chunk and auto-refresh the page.
		if ( '1' === $run && $running ) {
			$chunk = $this->run_chunk();
			if ( $chunk['done'] ) {
				wp_safe_redirect(
					add_query_arg(
						[ 'page' => TSM_Settings::SYNC_SLUG, 'ran' => '1' ],
						admin_url( 'admin.php' )
					)
				);
				exit;
			}
			$this->render_progress( $chunk );
			return;
		}

		// No run requested but a run is mid-flight — pick it up.
		if ( $running ) {
			wp_safe_redirect(
				add_query_arg(
					[ 'page' => TSM_Settings::SYNC_SLUG, 'run' => '1' ],
					admin_url( 'admin.php' )
				)
			);
			exit;
		}

		$run_url = wp_nonce_url( admin_url( 'admin-post.php?action=' . self::ACTION ), self::ACTION );
		?>
		<div class="wrap">
			<h1><?php echo esc_html__( 'Sincronização Montink', 'tshirtness-montink' ); ?></h1>
			<p><?php echo esc_html__( 'Importa o catálogo da Montink, agrupa por estampa, cria produtos/variacões no WooCommerce e sinaliza o que falta.', 'tshirtness-montink' ); ?></p>
			<p>
				<a class="button button-primary" href="<?php echo esc_url( $run_url ); ?>">
					<?php echo esc_html__( 'Executar sincronização', 'tshirtness-montink' ); ?>
				</a>
			</p>

			<?php if ( '1' === $ran && ! $result ) : ?>
				<div class="notice notice-error"><p><?php echo esc_html__( 'Nenhum resultado salvo. Verifique o token em Montink → Configurações.', 'tshirtness-montink' ); ?></p></div>
			<?php endif; ?>

			<?php if ( ! $result ) : ?>
				<p><?php echo esc_html__( 'Clique em "Executar sincronização" para importar.', 'tshirtness-montink' ); ?></p>
				<?php return; ?>
			<?php endif; ?>

			<?php $this->render_result( $result ); ?>
		</div>
		<?php
	}

	/**
	 * Whether a chunked sync is currently running.
	 */
	private function is_running(): bool {
		$state = get_option( self::STATE_OPTION, [] );
		return ! empty( $state['step'] ) && 'done' !== $state['step'];
	}

	/**
	 * Render the progress screen. It runs one chunk per page load and reloads
	 * itself via JS until the sync finishes.
	 */
	private function render_progress( array $chunk ): void {
		$pct      = min( 100, max( 0, (int) $chunk['progress'] ) );
		$label    = $chunk['label'];
		$page_url = admin_url( 'admin.php?page=' . TSM_Settings::SYNC_SLUG . '&run=1' );
		?>
		<div class="wrap">
			<h1><?php echo esc_html__( 'Sincronização Montink', 'tshirtness-montink' ); ?></h1>
			<p><?php echo esc_html__( 'Importando catálogo, imagens e variações. Esta página se atualiza automaticamente…', 'tshirtness-montink' ); ?></p>

			<div style="max-width:640px;margin:24px 0;">
				<div style="height:22px;background:#e5e5e5;border-radius:11px;overflow:hidden;border:1px solid #dcdcde;">
					<div style="height:100%;width:<?php echo esc_attr( (string) $pct ); ?>%;background:linear-gradient(90deg,#2271b1,#00a32a);transition:width .5s;"></div>
				</div>
				<p style="margin-top:8px;">
					<strong><?php echo esc_html( (string) $pct ); ?>%</strong>
					&nbsp;•&nbsp;
					<span style="color:#646970;"><?php echo esc_html( $label ); ?></span>
				</p>
			</div>

			<noscript>
				<p><a class="button" href="<?php echo esc_url( $page_url ); ?>"><?php echo esc_html__( 'Continuar', 'tshirtness-montink' ); ?></a></p>
			</noscript>
		</div>
		<script>
		(function () {
			'use strict';
			// Auto-refresh every 1.5s until the sync is done (this endpoint then
			// redirects to the results page).
			setTimeout(function () {
				window.location.href = <?php echo wp_json_encode( esc_url_raw( $page_url ) ); ?>;
			}, 1500);
		})();
		</script>
		<?php
	}

	private function render_result( array $result ): void {
		$date = wp_date( 'd/m/Y H:i', $result['timestamp'] );
		echo '<p>' . esc_html( sprintf( __( 'Última sincronização: %s', 'tshirtness-montink' ), $date ) ) . '</p>';

		if ( ! empty( $result['errors'] ) ) {
			echo '<div class="notice notice-error"><ul>';
			foreach ( $result['errors'] as $e ) {
				echo '<li>' . esc_html( $e ) . '</li>';
			}
			echo '</ul></div>';
		}

		echo '<h2>' . esc_html__( 'Resumo', 'tshirtness-montink' ) . '</h2>';
		echo '<p>'
			. esc_html( sprintf( __( 'Produtos WooCommerce criados: %d', 'tshirtness-montink' ), count( $result['created_products'] ) ) )
			. '<br>'
			. esc_html( sprintf( __( 'Variações criadas: %d', 'tshirtness-montink' ), $result['created_variations'] ) )
			. '</p>';

		echo '<h2>' . esc_html__( 'Estampas importadas', 'tshirtness-montink' ) . ' — ' . esc_html( (string) count( $result['groups'] ) ) . '</h2>';
		echo '<table class="widefat striped"><thead><tr>'
			. '<th>' . esc_html__( 'Estampa', 'tshirtness-montink' ) . '</th>'
			. '<th>' . esc_html__( 'Modelos (Montink)', 'tshirtness-montink' ) . '</th>'
			. '<th>' . esc_html__( 'Produto Woo', 'tshirtness-montink' ) . '</th>'
			. '<th>' . esc_html__( 'Variações criadas', 'tshirtness-montink' ) . '</th>'
			. '<th>' . esc_html__( 'Status', 'tshirtness-montink' ) . '</th>'
			. '</tr></thead><tbody>';

		foreach ( $result['groups'] as $g ) {
			$models = array_map( static fn( $v ) => $v['model'] . ' (#' . $v['product_id'] . ')', $g['variants'] );
			echo '<tr>';
			echo '<td><strong>' . esc_html( $g['name'] ) . '</strong></td>';
			echo '<td>' . esc_html( implode( '; ', $models ) ) . '</td>';
			if ( $g['woo_id'] ) {
				$edit = get_edit_post_link( $g['woo_id'] );
				echo '<td><a href="' . esc_url( $edit ) . '">' . esc_html( $g['name'] ) . ' (ID ' . esc_html( $g['woo_id'] ) . ')</a></td>';
			} else {
				echo '<td>—</td>';
			}
			echo '<td>' . esc_html( (string) $g['variations_added'] ) . '</td>';
			echo '<td>';
			if ( $g['created'] ) {
				echo '<span style="color:#2271b1">' . esc_html__( 'Produto criado', 'tshirtness-montink' ) . '</span>';
			} elseif ( ! empty( $g['errors'] ) ) {
				echo '<span style="color:#d63638">' . esc_html( implode( '; ', $g['errors'] ) ) . '</span>';
			} else {
				echo '<span style="color:#00a32a">OK</span>';
			}
			echo '</td></tr>';
		}

		echo '</tbody></table>';

		$missing = $result['missing_in_montink'];
		echo '<h2>' . esc_html__( 'Produtos WooCommerce SEM correspondência na Montink', 'tshirtness-montink' ) . ' — ' . esc_html( (string) count( $missing ) ) . '</h2>';

		if ( empty( $missing ) ) {
			echo '<p>' . esc_html__( 'Todos os produtos WooCommerce têm correspondência na Montink.', 'tshirtness-montink' ) . '</p>';
		} else {
			echo '<table class="widefat striped"><thead><tr>'
				. '<th>' . esc_html__( 'ID', 'tshirtness-montink' ) . '</th>'
				. '<th>' . esc_html__( 'Produto', 'tshirtness-montink' ) . '</th>'
				. '<th>' . esc_html__( 'SKU', 'tshirtness-montink' ) . '</th>'
				. '</tr></thead><tbody>';
			foreach ( $missing as $m ) {
				echo '<tr><td>' . esc_html( $m['id'] ) . '</td><td><a href="' . esc_url( get_edit_post_link( $m['id'] ) ) . '">' . esc_html( $m['name'] ) . '</a></td><td>' . esc_html( $m['sku'] ) . '</td></tr>';
			}
			echo '</tbody></table>';
		}
	}
}
