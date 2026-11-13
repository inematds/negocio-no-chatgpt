# negocio-no-chatgpt — business profile for AI

[![Your business on ChatGPT](guia/assets/banner-en.jpg)](https://inematds.github.io/negocio-no-chatgpt/guia/en/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

When someone asks ChatGPT where to buy what you sell, your business could show up. The business profile for AI gets everything ready in 10 minutes.

## What it is

Since November 10, 2026, ChatGPT has offered an official business listing in beta. But in Brazil, physical stores and restaurants still can’t sign up, and even businesses that can sign up only show up if the AI understands their business. **negocio-no-chatgpt** is a free toolkit for business owners who want to be found by AI: it creates a **business profile for AI** (ready-to-use text and a data block for your website) and scores your website, with a list of things to fix. It also includes step-by-step signup instructions based only on what OpenAI has confirmed. You only need a computer with Python, which is free.

## 📖 User guide

Complete guide (landing page + step-by-step instructions): **https://inematds.github.io/negocio-no-chatgpt/guia/en/**

## The feature and Brazil

**Businesses in ChatGPT** has been in beta since November 10, 2026. In **Business Hub**, eligible businesses can claim and verify their profile, update information, and connect a product feed. The facts used here come exclusively from [FONTES.md](FONTES.md) (in Portuguese).

**Brazil:** physical stores and restaurants can only claim existing profiles in the US. Online businesses can try; eligibility depends on OpenAI’s checks. Business Agent is currently only for eligible e-commerce and online services in the US. No list of countries has been published. Signing up does not guarantee sales or a particular position.

A free, public INEMA toolkit, built in Python 3 using only the standard library: no pip, no API account.

## Installation

Install Python 3 (Git is optional: you can [download the ZIP](https://github.com/inematds/negocio-no-chatgpt/archive/refs/heads/main.zip)). There are no dependencies to install. **On Windows, replace `python3` with `py`** in all commands.

```bash
git clone https://github.com/inematds/negocio-no-chatgpt
cd negocio-no-chatgpt
```

## Create your profile

```bash
python3 ficha.py
```

Answer one question at a time. For business type, enter a number or name (1 physical store, 2 restaurant, 3 local service, 4 online store, 5 online service), or a common synonym such as “bakery.” If an answer isn’t valid (type, phone, email, or website), you’ll be asked again without losing your other answers. The **business profile for AI** method creates `ficha.md`, `jsonld.html`, `jsonld.json`, and `checklist.md` in `minha-ficha/`. Review them before publishing. The script never uses the network.

To use a file with the same keys as the questions, copy and edit [respostas.json](exemplos/padaria/respostas.json). Products and services are a list; FAQs can contain up to five objects with `pergunta` and `resposta`. The example shows the exact key names. Only `nome`, `o_que_vende`, `tipo`, and at least one of `cidade` or `site` are required. Phone, WhatsApp, email, and website are validated if provided.

```bash
python3 ficha.py --de exemplos/padaria/respostas.json --saida exemplos/padaria/minha-ficha
```

Actual output:

```text
ficha do negócio para a IA gerada em exemplos/padaria/minha-ficha/
Arquivos: ficha.md, jsonld.html, jsonld.json, checklist.md
```

Paste the text from `ficha.md` into your website, profiles, and corresponding Business Hub fields, if eligible. Paste `jsonld.html` into your website’s `<head>`; `jsonld.json` contains the same data as plain JSON. Follow `checklist.md` and the [signup instructions](CADASTRO.md) (in Portuguese).

Recognized hours: `seg-sex 9h-18h, sáb 9h-13h`, `ter 9h30-18h`, `dom 09:00-12:00`. Separate time ranges with a comma or semicolon. If any part isn’t recognized, the entire `openingHours` field is omitted and the checklist will let you know; the original text remains in the profile. Hours are never guessed.

## Check your website

```bash
python3 checar_site.py exemplos/sites/bom/index.html
python3 checar_site.py https://seu-site.com.br
python3 checar_site.py seu-site.html --robots caminho/robots.txt --llms caminho/llms.txt
python3 checar_site.py exemplos/sites/bom/index.html --json
```

Excerpt from the good example’s actual output:

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

The checker uses HTMLParser to read HTML without running JavaScript. For a local file, it looks for `robots.txt` and `llms.txt` in the same folder or uses the specified paths. For a URL, it makes GET requests only, with a 15-second timeout per request, up to five redirects per resource, and reads no more than 2 MB per resource. It looks for auxiliary files at the final page’s origin. User-Agent: `negocio-no-chatgpt-checador/1.0`. Files that reach the remote read limit are rejected to prevent an incomplete analysis.

The score from 0 to 100 is a toolkit heuristic: access 30, JSON-LD 20, title/description 15, contact/location 20, visible text 10, and optional llms.txt 5. All criteria in each group must be met. If `robots.txt` is missing, access is allowed; if it can’t be checked, access is reported as unverified. GPTBot and ChatGPT-User are informational and don’t reduce the score. Blocking GPTBot (for training) does not remove your website from search.

For location, include the city from your JSON-LD in the visible text, along with a postal code or an explicit format such as `Cidade: Joinville` or `Joinville/SC`. The checker doesn’t automatically recognize every city. It recognizes common business types listed at the beginning of the code; it doesn’t download the schema.org catalog. It doesn’t check external CSS, JavaScript rendering, or IP access on the server/CDN. There is no confirmed effect of JSON-LD or llms.txt on ranking; llms.txt is optional, with no guaranteed effect.

The program returns code 0 when it can read the page, even if the score is low, and code 2 when it can’t. With `--json`, results and errors are returned as JSON. All example data is made up; don’t use the contact details as real information.

This makes your website easy for AI to read. It doesn’t guarantee a particular position: ChatGPT decides what appears.

## Offline tests

```bash
python3 testes/run.py
```

The tests block network connections and cover generation, validation, hours, HTML, robots.txt, read limits, and redirects with simulated responses.

Complete guide: https://inematds.github.io/negocio-no-chatgpt/guia/en/

## Related toolkits

- [website that sells](https://inematds.github.io/site-que-vende/guia/)
- [lead support](https://inematds.github.io/atende-leads/guia/)

MIT License, 2026 INEMA. Version 1.0.0.

**free on inema.club, right on the internet**
