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

/* new product lines */
for(const [en,es,pt] of [["Tees, hoodies & tanks","Camisetas, sudaderas y tank tops","Camisetas, moletons e regatas"],["Polos","Polos","Polos"],["Caps","Gorras","Bonés"],
["Tank Top","Tank top unisex","Regata unissex"],["Women's Racerback Tank","Tank top deportivo de mujer","Regata nadador feminina"],["Polo Shirt","Polo","Camisa polo"],["Women's Polo","Polo de mujer","Polo feminina"],
["Dad Hat","Gorra dad hat","Boné dad hat"],["Foam Trucker Hat","Gorra trucker de espuma","Boné trucker de espuma"],["Mesh Trucker Cap","Gorra trucker de malla","Boné trucker de tela"],
["Bella+Canvas 3480 - soft jersey tank","Bella+Canvas 3480 - tank de jersey suave","Bella+Canvas 3480 - regata de malha macia"],["Next Level 1533 - lightweight racerback","Next Level 1533 - espalda deportiva ligera","Next Level 1533 - nadador leve"],
["JERZEES 443M - classic piqué, chest print","JERZEES 443M - piqué clásico, estampado en el pecho","JERZEES 443M - piquet clássico, estampa no peito"],["CORE365 Origin - performance piqué, chest print","CORE365 Origin - piqué técnico, estampado en el pecho","CORE365 Origin - piquet esportivo, estampa no peito"],
["Yupoong 6245CM - soft, low profile","Yupoong 6245CM - suave, perfil bajo","Yupoong 6245CM - macio, perfil baixo"],["OTTO 39-165 - retro foam front, mesh back","OTTO 39-165 - frente de espuma retro, malla atrás","OTTO 39-165 - frente de espuma retrô, tela atrás"],["Yupoong 6006 - 5-panel, mesh back","Yupoong 6006 - 5 paneles, malla atrás","Yupoong 6006 - 5 gomos, tela atrás"],
["One size","Talla única","Tamanho único"],["Mint","Menta","Menta"],["Tahiti Blue","Azul Tahití","Azul Taiti"],["Light Orange","Naranja claro","Laranja claro"],["Heather Grey","Gris jaspeado","Cinza mescla"],["Platinum","Platino","Platina"],["Charity Pink","Rosa","Rosa"],["Stone","Piedra","Pedra"],["Khaki","Caqui","Cáqui"],["Pink","Rosa","Rosa"],["Pink Trim","Detalles rosa","Detalhes rosa"],["Blue Trim","Detalles azules","Detalhes azuis"],
["Bella+Canvas 3480 unisex jersey tank: about 4.2 oz, 100% Airlume combed and ring-spun cotton (heathers include polyester). Soft, light and breathable with a retail fit.","Tank top unisex Bella+Canvas 3480: unas 4.2 oz, 100% algodón Airlume peinado e hilado en anillo (los jaspeados incluyen poliéster). Suave, ligera y transpirable, de corte clásico.","Regata unissex Bella+Canvas 3480: cerca de 4,2 oz, 100% algodão Airlume penteado e fiado em anel (as mescladas têm poliéster). Macia, leve e respirável, caimento tradicional."],
["Next Level 1533 women's ideal racerback tank: about 3.9 oz cotton and polyester blend, slim racerback cut that sits close to the body. Size up for a looser fit.","Tank top Next Level 1533 de mujer con espalda deportiva: unas 3.9 oz de mezcla de algodón y poliéster, corte entallado. Elige una talla más para un ajuste holgado.","Regata nadador feminina Next Level 1533: cerca de 3,9 oz de mescla de algodão e poliéster, corte ajustado ao corpo. Escolha um tamanho maior para ficar mais solta."],
["JERZEES 443M men's piqué polo: breathable cotton-blend piqué, ribbed collar and three-button placket. The dog is printed on the chest.","Polo de piqué JERZEES 443M: piqué transpirable de mezcla de algodón, cuello acanalado y tapeta de tres botones. El perro va estampado en el pecho.","Polo de piquet JERZEES 443M: piquet respirável de mescla de algodão, gola canelada e carcela de três botões. O cachorro é estampado no peito."],
["CORE365 Origin women's performance piqué polo: moisture-wicking, snag-resistant polyester with a feminine fit. The dog is printed on the chest.","Polo técnica CORE365 Origin de mujer: poliéster que absorbe la humedad y resiste enganchones, con corte femenino. El perro va estampado en el pecho.","Polo esportiva feminina CORE365 Origin: poliéster que absorve o suor e resiste a puxões, com corte feminino. O cachorro é estampado no peito."],
["Yupoong 6245CM classic dad cap: unstructured six-panel cotton twill, low profile, curved visor and adjustable strap. Printed front (sharper than embroidery for fine line art).","Gorra dad hat Yupoong 6245CM: sarga de algodón de seis paneles sin estructura, perfil bajo, visera curva y correa ajustable. Frente estampado (más nítido que el bordado para arte de línea fina).","Boné dad hat Yupoong 6245CM: sarja de algodão de seis gomos sem estrutura, perfil baixo, aba curva e ajuste traseiro. Frente estampada (mais nítida que bordado para arte de linha fina)."],
["OTTO 39-165 foam trucker hat: retro high-crown foam front, breathable mesh back and snapback closure. Printed front.","Gorra trucker OTTO 39-165: frente alto de espuma estilo retro, malla transpirable atrás y cierre snapback. Frente estampado.","Boné trucker OTTO 39-165: frente alta de espuma estilo retrô, tela respirável atrás e fecho snapback. Frente estampada."],
["Yupoong 6006 five-panel trucker cap: structured front, mesh back, snapback closure. Printed front.","Gorra trucker Yupoong 6006 de cinco paneles: frente estructurado, malla atrás y cierre snapback. Frente estampado.","Boné trucker Yupoong 6006 de cinco gomos: frente estruturada, tela atrás e fecho snapback. Frente estampada."]])add(en,es,pt);
for(const z of ["XS","S","M","L","XL","2XL","3XL"]){D.es[z]=z;D.pt[z]=z}
add("Finished with the AlphaDog logo label.","Terminado con la etiqueta del logo de AlphaDog.","Acabamento com a etiqueta do logo AlphaDog.");
add("Custom design","Diseño personalizado","Design personalizado");
add("Didn't find your breed?","¿No encontraste tu raza?","Não encontrou sua raça?");
add("Doesn't quite look like your dog? Send us a few photos and our artist will draw your own dog in our style, ready for any tee, hoodie, tank, polo or cap.","¿No se parece del todo a tu perro? Envíanos algunas fotos y nuestro artista dibujará a tu propio perro en nuestro estilo, listo para cualquier camiseta, sudadera, tank top, polo o gorra.","Não se parece muito com o seu cachorro? Envie algumas fotos e nosso artista vai desenhar o seu próprio cachorro no nosso estilo, pronto para qualquer camiseta, moletom, regata, polo ou boné.");
add("Get a custom design","Pide un diseño personalizado","Peça um design personalizado");
add("Your dog, drawn just for you","Tu perro, dibujado solo para ti","Seu cachorro, desenhado só para você");
add("Tell us about your dog and send photos. We reply by email with a preview on your products and a quote. You only pay if you love it.","Cuéntanos sobre tu perro y envía fotos. Te respondemos por correo con una vista previa en tus productos y una cotización. Solo pagas si te encanta.","Conte sobre o seu cachorro e envie fotos. Respondemos por e-mail com uma prévia nos seus produtos e um orçamento. Você só paga se amar.");
add("Photo checklist (at least 5)","Lista de fotos (mínimo 5)","Lista de fotos (mínimo 5)");
add("Full body, standing, seen from the side","Cuerpo entero, de pie, visto de lado","Corpo inteiro, em pé, visto de lado");
add("Sitting, facing the camera","Sentado, mirando a la cámara","Sentado, olhando para a câmera");
add("A sharp close-up of the face, straight on","Un primer plano nítido de la cara, de frente","Um close nítido do rosto, de frente");
add("The face from the side or at an angle","La cara de lado o en ángulo","O rosto de lado ou em ângulo");
add("Any favorite photo that shows their personality","Tu foto favorita que muestre su personalidad","Sua foto favorita que mostre a personalidade dele");
add("Use bright, natural light, no filters, and let your dog fill the frame with the eyes clearly visible.","Usa luz natural y brillante, sin filtros, y que tu perro llene la foto con los ojos bien visibles.","Use luz natural e clara, sem filtros, e deixe o cachorro preencher a foto com os olhos bem visíveis.");
add("You","Tus datos","Seus dados");
add("Your name","Tu nombre","Seu nome");
add("Your dog","Tu perro","Seu cachorro");
add("Dog's name","Nombre del perro","Nome do cachorro");
add("Breed or mix","Raza o mezcla","Raça ou mistura");
add("e.g. Labrador and poodle mix","p. ej. mezcla de labrador y caniche","ex.: mistura de labrador com poodle");
add("Coat colors","Colores del pelaje","Cores da pelagem");
add("e.g. black and tan, cream, merle","p. ej. negro y fuego, crema, merle","ex.: preto e marrom, creme, merle");
add("Markings and patches","Marcas y manchas","Marcas e manchas");
add("e.g. white chest, spot over one eye, brindle","p. ej. pecho blanco, mancha en un ojo, atigrado","ex.: peito branco, mancha em um olho, tigrado");
add("Ears","Orejas","Orelhas");
add("e.g. pointy, floppy, one up one down","p. ej. puntiagudas, caídas, una arriba y otra abajo","ex.: em pé, caídas, uma pra cima e outra pra baixo");
add("Tail","Cola","Rabo");
add("e.g. curly, long, short","p. ej. rizada, larga, corta","ex.: enrolado, longo, curto");
add("Anything special we should capture?","¿Algo especial que debamos captar?","Algo especial que devemos capturar?");
add("Haircut, collar, favorite toy, missing tooth...","Corte de pelo, collar, juguete favorito, un diente que falta...","Tosa, coleira, brinquedo favorito, um dente faltando...");
add("Style","Estilo","Estilo");
add("Art style","Estilo de arte","Estilo de arte");
add("Mood","Ánimo","Clima");
add("Not sure, surprise me","No estoy seguro, sorpréndeme","Não sei, me surpreenda");
add("Which products do you want?","¿Qué productos quieres?","Quais produtos você quer?");
add("About how many pieces?","¿Cuántas piezas aproximadamente?","Quantas peças, mais ou menos?");
add("Notes","Notas","Observações");
add("Photos","Fotos","Fotos");
add("Tap to add photos","Toca para añadir fotos","Toque para adicionar fotos");
add("Send my request","Enviar mi solicitud","Enviar meu pedido");
add("No payment now. We email you a preview and a quote first.","No pagas nada ahora. Primero te enviamos una vista previa y una cotización.","Nada a pagar agora. Primeiro enviamos uma prévia e um orçamento.");
add("Sending…","Enviando…","Enviando…");
add("Please add at least 5 photos of your dog","Añade al menos 5 fotos de tu perro","Adicione pelo menos 5 fotos do seu cachorro");
add("Choose at least one product","Elige al menos un producto","Escolha pelo menos um produto");
add("One of the photos could not be used. Please use JPG or PNG photos.","Una de las fotos no se pudo usar. Usa fotos JPG o PNG.","Uma das fotos não pôde ser usada. Use fotos JPG ou PNG.");
add("Please send 12 photos or fewer","Envía 12 fotos o menos","Envie 12 fotos ou menos");
add("This custom design is not ready to order yet","Este diseño personalizado aún no está listo para pedir","Este design personalizado ainda não está pronto para pedir");
add("We could not find that request. Check the link in your email.","No encontramos esa solicitud. Revisa el enlace de tu correo.","Não encontramos esse pedido. Confira o link no seu e-mail.");
add("Request received","Solicitud recibida","Pedido recebido");
add("Our artist is drawing","Nuestro artista está dibujando","Nosso artista está desenhando");
add("Preview ready","Vista previa lista","Prévia pronta");
add("Ordered","Pedido","Encomendado");
add("Thank you! Request sent.","¡Gracias! Solicitud enviada.","Obrigado! Pedido enviado.");
add("Your custom design","Tu diseño personalizado","Seu design personalizado");
add("Here is your dog in our style. Pick any product, color and placement in the designer.","Aquí está tu perro en nuestro estilo. Elige cualquier producto, color y ubicación en el diseñador.","Aqui está o seu cachorro no nosso estilo. Escolha qualquer produto, cor e posição no criador.");
add("One-time design fee","Tarifa única de diseño","Taxa única de design");
add("added once to your first order","se suma una sola vez a tu primer pedido","cobrada uma única vez no primeiro pedido");
add("Design your products","Diseña tus productos","Crie seus produtos");
add("We have your photos. Our artist will email you a preview and a quote, usually within 2 to 4 business days. Keep this link to check progress.","Tenemos tus fotos. Nuestro artista te enviará una vista previa y una cotización por correo, normalmente en 2 a 4 días hábiles. Guarda este enlace para ver el progreso.","Recebemos suas fotos. Nosso artista vai enviar uma prévia e um orçamento por e-mail, normalmente em 2 a 4 dias úteis. Guarde este link para acompanhar.");
add("Custom design (one-time)","Diseño personalizado (pago único)","Design personalizado (pagamento único)");
add("Support","Soporte","Suporte");
add("Email us any time at","Escríbenos cuando quieras a","Escreva para nós quando quiser em");
add("Questions about an order, a missing breed or anything else? Send us a message and we will reply by email, usually within 1 to 2 business days. Please include your order number if you have one.","¿Dudas sobre un pedido, una raza que falta o cualquier otra cosa? Envíanos un mensaje y te responderemos por correo, normalmente en 1 a 2 días hábiles. Incluye tu número de pedido si lo tienes.","Dúvidas sobre um pedido, uma raça que falta ou qualquer outra coisa? Envie uma mensagem e responderemos por e-mail, normalmente em 1 a 2 dias úteis. Inclua o número do pedido, se tiver.");
add("One-time design fee: {0}","Tarifa única de diseño: {0}","Taxa única de design: {0}");
add("Pay it once, then put your dog on any product at regular prices, as often as you like.","La pagas una vez y luego pones a tu perro en cualquier producto a precio normal, cuantas veces quieras.","Você paga uma vez e depois coloca seu cachorro em qualquer produto pelo preço normal, quantas vezes quiser.");
export const STATUS=s=>t(s);
