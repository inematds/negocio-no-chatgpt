# FONTES — conferidas em 12–13/11/2026

Só fonte primária (OpenAI). O texto do kit e do vídeo usa apenas o que está aqui.

| # | Fonte (OpenAI) | URL | Data do conteúdo | Como foi lida |
|---|---|---|---|---|
| 1 | Anúncio "Introducing Businesses in ChatGPT" | https://openai.com/index/introducing-businesses-chatgpt/ | 10/11/2026 | índice de busca + repost oficial no fórum (o site devolve 403 ao robô) |
| 2 | Página "Businesses in ChatGPT: Claim Your Business" | https://openai.com/business/businesses-in-chatgpt/ | 11/2026 | índice de busca |
| 3 | Central de Ajuda "Setting up your business on ChatGPT" | https://help.openai.com/en/articles/20001635-setting-up-your-business-on-chatgpt | atualizado em 10/11/2026 | índice de busca (página com desafio Cloudflare para robô) |
| 4 | Política "Businesses in ChatGPT" | https://openai.com/policies/businesses-in-chatgpt/ | 11/2026 | índice de busca |
| 5 | Release notes do ChatGPT (lançamento do Business Hub) | https://help.openai.com/en/articles/6825453-chatgpt-release-notes | 10/11/2026 | índice de busca |
| 6 | Robôs da OpenAI ("Overview of OpenAI Crawlers") | https://platform.openai.com/docs/bots | lida em 13/11/2026 | lida direto (200, versão .md) |
| 7 | Central de Ajuda "Searching the web with ChatGPT" | https://help.openai.com/en/articles/9237897-chatgpt-search | lida em 13/11/2026 | índice de busca |
| 8 | Central de Ajuda "Publishers and Developers – FAQ" | https://help.openai.com/en/articles/12627856 | lida em 13/11/2026 | índice de busca |
| 9 | Fórum oficial — post "Introducing Businesses in ChatGPT in beta" (categoria Announcements) | https://community.openai.com/t/introducing-businesses-in-chatgpt-in-beta/1414865 | 10/11/2026 | lido direto |

## O que está CONFIRMADO

**O recurso** (1, 2, 3, 5, 9)
- Nome: "Businesses in ChatGPT", em **beta**, lançado em **10/11/2026**. O painel se chama **Business Hub**.
- No Business Hub o negócio **reivindica (claim) e verifica** a ficha, atualiza os dados e, se vender produtos, liga um **feed de produtos** (preço e disponibilidade; CSV, arquivo hospedado ou Shopify).
- Vê **insights agregados** dos últimos 28 dias: menções, cliques no site e temas das conversas em que o site foi citado. A OpenAI diz que **não entrega as conversas** das pessoas ao negócio.
- Reivindicar **não garante** posição melhor nem vendas; o ChatGPT continua fazendo recomendações independentes. A OpenAI pode completar, editar ou não mostrar o que o negócio enviar.
- Reivindicar, anunciar e publicar agente são coisas **separadas**: não precisa anunciar para reivindicar.

**Quem pode** (1, 3)
- Quem é dono ou está autorizado a representar o negócio. Não precisa de conta de anúncios nem de plano Enterprise.
- "Negócios elegíveis onde o ChatGPT está disponível", dependendo de local, tipo de negócio e das checagens da OpenAI. **Não há lista de países publicada.**
- **Lojas físicas e restaurantes: por enquanto só podem reivindicar uma ficha que já exista nos EUA.**
- **Business Agent** (o atendente do negócio dentro do ChatGPT): por enquanto só para **e-commerce e serviços online elegíveis nos EUA**.

**Onde e como** (3)
- Entrar no ChatGPT → Business Hub (chatgpt.com/business-hub ou menu lateral na web) → procurar o negócio → reivindicar a ficha que existe ou criar uma.
- Verificar o vínculo por **telefone, e-mail do negócio, domínio do site (registro TXT no DNS) ou Shopify**.
- Depois, **verificação de identidade pela Persona** (pode pedir documento oficial, registro da empresa e prova de autorização) — só então dá para publicar mudanças, ver insights e criar agente. O selo de verificado só aparece depois da Persona.
- Ficha já reivindicada por outro: "Dispute ownership". Ficha com "Contact support": travada, pedir ajuda.

**O que dá para preencher** (3, 4)
- Site, descrição, categoria, logo, política de entrega e de troca; a política cita nome, categoria, endereço ou área atendida, horário, contato e produtos/serviços.

**Como o ChatGPT acha sites (vale para qualquer negócio, em qualquer país)** (6, 7, 8)
- Qualquer site público pode aparecer na busca do ChatGPT. Para aparecer nas respostas, o site **não pode bloquear o robô `OAI-SearchBot`** no robots.txt (e o servidor/CDN tem que deixar passar os IPs publicados da OpenAI). Posição não é garantida.
- Robôs oficiais: `OAI-SearchBot` (busca), `GPTBot` (treino — bloquear não tira da busca), `ChatGPT-User` (quando uma pessoa pede para o ChatGPT abrir a página), `OAI-AdsBot` (só páginas de anúncio). Mudança no robots.txt leva ~24 h para valer na busca.
- Busca local: o ChatGPT usa a localização aproximada (IP) e pode usar fornecedores de fichas de negócios; ajuda escrever cidade/bairro na pergunta.

## O que NÃO está confirmado (não usar como fato)
- Lista de países, data de chegada ao Brasil, prazo de aprovação, custo futuro.
- Que JSON-LD, llms.txt ou descrição melhor façam o negócio subir no ChatGPT. O kit trata isso como **"deixar o site fácil de ler"**, não como garantia.
- Qualquer número de views/vendas por cadastrar.

## Leitura para o Brasil (como o kit fala)
- **Loja física ou restaurante no Brasil:** o cadastro ainda não abre (só fichas dos EUA). O que funciona hoje: site legível + robots.txt liberando o `OAI-SearchBot`.
- **Negócio online (loja virtual, serviço online):** pode tentar reivindicar no Business Hub; a aprovação depende das checagens da OpenAI. O agente ainda é só EUA.
