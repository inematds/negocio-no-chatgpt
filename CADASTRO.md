# Passo a passo do cadastro (conferido em 13/11/2026)

**Brasil:** lojas físicas e restaurantes ainda não conseguem reivindicar fichas brasileiras: por enquanto, só fichas já existentes nos EUA. Negócios online podem tentar no Business Hub; a aprovação depende das checagens da OpenAI. O Business Agent ainda é exclusivo de e-commerce e serviços online elegíveis nos EUA. **Não há lista de países publicada.**

Businesses in ChatGPT está em beta desde 10/11/2026. Este passo a passo usa somente a seção CONFIRMADO de [FONTES.md](FONTES.md). A ficha do negócio para a IA organiza os dados; não substitui as verificações de elegibilidade.

1. Entre no ChatGPT e abra o **Business Hub**: https://chatgpt.com/business-hub (também no menu lateral da web).
2. Procure o negócio. Você precisa ser o dono ou estar autorizado a representá-lo.
3. Reivindique a ficha existente ou crie uma, conforme a elegibilidade. Para lojas físicas e restaurantes, vale a restrição às fichas já existentes nos EUA.
4. Verifique o vínculo por telefone, e-mail do negócio, registro TXT no DNS do domínio ou Shopify.
5. Faça a verificação de identidade pela **Persona**. Ela pode pedir documento oficial, registro da empresa e prova de autorização. Só depois é possível publicar mudanças, ver insights e, quando elegível, criar agente. O selo de verificado só aparece depois da Persona.
6. Preencha site, descrição, categoria, logo, política de entrega e de troca. Copie os trechos correspondentes de `ficha.md`; revise nome, endereço ou área atendida, horário, contato e produtos/serviços. A ficha não inventa logo nem política de troca: forneça os dados reais quando solicitados.
7. Se vende produtos, conecte um feed com preço e disponibilidade: CSV, arquivo hospedado ou Shopify.

Se outra pessoa já reivindicou a ficha, use **Dispute ownership**. Se aparecer **Contact support**, a ficha está travada e é preciso pedir ajuda.

Não é necessário ter conta de anúncios nem plano Enterprise. Reivindicar, anunciar e publicar agente são ações separadas. Reivindicar não garante posição melhor nem vendas. A OpenAI pode completar, editar ou não mostrar os dados enviados.

## O que fazer HOJE, em qualquer país

- Deixe o `OAI-SearchBot` acessar o site. Confira as regras existentes no `robots.txt` antes de acrescentar um grupo como este:

```text
User-agent: OAI-SearchBot
Allow: /
```

- O servidor/CDN também precisa liberar os IPs publicados da OpenAI. A mudança no `robots.txt` leva cerca de **24 h** para valer na busca. Bloquear `GPTBot` (treino) não tira o site da busca.
- Coloque o conteúdo revisado de `ficha.md` no texto visível do site.
- Cole `jsonld.html` no `<head>` e mantenha os mesmos dados visíveis na página.
- Rode `python3 checar_site.py caminho/do/site.html` ou `python3 checar_site.py https://seu-site`.

Os arquivos e a pontuação são ferramentas locais deste kit para facilitar a leitura. Não são exigências oficiais do Business Hub. O `llms.txt` é opcional e não tem garantia de efeito.

## O que NÃO está confirmado

Não há confirmação, nas fontes reunidas, de lista de países, data de chegada ao Brasil, prazo de aprovação ou custo futuro. Não está confirmado que JSON-LD, llms.txt ou uma descrição melhor elevem a posição no ChatGPT. Não há número de vendas ou visualizações garantido por cadastro.

Isso deixa o site fácil de ler para a IA. Não garante posição: quem escolhe o que aparecer é o ChatGPT.

## Fontes oficiais

- [Anúncio Businesses in ChatGPT](https://openai.com/index/introducing-businesses-chatgpt/)
- [Claim Your Business](https://openai.com/business/businesses-in-chatgpt/)
- [Setting up your business on ChatGPT](https://help.openai.com/en/articles/20001635-setting-up-your-business-on-chatgpt)
- [Política Businesses in ChatGPT](https://openai.com/policies/businesses-in-chatgpt/)
- [Release notes](https://help.openai.com/en/articles/6825453-chatgpt-release-notes)
- [Overview of OpenAI Crawlers](https://platform.openai.com/docs/bots)
- [Searching the web with ChatGPT](https://help.openai.com/en/articles/9237897-chatgpt-search)
- [Publishers and Developers – FAQ](https://help.openai.com/en/articles/12627856)
- [Anúncio no fórum oficial](https://community.openai.com/t/introducing-businesses-in-chatgpt-in-beta/1414865)
