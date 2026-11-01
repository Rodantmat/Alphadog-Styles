// Tiny i18n: English is the source text; t("English") returns the Spanish / Brazilian Portuguese version when active.
const SUP=["en","es","pt"];
const pick=l=>{l=String(l||"").toLowerCase();return l.startsWith("es")?"es":l.startsWith("pt")?"pt":l.startsWith("en")?"en":null};
function detect(){
  let s=null;try{s=localStorage.getItem("ad_lang")}catch{}
  if(SUP.includes(s))return s;
  const list=(navigator.languages&&navigator.languages.length?navigator.languages:[navigator.language||"en"]);
  for(const l of list){const p=pick(l);if(p)return p}
  return "en";
}
export let lang=detect();
export const setLang=l=>{if(!SUP.includes(l))return;try{localStorage.setItem("ad_lang",l)}catch{}lang=l};
export const missing=new Set();
const D={es:{},pt:{}};
const add=(en,es,pt)=>{D.es[en]=es;D.pt[en]=pt};
export function t(s,...a){
  let o=s;
  if(lang!=="en"){o=D[lang][s];if(o===undefined){missing.add(s);o=s}}
  return a.length?o.replace(/\{(\d+)\}/g,(m,i)=>a[i]??""):o;
}
export const tn=s=>lang==="en"?s:(D[lang][s]??s);   // names (breeds, colors, styles)
/* ---- UI strings ---- */
add("Free US shipping on orders over $75","Envío gratis en EE. UU. en pedidos de más de $75","Frete grátis nos EUA em pedidos acima de $75");
add("Made to order, printed just for you","Hecho por encargo, impreso solo para ti","Feito sob encomenda, impresso só para você");
add("Shop","Tienda","Loja");add("Design yours","Diseña el tuyo","Crie o seu");add("Our story","Nuestra historia","Nossa história");add("Help","Ayuda","Ajuda");
add("Account","Cuenta","Conta");add("Cart","Carrito","Carrinho");add("Menu","Menú","Menu");add("Log in","Iniciar sesión","Entrar");
add("Made to order · Shipped across the US","Hecho por encargo · Envíos en todo EE. UU.","Feito sob encomenda · Envio para todos os EUA");
add("Your best friend, on your best tee.","Tu mejor amigo, en tu mejor camiseta.","Seu melhor amigo, na sua melhor camiseta.");
add("33 breeds, 2 art styles, 3 moods and every placement you can imagine. Design it your way, we print it just for you.","33 razas, 2 estilos de arte, 3 estados de ánimo y todas las ubicaciones que puedas imaginar. Diséñalo a tu manera, lo imprimimos solo para ti.","33 raças, 2 estilos de arte, 3 climas e todas as posições que você imaginar. Crie do seu jeito, nós imprimimos só para você.");
add("Browse designs","Ver diseños","Ver designs");
add("Fresh from the kennel","Recién salidos de la perrera","Saindo do canil");
add("Today's picks. Tap any design to make it yours.","Selección de hoy. Toca cualquier diseño para hacerlo tuyo.","Seleção de hoje. Toque em qualquer design para torná-lo seu.");
add("See all 198 designs","Ver los 198 diseños","Ver todos os 198 designs");
add("Real garments, real art","Prendas reales, arte real","Peças reais, arte de verdade");
add("Premium tees and hoodies, printed to order.","Camisetas y sudaderas premium, impresas por encargo.","Camisetas e moletons premium, impressos sob encomenda.");
add("Printed tee mockup {0}","Camiseta estampada, ejemplo {0}","Camiseta estampada, exemplo {0}");
add("Three simple steps","Tres pasos sencillos","Três passos simples");
add("Pick your pup","Elige a tu peludo","Escolha seu cachorro");
add("Choose from 33 breeds, in continuous line or geometric art, in Classic, Cool or Heart.","Elige entre 33 razas, en arte de línea continua o geométrico, en Clásico, Cool o Corazón.","Escolha entre 33 raças, em arte de linha contínua ou geométrica, em Clássico, Cool ou Coração.");
add("Make it yours","Hazlo tuyo","Faça do seu jeito");
add("Front, back or both. Head or full body, small emblem or big statement. Different dogs on each side? Go for it.","Frente, espalda o ambas. Cabeza o cuerpo entero, emblema pequeño o diseño grande. ¿Perros distintos en cada lado? Adelante.","Frente, costas ou ambos. Cabeça ou corpo inteiro, emblema pequeno ou estampa grande. Cachorros diferentes em cada lado? Pode ir.");
add("We print and ship","Imprimimos y enviamos","Imprimimos e enviamos");
add("Every piece is printed to order on premium blanks and shipped to your door.","Cada prenda se imprime por encargo sobre prendas premium y se envía a tu puerta.","Cada peça é impressa sob encomenda em peças premium e enviada até a sua porta.");
add("Premium blanks","Prendas premium","Peças premium");
add("Soft Bella+Canvas tees and cozy heavyweight hoodies that survive wash after wash.","Camisetas suaves Bella+Canvas y sudaderas gruesas y cómodas que resisten lavado tras lavado.","Camisetas macias Bella+Canvas e moletons grossos e aconchegantes que aguentam lavagem após lavagem.");
add("Truly custom","Realmente personalizado","Totalmente personalizado");
add("You choose breed, style, placement and color. No two combinations look the same.","Tú eliges raza, estilo, ubicación y color. No hay dos combinaciones iguales.","Você escolhe raça, estilo, posição e cor. Nenhuma combinação é igual à outra.");
add("Printed on demand","Impreso bajo demanda","Impresso sob demanda");
add("Nothing sits in a warehouse. Your order is made when you order it.","Nada se queda en un almacén. Tu pedido se hace cuando lo pides.","Nada fica parado em estoque. Seu pedido é feito quando você pede.");
add("Easy help","Ayuda fácil","Ajuda fácil");
add("Questions? We answer fast. See {0}.","¿Preguntas? Respondemos rápido. Mira {0}.","Dúvidas? Respondemos rápido. Veja {0}.");
add("FAQ","Preguntas frecuentes","Perguntas frequentes");
add("Shop all designs","Todos los diseños","Todos os designs");add("Search a breed…","Busca una raza…","Busque uma raça…");add("Search breeds","Buscar razas","Buscar raças");
add("All styles","Todos los estilos","Todos os estilos");add("All moods","Todos los ánimos","Todos os climas");
add("No designs match. Try another breed.","Ningún diseño coincide. Prueba otra raza.","Nenhum design encontrado. Tente outra raça.");
add("{0} {1} {2} design","Diseño {0} {1} {2}","Design {0} {1} {2}");
add("Preview is illustrative. Actual print is crisp on premium fabric.","La vista previa es ilustrativa. La impresión real es nítida sobre tela premium.","A prévia é ilustrativa. A impressão real é nítida em tecido premium.");
add("Front","Frente","Frente");add("Back","Espalda","Costas");add("Garment","Prenda","Peça");add("Color","Color","Cor");
add("Dark colors with white-ink art are coming soon.","Los colores oscuros con arte en tinta blanca llegarán pronto.","Cores escuras com arte em tinta branca chegam em breve.");
add("{0} - dark colors with white-ink art coming soon","{0} - colores oscuros con tinta blanca próximamente","{0} - cores escuras com tinta branca em breve");
add("Dark colors with white-ink art are coming soon","Los colores oscuros con arte en tinta blanca llegarán pronto","Cores escuras com arte em tinta branca chegam em breve");
add("Front design","Diseño del frente","Design da frente");add("Back design","Diseño de la espalda","Design das costas");
add("No print on the front.","Sin estampado en el frente.","Sem estampa na frente.");add("No print on the back.","Sin estampado en la espalda.","Sem estampa nas costas.");
add("Breed","Raza","Raça");add("Size","Talla","Tamanho");add("Size guide","Guía de tallas","Guia de tamanhos");
add("Add a front or back design","Añade un diseño al frente o a la espalda","Adicione um design na frente ou nas costas");
add("+ shipping","+ envío","+ frete");add("× {0} = {1}","× {0} = {1}","× {0} = {1}");add("{0} items","{0} artículos","{0} itens");
add("Add to cart","Añadir al carrito","Adicionar ao carrinho");add("♡ Save design","♡ Guardar diseño","♡ Salvar design");
add("Made to order for you","Hecho por encargo para ti","Feito sob encomenda para você");add("Ships across the US","Envíos en todo EE. UU.","Envio para todos os EUA");
add("30-day damage guarantee","Garantía de 30 días contra daños","Garantia de 30 dias contra danos");
add("Fabric & fit","Tela y ajuste","Tecido e caimento");add("Shipping & delivery","Envío y entrega","Envio e entrega");add("Care","Cuidado","Cuidados");
add("Production takes about 2 to 5 business days, then 3 to 7 business days in transit within the US. Shipping is $4.99, free over $75. You get tracking by email.","La producción tarda de 2 a 5 días hábiles y el envío dentro de EE. UU. de 3 a 7 días hábiles. El envío cuesta $4.99, gratis a partir de $75. Recibes el seguimiento por correo.","A produção leva de 2 a 5 dias úteis e o envio dentro dos EUA, de 3 a 7 dias úteis. O frete é $4.99, grátis acima de $75. Você recebe o rastreamento por e-mail.");
add("Machine wash cold, inside out, with similar colors. Tumble dry low. Do not iron or dry clean the print. The art is printed directly into the fabric so it will not crack or peel.","Lava a máquina con agua fría, del revés y con colores similares. Seca a baja temperatura. No planches ni limpies en seco el estampado. El arte se imprime directamente en la tela, así que no se agrieta ni se despega.","Lave na máquina em água fria, do avesso, com cores parecidas. Seque em temperatura baixa. Não passe ferro nem lave a seco a estampa. A arte é impressa direto no tecido, então não racha nem descasca.");
add("Bella+Canvas 3001 unisex jersey tee: about 4.2 oz, 100% Airlume combed and ring-spun cotton (heather shades include a little polyester). Soft, lightweight, retail fit that runs true to size. Size up for a relaxed fit.","Camiseta unisex Bella+Canvas 3001: unas 4.2 oz, 100% algodón Airlume peinado e hilado en anillo (los tonos jaspeados incluyen un poco de poliéster). Suave, ligera, de corte clásico y tallas fieles. Elige una talla más para un ajuste holgado.","Camiseta unissex Bella+Canvas 3001: cerca de 4,2 oz, 100% algodão Airlume penteado e fiado em anel (os tons mescla têm um pouco de poliéster). Macia, leve, caimento tradicional e tamanhos fiéis. Escolha um tamanho maior para um caimento solto.");
add("Gildan 18500 heavy blend hoodie: about 8 oz, 50% cotton and 50% polyester with a double-lined hood, pouch pocket and matching drawcord. Classic roomy fit. Size down if you like it snug.","Sudadera Gildan 18500 Heavy Blend: unas 8 oz, 50% algodón y 50% poliéster, con capucha doble, bolsillo canguro y cordón a juego. Ajuste clásico y holgado. Elige una talla menos si la prefieres ceñida.","Moletom Gildan 18500 Heavy Blend: cerca de 8 oz, 50% algodão e 50% poliéster, com capuz forrado, bolso canguru e cordão combinando. Caimento clássico e folgado. Escolha um tamanho menor se gostar mais justo.");
add("Added to cart","Añadido al carrito","Adicionado ao carrinho");add("Log in to save designs","Inicia sesión para guardar diseños","Entre para salvar designs");add("Saved to your account","Guardado en tu cuenta","Salvo na sua conta");
add("Your cart","Tu carrito","Seu carrinho");add("Less","Menos","Menos");add("More","Más","Mais");add("Remove","Quitar","Remover");
add("Subtotal","Subtotal","Subtotal");add("Shipping (US)","Envío (EE. UU.)","Frete (EUA)");add("Free","Gratis","Grátis");add("Shipping","Envío","Frete");
add("Add {0} more for free shipping","Añade {0} más para envío gratis","Adicione mais {0} para frete grátis");
add("You unlocked free shipping!","¡Desbloqueaste el envío gratis!","Você ganhou frete grátis!");
add("Total","Total","Total");add("Checkout","Pagar","Finalizar compra");
add("Your cart is empty.","Tu carrito está vacío.","Seu carrinho está vazio.");add("Design something","Diseña algo","Crie algo");add("or","o","ou");add("browse the shop","explora la tienda","explore a loja");
add("Complete the look","Completa el look","Complete o look");
add("Front: {0}","Frente: {0}","Frente: {0}");add("Back: {0}","Espalda: {0}","Costas: {0}");
add("Contact","Contacto","Contato");add("Email","Correo electrónico","E-mail");add("Ship to","Enviar a","Enviar para");add("United States only","Solo Estados Unidos","Somente Estados Unidos");
add("First name","Nombre","Nome");add("Last name","Apellido","Sobrenome");add("Address","Dirección","Endereço");add("Apt, suite (optional)","Apto., suite (opcional)","Apto., complemento (opcional)");
add("City","Ciudad","Cidade");add("State","Estado","Estado");add("ZIP","Código postal (ZIP)","CEP (ZIP)");add("Phone (optional)","Teléfono (opcional)","Telefone (opcional)");
add("Payment","Pago","Pagamento");
add("You will enter your card on Stripe’s secure page after you tap Pay. We never see or store your card details.","Ingresarás tu tarjeta en la página segura de Stripe después de tocar Pagar. Nunca vemos ni guardamos los datos de tu tarjeta.","Você vai inserir o cartão na página segura da Stripe depois de tocar em Pagar. Nunca vemos nem guardamos os dados do seu cartão.");
add("Order summary","Resumen del pedido","Resumo do pedido");add("Tee","Camiseta","Camiseta");add("Hoodie","Sudadera","Moletom");
add("{0} × {1} ({2}, {3})","{0} × {1} ({2}, {3})","{0} × {1} ({2}, {3})");
add("Pay securely","Pagar de forma segura","Pagar com segurança");add("Opening secure payment…","Abriendo pago seguro…","Abrindo pagamento seguro…");
add("Made to order. See","Hecho por encargo. Mira","Feito sob encomenda. Veja");add("returns","devoluciones","devoluções");
add("Payment received","Pago recibido","Pagamento recebido");add("Reserved","Reservado","Reservado");add("Thank you!","¡Gracias!","Obrigado!");
add("Order {0} is confirmed. Checking payment…","El pedido {0} está confirmado. Verificando el pago…","O pedido {0} está confirmado. Verificando o pagamento…");
add("Your order {0} is saved. We will email you a secure payment link as soon as checkout opens.","Tu pedido {0} está guardado. Te enviaremos por correo un enlace de pago seguro en cuanto se abra el pago.","Seu pedido {0} está salvo. Enviaremos um link de pagamento seguro por e-mail assim que o pagamento abrir.");
add("Order {0} is paid and on its way to print. We will email you tracking when it ships.","El pedido {0} está pagado y va camino a impresión. Te enviaremos el seguimiento por correo cuando salga.","O pedido {0} está pago e a caminho da impressão. Enviaremos o rastreamento por e-mail quando sair.");
add("Order {0} received. Your payment is still processing; you will get an email when it clears.","Pedido {0} recibido. Tu pago aún se está procesando; recibirás un correo cuando se confirme.","Pedido {0} recebido. Seu pagamento ainda está sendo processado; você receberá um e-mail quando for confirmado.");
add("Keep browsing","Seguir explorando","Continuar navegando");
add("Welcome!","¡Bienvenido!","Bem-vindo!");add("Log in or sign up","Inicia sesión o regístrate","Entre ou cadastre-se");add("No password needed.","No necesitas contraseña.","Sem precisar de senha.");
add("Continue with {0}","Continuar con {0}","Continuar com {0}");add("Not connected yet","Aún no está conectado","Ainda não conectado");add("or use your email","o usa tu correo","ou use seu e-mail");
add("Preview mode: the email service is not connected yet, so use code","Modo de vista previa: el servicio de correo aún no está conectado, usa el código","Modo de prévia: o serviço de e-mail ainda não está conectado, use o código");
add("Send my code","Enviar mi código","Enviar meu código");add("Code sent to {0}","Código enviado a {0}","Código enviado para {0}");add("Use a different email","Usar otro correo","Usar outro e-mail");
add("That code is not right","Ese código no es correcto","Esse código não está certo");
add("This sign-in is switching on soon. Use email for now.","Este inicio de sesión se activará pronto. Por ahora usa el correo.","Este login será ativado em breve. Por enquanto, use o e-mail.");
add("Hi there 🐾","Hola 🐾","Olá 🐾");add("Log out","Cerrar sesión","Sair");add("Saved designs","Diseños guardados","Designs salvos");add("Open","Abrir","Abrir");add("Delete","Eliminar","Excluir");
add("Nothing saved yet.","Aún no has guardado nada.","Nada salvo ainda.");add("and tap Save.","y toca Guardar.","e toque em Salvar.");
add("Orders","Pedidos","Pedidos");add("Order","Pedido","Pedido");add("Status","Estado","Status");add("Track","Seguir","Rastrear");add("No orders yet.","Aún no hay pedidos.","Nenhum pedido ainda.");
add("reserved","reservado","reservado");add("awaiting_payment","pago pendiente","aguardando pagamento");add("paid","pagado","pago");add("paid_test","pagado (prueba)","pago (teste)");add("test_complete","prueba completada","teste concluído");
add("in_production","en producción","em produção");add("shipped","enviado","enviado");add("needs_attention","en revisión","em análise");
add("Lost dog?","¿Perro perdido?","Cachorro perdido?");add("That page wandered off.","Esa página se fue a pasear.","Essa página saiu para passear.");add("Back to the shop","Volver a la tienda","Voltar para a loja");
add("You're in the pack!","¡Ya eres parte de la manada!","Você agora faz parte da matilha!");
add("Thanks! We will reply by email soon.","¡Gracias! Te responderemos por correo pronto.","Obrigado! Responderemos por e-mail em breve.");
/* footer / static html */
add("Custom dog-breed apparel for people who think their dog is the best breed. (It is.)","Ropa personalizada de razas de perro para quienes creen que su perro es la mejor raza. (Lo es.)","Roupas personalizadas de raças de cachorro para quem acha que o seu cachorro é a melhor raça. (E é.)");
add("All designs","Todos los diseños","Todos os designs");add("Continuous line","Línea continua","Linha contínua");add("Geometric","Geométrico","Geométrico");
add("Shipping policy","Envíos","Envio");add("Returns & refunds","Devoluciones","Devoluções");
add("Stay in the pack","Únete a la manada","Entre para a matilha");add("Join","Unirme","Entrar");add("New breeds and colors first. No spam.","Nuevas razas y colores primero. Sin spam.","Novas raças e cores primeiro. Sem spam.");
add("Privacy","Privacidad","Privacidade");add("Terms","Términos","Termos");
add("Wear your best friend","Lleva puesto a tu mejor amigo","Vista seu melhor amigo");
add("Custom dog-breed tees and hoodies. Pick your breed, art style and placement, we print it to order and ship it across the US.","Camisetas y sudaderas personalizadas de razas de perro. Elige tu raza, estilo de arte y ubicación; lo imprimimos por encargo y lo enviamos a todo EE. UU.","Camisetas e moletons personalizados de raças de cachorro. Escolha a raça, o estilo de arte e a posição; imprimimos sob encomenda e enviamos para todos os EUA.");
/* garments, designs, placements */
add("Premium Tee","Camiseta Premium","Camiseta Premium");add("Heavy Hoodie","Sudadera Gruesa","Moletom Grosso");
add("Bella+Canvas 3001 - soft Airlume cotton","Bella+Canvas 3001 - suave algodón Airlume","Bella+Canvas 3001 - algodão Airlume macio");
add("Gildan 18500 - cozy heavy blend","Gildan 18500 - mezcla gruesa y cómoda","Gildan 18500 - mescla grossa e aconchegante");
add("Continuous Line","Línea Continua","Linha Contínua");add("Classic","Clásico","Clássico");add("Cool","Cool","Cool");add("Heart","Corazón","Coração");
add("Nothing","Nada","Nada");add("Head emblem","Emblema de cabeza","Emblema de cabeça");add("Big head","Cabeza grande","Cabeça grande");add("Body emblem","Emblema de cuerpo","Emblema de corpo");add("Big body","Cuerpo grande","Corpo grande");
add("Head","Cabeza","Cabeça");add("Body","Cuerpo","Corpo");add("emblem","emblema","emblema");add("large","grande","grande");
/* colors */
for(const [en,es,pt] of [["White","Blanco","Branco"],["Natural","Natural","Natural"],["Soft Cream","Crema suave","Creme suave"],["Ash","Ceniza","Cinza claro"],["Athletic Heather","Gris jaspeado","Cinza mescla"],["Light Blue","Azul claro","Azul claro"],["Soft Pink","Rosa suave","Rosa suave"],["Black","Negro","Preto"],["Navy","Azul marino","Azul-marinho"],["Forest","Verde bosque","Verde floresta"],["Maroon","Granate","Bordô"],["Sand","Arena","Areia"],["Sport Grey","Gris deportivo","Cinza esportivo"],["Light Pink","Rosa claro","Rosa claro"]])add(en,es,pt);
/* breeds */
for(const [en,es,pt] of [["French Bulldog","Bulldog Francés","Buldogue Francês"],["German Shepherd","Pastor Alemán","Pastor Alemão"],["Dachshund","Teckel (Dachshund)","Dachshund (Salsicha)"],["Standard Poodle","Caniche Estándar","Poodle Standard"],["German Shorthaired Pointer","Pointer Alemán de Pelo Corto","Pointer Alemão de Pelo Curto"],["English Bulldog","Bulldog Inglés","Buldogue Inglês"],["Australian Shepherd","Pastor Australiano","Pastor Australiano"],["Doberman Pinscher","Doberman","Dobermann"],["Pembroke Welsh Corgi","Corgi Galés de Pembroke","Corgi Galês de Pembroke"],["Miniature Schnauzer","Schnauzer Miniatura","Schnauzer Miniatura"],["Boxer","Bóxer","Boxer"],["Pomeranian","Pomerania","Lulu da Pomerânia"],["Bernese Mountain Dog","Boyero de Berna","Boiadeiro Bernês"],["Great Dane","Gran Danés","Dogue Alemão"],["Havanese","Bichón Habanero","Havanês"],["Siberian Husky","Husky Siberiano","Husky Siberiano"],["American Pit Bull Terrier","Pit Bull Terrier Americano","Pit Bull Terrier Americano"],["Mini Poodle","Caniche Mini","Poodle Mini"],["Bichon Frise","Bichón Frisé","Bichon Frisé"],["Maltese","Maltés","Maltês"]])add(en,es,pt);
/* server messages shown to the customer */
for(const [en,es,pt] of [["Your cart has an invalid item","Tu carrito tiene un artículo no válido","Seu carrinho tem um item inválido"],["Please complete the shipping address","Completa la dirección de envío","Preencha o endereço de entrega"],["Enter a valid US ZIP code","Ingresa un código postal (ZIP) válido de EE. UU.","Informe um CEP (ZIP) válido dos EUA"],["Enter a valid email","Ingresa un correo válido","Informe um e-mail válido"],["Email and message required","Correo y mensaje obligatorios","E-mail e mensagem obrigatórios"],["Log in first","Inicia sesión primero","Entre primeiro"],["Code expired. Request a new one.","El código venció. Solicita uno nuevo.","O código expirou. Peça um novo."],["Please wait a moment before requesting another code","Espera un momento antes de pedir otro código","Aguarde um momento antes de pedir outro código"],["Email service is not configured yet","El servicio de correo aún no está configurado","O serviço de e-mail ainda não está configurado"],["This sign-in is not enabled yet","Este inicio de sesión aún no está habilitado","Este login ainda não está habilitado"],["Request failed","La solicitud falló","A solicitação falhou"],["Google sign-in failed","Falló el inicio de sesión con Google","Falha no login com Google"],["Facebook sign-in failed","Falló el inicio de sesión con Facebook","Falha no login com Facebook"],["Apple sign-in failed","Falló el inicio de sesión con Apple","Falha no login com Apple"],["Sign-in was cancelled or expired","El inicio de sesión se canceló o venció","O login foi cancelado ou expirou"]])add(en,es,pt);
export const STATUS=s=>t(s);
