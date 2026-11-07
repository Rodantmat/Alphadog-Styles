<?php
/**
 * WooCommerce → Montink order integration.
 *
 * Sends paid WooCommerce orders to Montink as external orders (create_order),
 * stores the Montink order id/token/tracking on the order, and receives order
 * status updates via a REST webhook.
 *
 * @package Tshirtness_Montink
 */

defined( 'ABSPATH' ) || exit;

final class TSM_Orders {

	/** Order meta: Montink order id. */
	const META_ORDER_ID = '_tsm_montink_order_id';

	/** Order meta: Montink cart token. */
	const META_TOKEN = '_tsm_montink_order_token';

	/** Order meta: last known Montink status text. */
	const META_STATUS = '_tsm_montink_status';

	/** Order meta: Montink tracking URL. */
	const META_TRACKING = '_tsm_montink_tracking_url';

	/** Order meta: flag marking the order as already sent to Montink. */
	const META_SENT = '_tsm_montink_sent';

	/** Order meta: last error message from a failed send. */
	const META_ERROR = '_tsm_montink_last_error';

	/** REST namespace for the webhook. */
	const REST_NS = 'tsm/v1';

	/** admin_post action to resend an order manually. */
	const ACTION_RESEND = 'tsm_resend_order';

	/** admin_post action to register the webhook URL on Montink. */
	const ACTION_WEBHOOK = 'tsm_register_webhook';

	/** Statuses that trigger a send to Montink (payment confirmed). */
	const TRIGGER_STATUSES = [ 'processing', 'completed' ];

	public function register(): void {
		add_action( 'woocommerce_order_status_changed', [ $this, 'maybe_send' ], 10, 3 );
		add_action( 'rest_api_init', [ $this, 'register_webhook_route' ] );
		add_action( 'add_meta_boxes', [ $this, 'add_meta_box' ] );
		add_action( 'admin_post_' . self::ACTION_RESEND, [ $this, 'handle_resend' ] );
		add_action( 'admin_post_' . self::ACTION_WEBHOOK, [ $this, 'handle_webhook_register' ] );
	}

	/**
	 * Send an order to Montink when it reaches a paid status (once only).
	 */
	public function maybe_send( int $order_id, string $from, string $to ): void {
		if ( ! in_array( $to, self::TRIGGER_STATUSES, true ) ) {
			return;
		}
		$this->send_order( $order_id );
	}

	/**
	 * Send a WooCommerce order to Montink via create_order.
	 *
	 * Skips orders already sent or without Montink products.
	 *
	 * @param int $order_id WooCommerce order id.
	 *
	 * @return bool True on success.
	 */
	public function send_order( int $order_id ): bool {
		$order = wc_get_order( $order_id );
		if ( ! $order || 'shop_order' !== $order->get_type() ) {
			return false;
		}

		if ( 'yes' === $order->get_meta( self::META_SENT ) ) {
			return false;
		}

		$payload = $this->build_payload( $order );
		if ( is_wp_error( $payload ) ) {
			$order->add_order_note( __( 'Montink: pedido não enviado — ' . $payload->get_error_message(), 'tshirtness-montink' ) );
			$order->update_meta_data( self::META_ERROR, $payload->get_error_message() );
			$order->save();
			return false;
		}

		$res = TSM_API::create_order( $payload );

		if ( is_wp_error( $res ) ) {
			$order->add_order_note(
				sprintf(
					/* translators: %s: error message. */
					__( 'Montink: falha ao enviar pedido — %s', 'tshirtness-montink' ),
					$res->get_error_message()
				)
			);
			$order->update_meta_data( self::META_ERROR, $res->get_error_message() );
			$order->save();
			return false;
		}

		$montink_id = isset( $res['id'] ) ? (string) $res['id'] : '';
		$token      = isset( $res['token'] ) ? (string) $res['token'] : '';
		$tracking   = isset( $res['tracking_url'] ) ? (string) $res['tracking_url'] : '';

		$order->update_meta_data( self::META_ORDER_ID, $montink_id );
		$order->update_meta_data( self::META_TOKEN, $token );
		$order->update_meta_data( self::META_TRACKING, $tracking );
		$order->update_meta_data( self::META_STATUS, __( 'Aguardando pagamento', 'tshirtness-montink' ) );
		$order->update_meta_data( self::META_SENT, 'yes' );
		$order->delete_meta_data( self::META_ERROR );

		$order->add_order_note(
			sprintf(
				/* translators: %s: Montink order id. */
				__( 'Pedido enviado à Montink. ID Montink: #%s.', 'tshirtness-montink' ),
				$montink_id
			)
		);
		$order->save();

		return true;
	}

	/**
	 * Build the create_order payload from a WooCommerce order.
	 *
	 * @return array|WP_Error
	 */
	private function build_payload( \WC_Order $order ) {
		$opts = TSM::get_options();

		$items = [];
		$units = 0;
		foreach ( $order->get_items() as $item ) {
			$variation_id = (int) $item->get_variation_id();
			if ( ! $variation_id ) {
				continue;
			}
			$product_id = get_post_meta( $variation_id, TSM_Sync::META_VAR_SKU, true );
			if ( '' === $product_id ) {
				continue;
			}

			$attributes = $this->variation_attributes( $variation_id );
			$size       = $attributes['pa_tamanho'] ?? '';
			$color      = $attributes['pa_cor'] ?? '';

			if ( '' === $size || '' === $color ) {
				continue;
			}

			$price = (float) $item->get_subtotal() / max( 1, (int) $item->get_quantity() );

			$items[] = [
				'product_id' => (int) $product_id,
				'quantity'   => (int) $item->get_quantity(),
				'price'      => $price,
				'var1'       => $size,
				'var2'       => $color,
			];
			$units += (int) $item->get_quantity();
		}

		if ( empty( $items ) ) {
			return new WP_Error( 'tsm_no_montink_items', __( 'o pedido não contém produtos vinculados à Montink.', 'tshirtness-montink' ) );
		}

		$shipping = $order->get_address( 'shipping' );
		if ( empty( $shipping['postcode'] ) || empty( $shipping['address_1'] ) ) {
			$shipping = $order->get_address( 'billing' );
		}

		// Brazilian checkout plugins save number/bairro as custom meta with
		// underscore keys on the order (e.g. "Calculadora de Frete e Campos
		// Checkout para o Brasil", "Brazilian Market"). Prefer shipping meta
		// and fall back to billing.
		$sh_number = (string) $order->get_meta( '_shipping_number' );
		$sh_neigh  = (string) $order->get_meta( '_shipping_neighborhood' );
		if ( '' === $sh_number ) {
			$sh_number = (string) $order->get_meta( '_billing_number' );
		}
		if ( '' === $sh_neigh ) {
			$sh_neigh = (string) $order->get_meta( '_billing_neighborhood' );
		}

		$document = $this->document( $order );
		$address  = [
			'zipcode'      => preg_replace( '/\D/', '', (string) ( $shipping['postcode'] ?? '' ) ),
			'street'       => (string) ( $shipping['address_1'] ?? '' ),
			'number'       => $sh_number,
			'neighborhood' => $sh_neigh,
			'city'         => (string) ( $shipping['city'] ?? '' ),
			'state'        => (string) ( $shipping['state'] ?? '' ),
			'complement'   => (string) ( $shipping['address_2'] ?? '' ),
		];

		if ( '' === $address['zipcode'] || '' === $address['street'] ) {
			return new WP_Error( 'tsm_no_address', __( 'endereço de entrega incompleto.', 'tshirtness-montink' ) );
		}

		$shipping_id = $this->resolve_shipping_id( $order, $address['zipcode'], $units );

		$birthdate = (string) $order->get_meta( '_billing_birthdate' );
		if ( '' === $birthdate ) {
			$birthdate = (string) $order->get_meta( 'billing_birthdate' );
		}

		$payload = [
			'customer_name'     => $order->get_billing_first_name() . ' ' . $order->get_billing_last_name(),
			'customer_email'    => $order->get_billing_email(),
			'customer_document' => $document,
			'customer_phone'    => preg_replace( '/\D/', '', (string) $order->get_billing_phone() ),
			'payment_method'    => isset( $opts['payment_method'] ) ? (string) $opts['payment_method'] : 'pix',
			'external_order_id' => (string) $order->get_id(),
			'address'           => $address,
			'products'          => $items,
		];

		if ( '' !== $birthdate ) {
			$payload['customer_birthday'] = $this->normalize_birthdate( $birthdate );
		}

		if ( $shipping_id ) {
			$payload['shipping_id'] = $shipping_id;
		}

		return $payload;
	}

	/**
	 * Normalize a birthdate to Y-m-d (accepts d/m/Y or Y-m-d).
	 */
	private function normalize_birthdate( string $raw ): string {
		$raw = trim( $raw );
		if ( preg_match( '/^\d{2}\/\d{2}\/\d{4}$/', $raw ) ) {
			$parts = explode( '/', $raw );
			return sprintf( '%04d-%02d-%02d', (int) $parts[2], (int) $parts[1], (int) $parts[0] );
		}
		if ( preg_match( '/^\d{4}-\d{2}-\d{2}$/', $raw ) ) {
			return $raw;
		}
		return '';
	}

	/**
	 * Resolve the Montink delivery_method_id for the order.
	 *
	 * Prefers the delivery_method_id embedded in the shipping item meta (set by
	 * the Montink shipping method), then falls back to name matching against
	 * calculate_shipping options, then to the first available option.
	 */
	private function resolve_shipping_id( \WC_Order $order, string $cep, int $units ): int {
		// If the customer chose a Montink rate, its meta already carries the id.
		foreach ( $order->get_shipping_methods() as $ship ) {
			if ( 'tsm_montink' !== $ship->get_method_id() ) {
				continue;
			}
			$mid = (int) $ship->get_meta( 'tsm_delivery_method_id' );
			if ( $mid > 0 ) {
				return $mid;
			}
		}

		$options = TSM_API::calculate_shipping( $cep, $units );
		if ( is_wp_error( $options ) || empty( $options ) ) {
			return 0;
		}

		$method = strtolower( trim( (string) $order->get_shipping_method() ) );
		if ( '' !== $method ) {
			foreach ( $options as $opt ) {
				$name = strtolower( (string) ( $opt['name'] ?? '' ) );
				if ( '' !== $name && ( false !== strpos( $name, $method ) || false !== strpos( $method, $name ) ) ) {
					return (int) ( $opt['delivery_method_id'] ?? 0 );
				}
			}
		}

		$first = reset( $options );
		return (int) ( $first['delivery_method_id'] ?? 0 );
	}

	/**
	 * Read the size/color attribute names of a variation.
	 *
	 * @return array{pa_modelo?:string,pa_tamanho?:string,pa_cor?:string}
	 */
	private function variation_attributes( int $variation_id ): array {
		$attrs = [];
		$v     = wc_get_product( $variation_id );
		if ( ! $v ) {
			return $attrs;
		}
		foreach ( $v->get_attributes() as $tax => $slug ) {
			if ( ! is_string( $slug ) ) {
				continue;
			}
			$term = get_term_by( 'slug', $slug, $tax );
			$attrs[ $tax ] = $term ? $term->name : $slug;
		}
		return $attrs;
	}

	/**
	 * Find the customer document (CPF/CNPJ) on the order, trying the common
	 * Brazilian checkout field keys.
	 */
	private function document( \WC_Order $order ): string {
		$keys = [ '_billing_cpf', 'billing_cpf', '_billing_cnpj', 'billing_cnpj', '_billing_document', 'billing_document' ];
		foreach ( $keys as $key ) {
			$doc = (string) $order->get_meta( $key );
			if ( '' !== $doc ) {
				return preg_replace( '/\D/', '', $doc );
			}
		}
		return '';
	}

	/**
	 * Register the REST route Montink uses to POST order status updates.
	 */
	public function register_webhook_route(): void {
		register_rest_route(
			self::REST_NS,
			'/webhook',
			[
				'methods'             => 'POST',
				'callback'            => [ $this, 'handle_webhook' ],
				'permission_callback' => '__return_true',
				'args'                => [],
			]
		);
	}

	/**
	 * REST webhook handler. Locates the WooCommerce order by external_order_id
	 * (or Montink id) and syncs the status + tracking.
	 *
	 * @param WP_REST_Request $request
	 *
	 * @return WP_REST_Response
	 */
	public function handle_webhook( \WP_REST_Request $request ) {
		$opts  = TSM::get_options();
		$token = isset( $opts['api_token'] ) ? (string) $opts['api_token'] : '';

		// Verify the sender is Montink (same token used by the integration).
		$header = (string) $request->get_header( 'Authorizationtoken' );
		if ( '' === $header ) {
			$header = isset( $_SERVER['HTTP_AUTHORIZATIONTOKEN'] ) ? (string) $_SERVER['HTTP_AUTHORIZATIONTOKEN'] : '';
		}
		if ( '' !== $token && ! hash_equals( $token, $header ) ) {
			return new \WP_REST_Response( [ 'success' => false, 'msg' => 'Token inválido.' ], 403 );
		}

		$body = $request->get_json_params();
		if ( ! is_array( $body ) ) {
			$body = $request->get_params();
		}

		$carrinho = isset( $body['carrinho'] ) && is_array( $body['carrinho'] ) ? $body['carrinho'] : $body;

		// Try to locate the WooCommerce order.
		$order_id = 0;
		if ( isset( $carrinho['plataforma_pedido_id'] ) ) {
			$order_id = (int) $carrinho['plataforma_pedido_id'];
		} elseif ( isset( $carrinho['id'] ) ) {
			$order_id = $this->find_order_by_montink_id( (string) $carrinho['id'] );
		} elseif ( isset( $body['id'] ) ) {
			$order_id = $this->find_order_by_montink_id( (string) $body['id'] );
		}

		$order = $order_id ? wc_get_order( $order_id ) : false;
		if ( ! $order ) {
			return new \WP_REST_Response( [ 'success' => false, 'msg' => 'Pedido WooCommerce não encontrado.' ], 404 );
		}

		$status  = isset( $body['order']['status'] ) ? (string) $body['order']['status'] : ( isset( $carrinho['status'] ) ? (string) $carrinho['status'] : '' );
		$pay     = isset( $carrinho['pagamento_status'] ) ? (string) $carrinho['pagamento_status'] : '';
		$track   = isset( $body['linkRastreio'] ) ? (string) $body['linkRastreio'] : ( isset( $carrinho['link_rastreio'] ) ? (string) $carrinho['link_rastreio'] : '' );

		if ( '' !== $status ) {
			$order->update_meta_data( self::META_STATUS, $status );
		}
		if ( '' !== $track ) {
			$order->update_meta_data( self::META_TRACKING, $track );
		}
		if ( isset( $carrinho['id'] ) ) {
			$order->update_meta_data( self::META_ORDER_ID, (string) $carrinho['id'] );
		}
		$order->save();

		$order->add_order_note(
			sprintf(
				/* translators: %1$s: Montink status, %2$s: payment status. */
				__( 'Montink: status "%1$s" (pagamento: %2$s).', 'tshirtness-montink' ),
				$status,
				$pay
			)
		);

		$wc_status = $this->map_status( $status, $pay );
		if ( $wc_status ) {
			$order->update_status( $wc_status, __( 'Atualizado pelo webhook Montink.', 'tshirtness-montink' ) );
		}

		return new \WP_REST_Response( [ 'success' => true, 'msg' => 'Status atualizado.' ], 200 );
	}

	/**
	 * Map a Montink status to a WooCommerce order status.
	 */
	private function map_status( string $montink, string $payment ): string {
		$s = strtolower( $montink );
		$p = strtolower( $payment );

		if ( 'paid' === $p || false !== strpos( $s, 'pago' ) || false !== strpos( $s, 'pagamento confirmado' ) ) {
			return 'processing';
		}
		if ( 'canceled' === $p || 'cancelled' === $p || false !== strpos( $s, 'cancel' ) ) {
			return 'cancelled';
		}
		if ( false !== strpos( $s, 'transit' ) || false !== strpos( $s, 'enviad' ) || false !== strpos( $s, 'entreg' ) || false !== strpos( $s, 'delivered' ) || false !== strpos( $s, 'shipped' ) ) {
			return 'completed';
		}
		return '';
	}

	/**
	 * Find a WooCommerce order by the stored Montink order id.
	 */
	private function find_order_by_montink_id( string $montink_id ): int {
		if ( '' === $montink_id ) {
			return 0;
		}
		$orders = wc_get_orders( [
			'limit'  => 1,
			'type'   => 'shop_order',
			'return' => 'ids',
			'meta_key'   => self::META_ORDER_ID,
			'meta_value' => $montink_id,
		] );
		return $orders ? (int) $orders[0] : 0;
	}

	/**
	 * Show Montink status inside the order edit screen (works on both the
	 * classic CPT screen and WooCommerce HPOS).
	 */
	public function add_meta_box( string $screen ): void {
		if ( ! in_array( $screen, [ 'shop_order', 'woocommerce_page_wc-orders' ], true ) ) {
			return;
		}
		add_meta_box(
			'tsm_montink_order',
			__( 'Montink — Pedido', 'tshirtness-montink' ),
			[ $this, 'render_meta_box' ],
			$screen,
			'side',
			'high'
		);
	}

	public function render_meta_box( \WP_Post $post ): void {
		$order = wc_get_order( $post->ID );
		if ( ! $order ) {
			return;
		}

		$id       = (string) $order->get_meta( self::META_ORDER_ID );
		$status   = (string) $order->get_meta( self::META_STATUS );
		$tracking = (string) $order->get_meta( self::META_TRACKING );
		$error    = (string) $order->get_meta( self::META_ERROR );
		$sent     = 'yes' === $order->get_meta( self::META_SENT );

		echo '<p>';
		if ( $sent && '' !== $id ) {
			echo '<strong>' . esc_html__( 'Enviado à Montink', 'tshirtness-montink' ) . '</strong><br>';
			/* translators: %s: Montink order id. */
			echo esc_html( sprintf( __( 'ID: #%s', 'tshirtness-montink' ), $id ) ) . '<br>';
			if ( '' !== $status ) {
				echo esc_html__( 'Status: ', 'tshirtness-montink' ) . esc_html( $status ) . '<br>';
			}
			if ( '' !== $tracking ) {
				echo '<a href="' . esc_url( $tracking ) . '" target="_blank" rel="noopener">' . esc_html__( 'Rastrear pedido', 'tshirtness-montink' ) . '</a>';
			}
		} else {
			echo esc_html__( 'Pedido ainda não enviado à Montink.', 'tshirtness-montink' );
			if ( '' !== $error ) {
				echo '<br><em>' . esc_html__( 'Último erro: ', 'tshirtness-montink' ) . esc_html( $error ) . '</em>';
			}
			$url = wp_nonce_url(
				add_query_arg( [ 'action' => self::ACTION_RESEND, 'order_id' => $post->ID ], admin_url( 'admin-post.php' ) ),
				self::ACTION_RESEND
			);
			echo '<br><a class="button" href="' . esc_url( $url ) . '">' . esc_html__( 'Enviar para a Montink agora', 'tshirtness-montink' ) . '</a>';
		}
		echo '</p>';
	}

	/**
	 * Manual resend from the order edit screen.
	 */
	public function handle_resend(): void {
		if ( ! current_user_can( 'manage_woocommerce' ) ) {
			wp_die( esc_html__( 'Permissão negada.', 'tshirtness-montink' ) );
		}
		check_admin_referer( self::ACTION_RESEND );

		$order_id = isset( $_GET['order_id'] ) ? (int) $_GET['order_id'] : 0;
		$this->send_order( $order_id );

		wp_safe_redirect(
			admin_url( 'post.php?post=' . $order_id . '&action=edit' )
		);
		exit;
	}

	/**
	 * Register the plugin webhook URL on Montink (settings button).
	 */
	public function handle_webhook_register(): void {
		if ( ! current_user_can( 'manage_woocommerce' ) ) {
			wp_die( esc_html__( 'Permissão negada.', 'tshirtness-montink' ) );
		}
		check_admin_referer( self::ACTION_WEBHOOK );

		$url = rest_url( self::REST_NS . '/webhook' );
		$res = TSM_API::register_webhook( $url );

		$flag = is_wp_error( $res ) ? 'tsm_webhook_err' : 'tsm_webhook_ok';

		wp_safe_redirect(
			add_query_arg(
				[ 'page' => TSM_Settings::PAGE_SLUG, $flag => '1' ],
				admin_url( 'admin.php' )
			)
		);
		exit;
	}
}