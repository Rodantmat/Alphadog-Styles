<?php
/**
 * Montink API client.
 *
 * @package Tshirtness_Montink
 */

defined( 'ABSPATH' ) || exit;

final class TSM_API {

	const BASE_URL = 'https://api.montink.com';

	/**
	 * Return the saved API token (or empty string).
	 */
	private static function token(): string {
		$opts = TSM::get_options();
		return isset( $opts['api_token'] ) ? (string) $opts['api_token'] : '';
	}

	/**
	 * Perform an authenticated GET against the Montink API.
	 *
	 * @param string $path    Path after the base URL, starting with '/'.
	 * @param array  $query   Optional query params.
	 *
	 * @return array|WP_Error Decoded JSON body, or WP_Error on failure.
	 */
	public static function get( string $path, array $query = [] ) {
		$token = self::token();
		if ( '' === $token ) {
			return new WP_Error( 'tsm_no_token', __( 'Token Montink não configurado.', 'tshirtness-montink' ) );
		}

		$url = self::BASE_URL . $path;
		if ( $query ) {
			$url = add_query_arg( $query, $url );
		}

		$args = [
			'timeout'     => 30,
			'sslverify'   => true,
			'redirection' => 5,
			'headers'     => [ 'Authorizationtoken' => $token ],
		];

		$response = wp_remote_get( $url, $args );

		if ( is_wp_error( $response ) ) {
			return $response;
		}

		$code = wp_remote_retrieve_response_code( $response );
		if ( 200 !== $code ) {
			return new WP_Error(
				'tsm_http_' . $code,
				sprintf(
					/* translators: %d: HTTP response code */
					__( 'Montink retornou status HTTP %d.', 'tshirtness-montink' ),
					$code
				),
				[ 'status' => $code, 'body' => wp_remote_retrieve_body( $response ) ]
			);
		}

		$body    = wp_remote_retrieve_body( $response );
		$decoded = json_decode( $body, true );

		if ( ! is_array( $decoded ) ) {
			return new WP_Error( 'tsm_invalid_json', __( 'Resposta inválida da Montink.', 'tshirtness-montink' ) );
		}

		if ( isset( $decoded['success'] ) && false === $decoded['success'] ) {
			return new WP_Error(
				'tsm_api_error',
				isset( $decoded['msg'] ) ? (string) $decoded['msg'] : __( 'Erro da Montink.', 'tshirtness-montink' )
			);
		}

		return $decoded;
	}

	/**
	 * Fetch all enabled products (paginated).
	 *
	 * @return array|WP_Error Array of products, or WP_Error.
	 */
	public static function get_products() {
		$all    = [];
		$page   = 0;
		$max_pg = 20;

		while ( $page < $max_pg ) {
			$res = self::get( '/products', [ 'pp' => 200, 'pga' => $page ] );
			if ( is_wp_error( $res ) ) {
				return $res;
			}

			$products = isset( $res['produtos'] ) && is_array( $res['produtos'] ) ? $res['produtos'] : [];
			if ( empty( $products ) ) {
				break;
			}

			$all = array_merge( $all, $products );

			// contPg is 0-based; stop when the returned page is below the requested page.
			if ( ! empty( $res['contPg'] ) && (int) $res['contPg'] <= $page ) {
				break;
			}
			$page++;
		}

		return $all;
	}

	/**
	 * Fetch a single product detail.
	 *
	 * @param string $product_id Montink product id.
	 *
	 * @return array|WP_Error
	 */
	public static function get_product( string $product_id ) {
		return self::get( '/product/' . rawurlencode( $product_id ) );
	}

	/**
	 * Perform an authenticated POST against the Montink API with a JSON body.
	 *
	 * @param string $path  Path after the base URL, starting with '/'.
	 * @param array  $body  Associative array encoded as JSON.
	 *
	 * @return array|WP_Error Decoded JSON body, or WP_Error on failure.
	 */
	public static function post( string $path, array $body = [] ) {
		$token = self::token();
		if ( '' === $token ) {
			return new WP_Error( 'tsm_no_token', __( 'Token Montink não configurado.', 'tshirtness-montink' ) );
		}

		$args = [
			'timeout'     => 30,
			'sslverify'   => true,
			'redirection' => 5,
			'headers'     => [
				'Authorizationtoken' => $token,
				'Content-Type'       => 'application/json',
			],
			'body'        => wp_json_encode( $body ),
		];

		$response = wp_remote_post( self::BASE_URL . $path, $args );

		if ( is_wp_error( $response ) ) {
			return $response;
		}

		$code = wp_remote_retrieve_response_code( $response );
		if ( 200 !== $code ) {
			return new WP_Error(
				'tsm_http_' . $code,
				sprintf(
					/* translators: %d: HTTP response code */
					__( 'Montink retornou status HTTP %d.', 'tshirtness-montink' ),
					$code
				),
				[ 'status' => $code, 'body' => wp_remote_retrieve_body( $response ) ]
			);
		}

		$body    = wp_remote_retrieve_body( $response );
		$decoded = json_decode( $body, true );

		if ( ! is_array( $decoded ) ) {
			return new WP_Error( 'tsm_invalid_json', __( 'Resposta inválida da Montink.', 'tshirtness-montink' ) );
		}

		if ( isset( $decoded['success'] ) && false === $decoded['success'] ) {
			return new WP_Error(
				'tsm_api_error',
				isset( $decoded['msg'] ) ? (string) $decoded['msg'] : __( 'Erro da Montink.', 'tshirtness-montink' )
			);
		}

		return $decoded;
	}

	/**
	 * Start an empty cart on Montink and return its token (for create_order).
	 *
	 * @return array|WP_Error
	 */
	public static function create_cart() {
		return self::post( '/create_cart' );
	}

	/**
	 * Import a WooCommerce order as an external order on Montink.
	 *
	 * @param array $payload create_order body.
	 *
	 * @return array|WP_Error
	 */
	public static function create_order( array $payload ) {
		return self::post( '/create_order', $payload );
	}

	/**
	 * Calculate available shipping options for a CEP + total quantity.
	 *
	 * @param string $cep         Destination CEP.
	 * @param int    $quantity    Total number of units.
	 *
	 * @return array|WP_Error
	 */
	public static function calculate_shipping( string $cep, int $quantity ) {
		$res = self::get( '/calculate_shipping/' . rawurlencode( $cep ) . '/' . max( 1, $quantity ) );
		if ( is_wp_error( $res ) ) {
			return $res;
		}
		$options = isset( $res['shipping_options'] ) && is_array( $res['shipping_options'] ) ? $res['shipping_options'] : [];
		return array_values( $options );
	}

	/**
	 * Fetch the detail of a Montink order.
	 *
	 * @param string $order_id Montink order id.
	 *
	 * @return array|WP_Error
	 */
	public static function get_order( string $order_id ) {
		return self::get( '/order/' . rawurlencode( $order_id ) );
	}

	/**
	 * Register a webhook URL so Montink posts order status updates to it.
	 *
	 * @param string $url Full URL (HTTPS recommended).
	 *
	 * @return array|WP_Error
	 */
	public static function register_webhook( string $url ) {
		return self::post( '/webhook', [ 'webhook_url' => $url ] );
	}
}
