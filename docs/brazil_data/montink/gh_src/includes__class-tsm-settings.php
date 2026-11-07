<?php
/**
 * Plugin settings page (Settings API).
 *
 * @package Tshirtness_Montink
 */

defined( 'ABSPATH' ) || exit;

final class TSM_Settings {

	const PAGE_SLUG   = 'tsm-settings';
	const SYNC_SLUG   = 'tsm-sync';
	const OPTION_GROUP = 'tsm_options_group';

	public function register(): void {
		add_action( 'admin_menu', [ $this, 'add_menus' ] );
		add_action( 'admin_init', [ $this, 'register_settings' ] );
	}

	public function add_menus(): void {
		add_menu_page(
			__( 'Montink', 'tshirtness-montink' ),
			__( 'Montink', 'tshirtness-montink' ),
			'manage_woocommerce',
			self::PAGE_SLUG,
			[ $this, 'render_settings_page' ],
			'dashicons-car',
			56
		);

		add_submenu_page(
			self::PAGE_SLUG,
			__( 'Sincronização', 'tshirtness-montink' ),
			__( 'Sincronização', 'tshirtness-montink' ),
			'manage_woocommerce',
			self::SYNC_SLUG,
			[ $this, 'render_sync_page' ]
		);
	}

	public function register_settings(): void {
		register_setting(
			self::OPTION_GROUP,
			TSM::OPTION_KEY,
			[
				'type'              => 'array',
				'sanitize_callback' => [ $this, 'sanitize' ],
				'default'           => [ 'api_token' => '' ],
				'show_in_rest'      => false,
			]
		);

		add_settings_section(
			'tsm_main',
			__( 'Conexão Montink', 'tshirtness-montink' ),
			'__return_false',
			self::PAGE_SLUG
		);

		add_settings_field(
			'tsm_api_token',
			__( 'Token de autorização', 'tshirtness-montink' ),
			[ $this, 'render_token_field' ],
			self::PAGE_SLUG,
			'tsm_main'
		);

		add_settings_section(
			'tsm_orders',
			__( 'Pedidos', 'tshirtness-montink' ),
			'__return_false',
			self::PAGE_SLUG
		);

		add_settings_field(
			'tsm_payment_method',
			__( 'Forma de pagamento Montink', 'tshirtness-montink' ),
			[ $this, 'render_payment_field' ],
			self::PAGE_SLUG,
			'tsm_orders'
		);

		add_settings_field(
			'tsm_webhook',
			__( 'Webhook de status', 'tshirtness-montink' ),
			[ $this, 'render_webhook_field' ],
			self::PAGE_SLUG,
			'tsm_orders'
		);
	}

	/**
	 * Sanitize all settings on save.
	 */
	public function sanitize( $input ): array {
		$input = is_array( $input ) ? $input : [];

		$token = isset( $input['api_token'] ) ? trim( (string) $input['api_token'] ) : '';

		// Empty field means "keep the current token".
		if ( '' === $token ) {
			$current = get_option( TSM::OPTION_KEY, [] );
			$token   = isset( $current['api_token'] ) ? (string) $current['api_token'] : '';
		}

		$payment = isset( $input['payment_method'] ) ? (string) $input['payment_method'] : 'pix';
		if ( ! in_array( $payment, [ 'pix', 'saldo', 'boleto' ], true ) ) {
			$payment = 'pix';
		}

		return [
			'api_token'      => sanitize_text_field( $token ),
			'payment_method' => $payment,
		];
	}

	public function render_token_field(): void {
		$opts = TSM::get_options();
		$set  = ! empty( $opts['api_token'] ) ? __( 'Token configurado. Deixe em branco para manter.', 'tshirtness-montink' ) : __( 'Nenhum token configurado.', 'tshirtness-montink' );
		echo '<input type="password" name="' . esc_attr( TSM::OPTION_KEY ) . '[api_token]" value="" class="regular-text" autocomplete="off" placeholder="' . esc_attr( __( 'Cole o token da Montink', 'tshirtness-montink' ) ) . '">';
		echo '<p class="description">' . esc_html( $set ) . '</p>';
		echo '<p class="description">' . esc_html__( 'Gere o token em: Montink → Adicionar Apps → API Montink → Conectar.', 'tshirtness-montink' ) . '</p>';
	}

	public function render_payment_field(): void {
		$opts = TSM::get_options();
		$cur  = isset( $opts['payment_method'] ) ? (string) $opts['payment_method'] : 'pix';
		$opts = [
			'pix'    => __( 'Pix', 'tshirtness-montink' ),
			'saldo'  => __( 'Saldo (carteira Montink)', 'tshirtness-montink' ),
			'boleto' => __( 'Boleto', 'tshirtness-montink' ),
		];
		echo '<select name="' . esc_attr( TSM::OPTION_KEY ) . '[payment_method]">';
		foreach ( $opts as $value => $label ) {
			printf(
				'<option value="%s"%s>%s</option>',
				esc_attr( $value ),
				selected( $cur, $value, false ),
				esc_html( $label )
			);
		}
		echo '</select>';
		echo '<p class="description">' . esc_html__( 'Método de pagamento usado ao importar o pedido na Montink.', 'tshirtness-montink' ) . '</p>';
	}

	public function render_webhook_field(): void {
		$url = rest_url( TSM_Orders::REST_NS . '/webhook' );
		echo '<code>' . esc_html( $url ) . '</code>';
		echo '<p class="description">' . esc_html__( 'Cadastre esta URL no app da Montink (ou no botão abaixo) para receber atualizações de status.', 'tshirtness-montink' ) . '</p>';

		$button = wp_nonce_url(
			add_query_arg( [ 'action' => 'tsm_register_webhook' ], admin_url( 'admin-post.php' ) ),
			'tsm_register_webhook'
		);
		echo '<p><a class="button" href="' . esc_url( $button ) . '">' . esc_html__( 'Cadastrar webhook na Montink', 'tshirtness-montink' ) . '</a></p>';

		if ( isset( $_GET['tsm_webhook_ok'] ) ) {
			echo '<p class="notice notice-success" style="padding:8px;">' . esc_html__( 'Webhook cadastrado com sucesso.', 'tshirtness-montink' ) . '</p>';
		} elseif ( isset( $_GET['tsm_webhook_err'] ) ) {
			echo '<p class="notice notice-error" style="padding:8px;">' . esc_html__( 'Falha ao cadastrar webhook.', 'tshirtness-montink' ) . '</p>';
		}
	}

	public function render_settings_page(): void {
		if ( ! current_user_can( 'manage_woocommerce' ) ) {
			return;
		}
		?>
		<div class="wrap">
			<h1><?php echo esc_html( get_admin_page_title() ); ?></h1>
			<form action="options.php" method="post">
				<?php
				settings_fields( self::OPTION_GROUP );
				do_settings_sections( self::PAGE_SLUG );
				submit_button( __( 'Salvar', 'tshirtness-montink' ) );
				?>
			</form>
		</div>
		<?php
	}

	public function render_sync_page(): void {
		if ( ! current_user_can( 'manage_woocommerce' ) ) {
			return;
		}
		// Delegate rendering to the sync controller (keeps sync logic together).
		( new TSM_Sync() )->render_page();
	}
}
