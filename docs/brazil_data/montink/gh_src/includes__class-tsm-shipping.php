<?php
/**
 * Montink shipping method (WooCommerce shipping zone method).
 *
 * Adds a "Frete Montink" method that quotes delivery via the Montink
 * calculate_shipping API. Rates embed the Montink delivery_method_id as order
 * shipping item meta so the order payload can send the exact shipping_id that
 * the customer chose (validated against the same CEP/total quantity).
 *
 * @package Tshirtness_Montink
 */

defined( 'ABSPATH' ) || exit;

final class TSM_Shipping_Method extends WC_Shipping_Method {

	public function __construct( int $instance_id = 0 ) {
		$this->id                 = 'tsm_montink';
		$this->instance_id        = absint( $instance_id );
		$this->method_title       = __( 'Frete Montink', 'tshirtness-montink' );
		$this->method_description = __( 'Calcula o frete usando a API da Montink.', 'tshirtness-montink' );
		$this->supports           = [ 'shipping-zones', 'instance-settings' ];

		$this->init();
	}

	public function init(): void {
		$this->init_form_fields();
		$this->title      = $this->get_option( 'title', $this->method_title );
		$this->tax_status = $this->get_option( 'tax_status' );
	}

	public function init_form_fields(): void {
		$this->form_fields = [
			'title' => [
				'title'       => __( 'Título', 'tshirtness-montink' ),
				'type'        => 'text',
				'description' => __( 'Nome exibido no checkout.', 'tshirtness-montink' ),
				'default'     => __( 'Frete Montink', 'tshirtness-montink' ),
				'desc_tip'    => true,
			],
			'tax_status' => [
				'title'   => __( 'Impostos', 'tshirtness-montink' ),
				'type'    => 'select',
				'default' => 'taxable',
				'options' => [
					'taxable' => __( 'Tributável', 'tshirtness-montink' ),
					'none'    => __( 'Isento', 'tshirtness-montink' ),
				],
			],
		];
	}

	/**
	 * Quote shipping for a package using the Montink API.
	 *
	 * @param array $package Shipping package.
	 */
	public function calculate_shipping( $package = [] ): void {
		$cep = preg_replace( '/\D/', '', (string) ( $package['destination']['postcode'] ?? '' ) );
		if ( '' === $cep ) {
			return;
		}

		$qty = 0;
		if ( isset( $package['contents'] ) && is_array( $package['contents'] ) ) {
			foreach ( $package['contents'] as $item ) {
				$qty += (int) ( $item['quantity'] ?? 1 );
			}
		}
		if ( $qty < 1 ) {
			$qty = 1;
		}

		$options = $this->get_options_cached( $cep, $qty );
		if ( is_wp_error( $options ) || empty( $options ) ) {
			return;
		}

		foreach ( $options as $opt ) {
			$id   = (int) ( $opt['delivery_method_id'] ?? 0 );
			$name = (string) ( $opt['name'] ?? '' );
			$cost = (float) ( $opt['value'] ?? 0 );
			if ( ! $id || '' === $name ) {
				continue;
			}

			$label = $name;
			$days  = (int) ( $opt['business_days'] ?? 0 );
			if ( $days > 0 ) {
				/* translators: %d: number of business days. */
				$label .= sprintf( ' (%d %s)', $days, _n( 'dia útil', 'dias úteis', $days, 'tshirtness-montink' ) );
			}

			$this->add_rate( [
				'id'        => $this->id . '_' . $id,
				'label'     => $label,
				'cost'      => $cost,
				'meta_data' => [
					'tsm_delivery_method_id' => $id,
					'tsm_delivery_name'      => $name,
				],
			] );
		}
	}

	/**
	 * Fetch shipping options with a short-lived cache (per CEP + quantity).
	 */
	private function get_options_cached( string $cep, int $qty ) {
		$cache_key = 'tsm_shipping_' . md5( $cep . '_' . $qty );
		$cached    = get_transient( $cache_key );
		if ( is_array( $cached ) ) {
			return $cached;
		}

		$options = TSM_API::calculate_shipping( $cep, $qty );
		if ( is_wp_error( $options ) ) {
			return $options;
		}

		set_transient( $cache_key, $options, 30 * MINUTE_IN_SECONDS );
		return $options;
	}
}

final class TSM_Shipping {

	/** REST namespace for product-page shipping quotes. */
	const REST_NS = 'tsm/v1';

	public function register(): void {
		add_filter( 'woocommerce_shipping_methods', [ $this, 'add_method' ] );
		add_action( 'rest_api_init', [ $this, 'register_quote_route' ] );
		add_action( 'woocommerce_single_product_summary', [ $this, 'render_product_calculator' ], 50 );
		add_action( 'wp_enqueue_scripts', [ $this, 'enqueue_product_scripts' ] );
	}

	public function add_method( array $methods ): array {
		$methods['tsm_montink'] = 'TSM_Shipping_Method';
		return $methods;
	}

	/**
	 * GET /tsm/v1/shipping?cep=01310100&qty=1
	 *
	 * Returns the Montink delivery options (price + delivery time) so the
	 * product-page calculator can render them without hitting the AJAX
	 * endpoints blocked by the WAF.
	 */
	public function register_quote_route(): void {
		register_rest_route(
			self::REST_NS,
			'/shipping',
			[
				'methods'             => 'GET',
				'callback'            => [ $this, 'handle_quote' ],
				'permission_callback' => '__return_true',
				'args'                => [
					'cep' => [
						'required'          => true,
						'sanitize_callback' => static function ( $v ) {
							return preg_replace( '/\D/', '', (string) $v );
						},
					],
					'qty' => [
						'default'           => 1,
						'sanitize_callback' => static fn( $v ) => max( 1, (int) $v ),
					],
				],
			]
		);
	}

	/**
	 * Quote handler for the product-page calculator.
	 *
	 * @param WP_REST_Request $request
	 */
	public function handle_quote( \WP_REST_Request $request ) {
		$cep = (string) $request->get_param( 'cep' );
		$qty = (int) $request->get_param( 'qty' );

		if ( 8 !== strlen( $cep ) ) {
			return new \WP_REST_Response( [ 'success' => false, 'msg' => __( 'Informe um CEP válido.', 'tshirtness-montink' ) ], 400 );
		}

		$options = TSM_API::calculate_shipping( $cep, $qty );
		if ( is_wp_error( $options ) ) {
			return new \WP_REST_Response( [ 'success' => false, 'msg' => $options->get_error_message() ], 502 );
		}
		if ( empty( $options ) ) {
			return new \WP_REST_Response( [ 'success' => false, 'msg' => __( 'Nenhuma opção de frete disponível para este CEP.', 'tshirtness-montink' ) ], 404 );
		}

		$out = [];
		foreach ( $options as $opt ) {
			$out[] = [
				'name'          => (string) ( $opt['name'] ?? '' ),
				'value'         => (float) ( $opt['value'] ?? 0 ),
				'value_fmt'     => wc_price( (float) ( $opt['value'] ?? 0 ) ),
				'business_days' => (int) ( $opt['business_days'] ?? 0 ),
			];
		}

		return new \WP_REST_Response( [ 'success' => true, 'destination' => $cep, 'options' => $out ], 200 );
	}

	/**
	 * Render the "Calcular frete" box on single product pages.
	 */
	public function render_product_calculator(): void {
		if ( ! is_product() ) {
			return;
		}
		$token = TSM::get_options()['api_token'] ?? '';
		if ( '' === $token ) {
			return;
		}
		?>
		<div class="tsm-shipping-calculator" id="tsm-shipping-calculator">
			<h3 class="tsm-shipping-title"><?php echo esc_html__( 'Calcular frete e prazo', 'tshirtness-montink' ); ?></h3>
			<div class="tsm-shipping-row">
				<input
					type="text"
					id="tsm-cep-input"
					class="tsm-cep-input"
					placeholder="00000-000"
					inputmode="numeric"
					autocomplete="postal-code"
					maxlength="9"
				>
				<button type="button" class="tsm-cep-button" id="tsm-cep-button">
					<?php echo esc_html__( 'Calcular', 'tshirtness-montink' ); ?>
				</button>
			</div>
			<div class="tsm-shipping-result" id="tsm-shipping-result" hidden></div>
		</div>
		<?php
	}

	/**
	 * Load the product-page calculator script only on product pages.
	 */
	public function enqueue_product_scripts(): void {
		if ( ! is_product() ) {
			return;
		}
		wp_enqueue_script(
			'tsm-shipping',
			TSM_URL . 'assets/js/tsm-shipping.js',
			[ 'jquery' ],
			TSM_VERSION,
			true
		);
		wp_enqueue_style(
			'tsm-shipping',
			TSM_URL . 'assets/css/tsm-shipping.css',
			[],
			TSM_VERSION
		);
		wp_localize_script( 'tsm-shipping', 'tsmShipping', [
			'endpoint' => rest_url( self::REST_NS . '/shipping' ),
			'labels'   => [
				'loading' => __( 'Calculando…', 'tshirtness-montink' ),
				'error'   => __( 'Não foi possível calcular o frete.', 'tshirtness-montink' ),
				'days'    => __( 'dia(s) útil(eis)', 'tshirtness-montink' ),
			],
		] );
	}
}