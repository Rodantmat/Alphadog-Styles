<?php
/**
 * Main plugin container (singleton).
 *
 * @package Tshirtness_Montink
 */

defined( 'ABSPATH' ) || exit;

final class TSM {

	private static ?TSM $instance = null;

	/** @var string Option key that stores plugin settings. */
	const OPTION_KEY = 'tsm_options';

	/** @var string Meta key that links a WooCommerce product to Montink products. */
	const META_MONTINK_LINK = '_tsm_montink_product_ids';

	public static function instance(): TSM {
		if ( null === self::$instance ) {
			self::$instance = new self();
		}
		return self::$instance;
	}

	public function init(): void {
		require_once TSM_PATH . 'includes/class-tsm-api.php';
		require_once TSM_PATH . 'includes/class-tsm-attributes.php';
		require_once TSM_PATH . 'includes/class-tsm-settings.php';
		require_once TSM_PATH . 'includes/class-tsm-sync.php';
		require_once TSM_PATH . 'includes/class-tsm-orders.php';
		require_once TSM_PATH . 'includes/class-tsm-shipping.php';

		( new TSM_Settings() )->register();
		( new TSM_Sync() )->register();
		( new TSM_Orders() )->register();
		( new TSM_Shipping() )->register();
	}

	/**
	 * Get plugin settings (array) with defaults.
	 */
	public static function get_options(): array {
		return wp_parse_args(
			get_option( self::OPTION_KEY, [] ),
			[
				'api_token'      => '',
				'payment_method' => 'pix',
			]
		);
	}
}
