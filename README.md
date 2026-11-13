# negocio-no-chatgpt — ficha do negócio para a IA

[![Seu negócio no ChatGPT](guia/assets/banner.jpg)](https://inematds.github.io/negocio-no-chatgpt/guia/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

🎬 Vídeo: https://www.youtube.com/watch?v=YUlRfOmXK1c · Short: https://youtube.com/shorts/oSKT2cQBAQw

Quando alguém perguntar ao ChatGPT onde comprar o que você vende, o seu negócio pode aparecer. A ficha do negócio para a IA deixa tudo pronto em 10 minutos.

## O que é

Desde 10/11/2026 o ChatGPT tem, em teste, um cadastro oficial para negócios. Mas no Brasil a loja física e o restaurante ainda não conseguem se cadastrar, e mesmo quem consegue só aparece se a IA entender o negócio. O **negocio-no-chatgpt** é um kit grátis para o dono de negócio que quer ser encontrado pela IA: ele monta a **ficha do negócio para a IA** (o texto pronto e o bloco de dados que vai no site) e dá uma nota ao seu site com a lista do que corrigir. Também traz o passo a passo do cadastro, só com o que a OpenAI confirmou. Precisa só de um computador com Python, que é grátis.

## 📖 Guia de uso

Guia completo (landing + passo a passo): **https://inematds.github.io/negocio-no-chatgpt/guia/**

## O recurso e o Brasil

**Businesses in ChatGPT** está em beta desde 10/11/2026. No **Business Hub**, negócios elegíveis podem reivindicar e verificar a ficha, atualizar informações e conectar um feed de produtos. Os fatos usados aqui vêm exclusivamente de [FONTES.md](FONTES.md).

**Brasil:** lojas físicas e restaurantes ainda só podem reivindicar fichas existentes nos EUA. Negócios online podem tentar; depende das checagens da OpenAI. O Business Agent ainda é só para e-commerce e serviços online elegíveis nos EUA. Não há lista de países publicada. Cadastro não garante vendas ou posição.

Kit público INEMA, pequeno, em Python 3, só com biblioteca padrão: sem pip, sem conta de API.

## Instalação

Tenha Python 3 instalado (Git é opcional: dá para [baixar o ZIP](https://github.com/inematds/negocio-no-chatgpt/archive/refs/heads/main.zip)). Não há dependências para instalar. **No Windows, troque `python3` por `py`** em todos os comandos.

```bash
git clone https://github.com/inematds/negocio-no-chatgpt
cd negocio-no-chatgpt
```

## Prepare a ficha

```bash
python3 ficha.py
```

Responda uma pergunta por vez. No tipo, vale o número ou o nome (1 loja física, 2 restaurante, 3 serviço local, 4 loja virtual, 5 serviço online) e sinônimos comuns como “padaria”; resposta que não serve (tipo, telefone, e-mail, site) é perguntada de novo, sem perder o resto. O método **ficha do negócio para a IA** produz `ficha.md`, `jsonld.html`, `jsonld.json` e `checklist.md` em `minha-ficha/`. Revise antes de publicar. O script nunca usa rede.

Para usar um arquivo com as mesmas chaves das perguntas, copie e edite [respostas.json](exemplos/padaria/respostas.json). Produtos/serviços são uma lista; perguntas frequentes são até cinco objetos com `pergunta` e `resposta`. Os nomes exatos das chaves estão no exemplo. Somente `nome`, `o_que_vende`, `tipo` e pelo menos um entre `cidade` e `site` são obrigatórios. Telefone, WhatsApp, e-mail e site são validados quando preenchidos.

```bash
python3 ficha.py --de exemplos/padaria/respostas.json --saida exemplos/padaria/minha-ficha
```

Saída real:

```text
ficha do negócio para a IA gerada em exemplos/padaria/minha-ficha/
Arquivos: ficha.md, jsonld.html, jsonld.json, checklist.md
```

Cole os textos de `ficha.md` no site, nos perfis e nos campos correspondentes do Business Hub, se elegível. Cole `jsonld.html` no `<head>` do site; `jsonld.json` contém os mesmos dados em JSON puro. Siga `checklist.md` e o [passo a passo do cadastro](CADASTRO.md).

Horários reconhecidos: `seg-sex 9h-18h, sáb 9h-13h`, `ter 9h30-18h`, `dom 09:00-12:00`. Separe períodos por vírgula ou ponto e vírgula. Se algum trecho não for reconhecido, o campo `openingHours` inteiro é omitido e o checklist avisa; o texto original continua na ficha. Não há adivinhação de horário.

## Confira o site

```bash
python3 checar_site.py exemplos/sites/bom/index.html
python3 checar_site.py https://seu-site.com.br
python3 checar_site.py seu-site.html --robots caminho/robots.txt --llms caminho/llms.txt
python3 checar_site.py exemplos/sites/bom/index.html --json
```

Trecho da saída real do exemplo bom:

```text
ficha do negócio para a IA — nota: 100/100

OK
- OAI-SearchBot liberado nesta página; sem meta noindex.
- JSON-LD válido com tipo de negócio.
- Título e descrição dentro dos tamanhos recomendados pelo kit.
- Contato e localização legíveis no texto da página.
- Texto visível: 198 palavras (mínimo do kit: 150).
- llms.txt presente: opcional, sem garantia de efeito.

CORRIGIR
- Nenhum item.
```

O checador usa HTMLParser e lê HTML, sem executar JavaScript. Para arquivo local, procura `robots.txt` e `llms.txt` na mesma pasta, ou usa os caminhos indicados. Para URL, faz somente GET com urllib, timeout de 15 segundos por requisição, até cinco redirecionamentos por recurso e leitura de no máximo 2 MB por recurso. Busca os arquivos auxiliares na origem da página final. User-Agent: `negocio-no-chatgpt-checador/1.0`. Arquivos que atingem o limite de leitura remota são recusados para evitar análise truncada.

A nota de 0 a 100 é uma heurística do kit: acesso 30, JSON-LD 20, título/descrição 15, contato/localização 20, texto visível 10 e llms.txt opcional 5. Os critérios de cada grupo precisam ser atendidos juntos. A ausência de robots.txt libera; falha ao consultá-lo é informada como não verificado. GPTBot e ChatGPT-User são informativos e não descontam pontos. Bloquear GPTBot (treino) não tira o site da busca.

Para localização, use cidade do JSON-LD também no texto visível, CEP ou um formato explícito como `Cidade: Joinville` ou `Joinville/SC`. O checador não reconhece todas as cidades automaticamente. Reconhece tipos comuns de negócio listados no início do código; não baixa o catálogo schema.org. Não verifica CSS externo, renderização de JavaScript ou liberação de IPs no servidor/CDN. JSON-LD e llms.txt não têm efeito em posição confirmado; llms.txt é opcional e não há garantia de efeito.

O programa retorna código 0 quando consegue ler a página, mesmo com nota baixa, e 2 quando não consegue. Em `--json`, os resultados e os erros são JSON. Os dados dos exemplos são todos inventados; não use seus contatos como dados reais.

Isso deixa o site fácil de ler para a IA. Não garante posição: quem escolhe o que aparecer é o ChatGPT.

## Testes sem rede

```bash
python3 testes/run.py
```

Os testes bloqueiam conexões de rede e cobrem geração, validação, horários, HTML, robots.txt, limites de leitura e redirecionamento com respostas simuladas.

Guia completo: https://inematds.github.io/negocio-no-chatgpt/guia/

## Kits que combinam

- [site que vende](https://inematds.github.io/site-que-vende/guia/)
- [atendimento de leads](https://inematds.github.io/atende-leads/guia/)

Licença MIT, 2026 INEMA. Versão 1.0.0.

**grátis no inema.club, direto na internet**
