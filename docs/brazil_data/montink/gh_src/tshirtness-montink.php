<?php
/**
 * Plugin Name:  Montink para WooCommerce
 * Description:  Integração de dropshipping com a plataforma Montink: sincroniza o catálogo, cria variações vinculadas, calcula frete e envia pedidos pagos à Montink, com atualizações de status via webhook.
 * Version:      0.7.0
 * Requires at least: 6.5
 * Requires PHP: 8.1
 * Requires Plugins: woocommerce
 * Author:       Sulivan Rodrigues
 * Author URI:   https://github.com/noxsulivan
 * License:      GPL-2.0-or-later
 * Text Domain:  tshirtness-montink
 */

defined( 'ABSPATH' ) || exit;

define( 'TSM_VERSION', '0.7.0' );
define( 'TSM_PATH',    plugin_dir_path( __FILE__ ) );
define( 'TSM_URL',     plugin_dir_url( __FILE__ ) );

// Bail early if WooCommerce is not active.
add_action( 'plugins_loaded', function () {
	if ( ! class_exists( 'WooCommerce' ) ) {
		add_action( 'admin_notices', function () {
			echo '<div class="notice notice-warning"><p>'
				. esc_html__( 'Tshirtness Montink requires WooCommerce to be active.', 'tshirtness-montink' )
				. '</p></div>';
		} );
		return;
	}

	require_once TSM_PATH . 'includes/class-tsm.php';
	TSM::instance()->init();
} );

// Declare HPOS compatibility (WooCommerce High-Performance Order Storage).
add_action( 'before_woocommerce_init', function () {
	if ( class_exists( \Automattic\WooCommerce\Utilities\FeaturesUtil::class ) ) {
		\Automattic\WooCommerce\Utilities\FeaturesUtil::declare_compatibility(
			'custom_order_tables',
			__FILE__,
			true
		);
	}
} );
