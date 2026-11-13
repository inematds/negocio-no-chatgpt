#!/usr/bin/env python3
"""Ficha do negócio para a IA: geração local, somente biblioteca padrão."""
import argparse
import json
from pathlib import Path
import re
import unicodedata

TIPOS = {'loja física': 'Store', 'restaurante': 'Restaurant', 'serviço local': 'LocalBusiness',
         'loja virtual': 'Organization', 'serviço online': 'Organization'}
PERGUNTAS = [
    ('nome', 'Qual é o nome do negócio?'), ('o_que_vende', 'O que vende, em uma frase?'),
    ('tipo', 'Qual o tipo: loja física, restaurante, serviço local, loja virtual ou serviço online?'),
    ('produtos_servicos', 'Quais os principais produtos ou serviços? Separe por vírgula ou ponto e vírgula.'),
    ('cidade', 'Qual a cidade?'), ('bairro', 'Qual o bairro?'), ('estado', 'Qual o estado (sigla)?'),
    ('endereco', 'Qual o endereço? (opcional)'), ('area_atendida', 'Qual a área atendida?'),
    ('telefone', 'Qual o telefone com DDD?'), ('whatsapp', 'Qual o WhatsApp com DDD? (opcional)'),
    ('email', 'Qual o e-mail?'), ('site', 'Qual o site, começando com https://?'),
    ('horario', 'Qual o horário? Ex.: seg-sex 9h-18h, sáb 9h-13h'),
    ('faixa_preco', 'Qual a faixa de preço? Ex.: R$ 30 a R$ 80'),
    ('pagamento', 'Quais as formas de pagamento?'), ('entrega_retirada', 'Como funciona entrega ou retirada?')]


def simples(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto.lower()) if not unicodedata.combining(c))


def converter_horario(texto):
    """Converte apenas expressões reconhecidas integralmente; nunca adivinha."""
    if not texto.strip():
        return []
    dias = dict(zip(('seg', 'ter', 'qua', 'qui', 'sex', 'sab', 'dom'), ('Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su')))
    hora = r'(\d{1,2})(?:h(\d{2})?|:(\d{2}))?'
    padrao = re.compile(r'(seg|ter|qua|qui|sex|sab|dom)(?:\s*-\s*(seg|ter|qua|qui|sex|sab|dom))?\s+' + hora + r'\s*-\s*' + hora)
    saida = []
    for parte in re.split(r'[,;]', simples(texto).replace('–', '-')):
        m = padrao.fullmatch(parte.strip())
        if not m:
            return []
        d1, d2, h1, m1, n1, h2, m2, n2 = m.groups()
        h1, h2, m1, m2 = int(h1), int(h2), int(m1 or n1 or 0), int(m2 or n2 or 0)
        if h1 > 23 or h2 > 23 or m1 > 59 or m2 > 59:
            return []
        dia = dias[d1] + ('-' + dias[d2] if d2 else '')
        saida.append(f'{dia} {h1:02d}:{m1:02d}-{h2:02d}:{m2:02d}')
    return saida


def validar(d):
    if not isinstance(d, dict):
        raise ValueError('As respostas devem ser um objeto JSON.')
    erros = []
    for chave, _ in PERGUNTAS:
        if chave == 'produtos_servicos':
            if chave in d and (not isinstance(d[chave], list) or not all(isinstance(x, str) and x.strip() for x in d[chave])):
                erros.append('produtos_servicos deve ser uma lista de textos não vazios.')
        elif chave in d and not isinstance(d[chave], str):
            erros.append(f'{chave} deve ser texto.')
    if erros:
        raise ValueError('\n'.join(erros))
    for chave, rotulo in [('nome', 'nome'), ('o_que_vende', 'o que vende'), ('tipo', 'tipo')]:
        if not d.get(chave, '').strip():
            erros.append(f'Preencha {rotulo}.')
    if d.get('tipo') not in TIPOS:
        erros.append('Escolha um tipo: ' + ', '.join(TIPOS) + '.')
    if not (d.get('cidade', '').strip() or d.get('site', '').strip()):
        erros.append('Preencha cidade ou site.')
    for chave in ('telefone', 'whatsapp'):
        valor = d.get(chave, '').strip()
        if valor and not re.fullmatch(r'(?:\+55\s*)?\(?[1-9]\d\)?[\s.-]*\d{4,5}[\s.-]*\d{4}', valor):
            erros.append(f'{chave}: informe um número brasileiro com DDD, como (47) 0000-0000.')
    if d.get('email') and not re.fullmatch(r'[^\s@]+@[^\s@]+', d['email']):
        erros.append('E-mail inválido: inclua @ e o domínio.')
    if d.get('site') and not re.fullmatch(r'https?://[^\s/?#]+(?:[^\s]*)?', d['site']):
        erros.append('Site inválido: use http:// ou https:// seguido do domínio.')
    faq = d.get('perguntas_frequentes', [])
    if not isinstance(faq, list) or len(faq) > 5 or any(not isinstance(x, dict) or any(not isinstance(x.get(k), str) or not x[k].strip() for k in ('pergunta', 'resposta')) for x in faq):
        erros.append('Use até 5 perguntas_frequentes, com pergunta e resposta preenchidas.')
    if erros:
        raise ValueError('\n'.join(erros))


def gerar(d, pasta):
    validar(d)
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    tipo = TIPOS[d['tipo']]
    negocio = {'@type': tipo, 'name': d['nome'], 'description': d['o_que_vende']}
    for chave, campo in [('site', 'url'), ('telefone', 'telephone'), ('email', 'email'), ('area_atendida', 'areaServed'), ('faixa_preco', 'priceRange'), ('pagamento', 'paymentAccepted')]:
        if d.get(chave):
            negocio[campo] = d[chave]
    if any(d.get(k) for k in ('cidade', 'estado', 'endereco')):
        endereco = {'@type': 'PostalAddress', 'addressCountry': 'BR'}
        for chave, campo in [('cidade', 'addressLocality'), ('estado', 'addressRegion'), ('endereco', 'streetAddress')]:
            if d.get(chave):
                endereco[campo] = d[chave]
        negocio['address'] = endereco
    horarios = converter_horario(d.get('horario', ''))
    if horarios:
        negocio['openingHours'] = horarios
    negocio['makesOffer'] = [{'@type': 'Offer', 'itemOffered': {'@type': 'Service' if d['tipo'].startswith('serviço') else 'Product', 'name': p}} for p in d.get('produtos_servicos', [])]
    faq = {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': p['pergunta'], 'acceptedAnswer': {'@type': 'Answer', 'text': p['resposta']}} for p in d.get('perguntas_frequentes', [])]}
    documento = {'@context': 'https://schema.org', '@graph': [negocio, faq]}
    # Escapar < impede que respostas fechem o script no HTML.
    serial = json.dumps(documento, ensure_ascii=False, indent=2).replace('<', '\\u003c')
    (pasta / 'jsonld.json').write_text(serial + '\n', encoding='utf-8')
    (pasta / 'jsonld.html').write_text('<script type="application/ld+json">\n' + serial + '\n</script>\n', encoding='utf-8')
    curta = f"{d['nome']}: {d['o_que_vende']}"
    if len(curta) > 300:
        curta = curta[:299].rstrip() + '…'
    rotulos = {'endereco': 'Endereço', 'bairro': 'Bairro', 'cidade': 'Cidade', 'estado': 'Estado', 'area_atendida': 'Área atendida', 'telefone': 'Telefone', 'whatsapp': 'WhatsApp', 'email': 'E-mail', 'site': 'Site', 'horario': 'Horário', 'faixa_preco': 'Faixa de preço', 'pagamento': 'Formas de pagamento', 'entrega_retirada': 'Entrega e retirada'}
    local = ', '.join(x for x in (d.get('bairro'), d.get('cidade'), d.get('estado')) if x)
    longa = [f"{d['nome']}: {d['o_que_vende'].rstrip('.')}."]
    if d.get('produtos_servicos'):
        longa.append('Principais produtos e serviços: ' + ', '.join(d['produtos_servicos']) + '.')
    if local:
        longa.append(f'Fica em {local}.' if d['tipo'] in ('loja física', 'restaurante') else f'Atende a partir de {local}.')
    if d.get('horario'):
        longa.append(f"Horário: {d['horario']}.")
    if d.get('faixa_preco'):
        longa.append(f"Preços: {d['faixa_preco']}.")
    linhas = ['# ficha do negócio para a IA', '', '## Descrição curta', curta, '', '## Descrição longa', ' '.join(longa), '', '## O que vende']
    linhas += ['- ' + p for p in d.get('produtos_servicos', [])] or ['Não informado.']
    for titulo, chaves in [('Onde', ('endereco', 'bairro', 'cidade', 'estado', 'area_atendida')), ('Contato', ('telefone', 'whatsapp', 'email', 'site')), ('Horário', ('horario',)), ('Preço', ('faixa_preco',)), ('Pagamento', ('pagamento',)), ('Entrega e retirada', ('entrega_retirada',))]:
        linhas += ['', '## ' + titulo] + [f'{rotulos[k]}: {d[k]}' for k in chaves if d.get(k)]
    linhas += ['', '## Perguntas frequentes']
    for p in d.get('perguntas_frequentes', []):
        linhas += ['', '### ' + p['pergunta'], p['resposta']]
    (pasta / 'ficha.md').write_text('\n'.join(linhas) + '\n', encoding='utf-8')
    checklist = ['# Checklist — ficha do negócio para a IA', '', '- Revise os dados: publique apenas informações reais do seu negócio.', '- ficha.md: copie os trechos no Sobre do site, nos perfis e nos campos correspondentes do Business Hub, se elegível. Veja CADASTRO.md na raiz do kit.', '- jsonld.html: cole o bloco no <head> do site e mantenha os mesmos dados visíveis na página.', '- jsonld.json: versão JSON pura para conferir ou usar na integração do seu site.', '- Libere OAI-SearchBot no robots.txt. A mudança leva cerca de 24 h para valer na busca.', '- Rode: python3 checar_site.py caminho/do/site.html', '- Brasil: lojas físicas e restaurantes só podem reivindicar fichas existentes nos EUA. Negócio online pode tentar; depende das checagens. Business Agent ainda só EUA.', '- JSON-LD e llms.txt não têm efeito em posição confirmado. llms.txt é opcional.']
    if not horarios:
        checklist += ['- ATENÇÃO: horário ausente ou não convertido; openingHours foi omitido. Mantenha o horário visível e tente o formato seg-sex 9h-18h, sáb 9h-13h.']
    checklist += ['', 'Isso deixa o site fácil de ler para a IA. Não garante posição: quem escolhe o que aparecer é o ChatGPT.']
    (pasta / 'checklist.md').write_text('\n'.join(checklist) + '\n', encoding='utf-8')
    return documento


def interativo():
    print('ficha do negócio para a IA — deixe em branco o que não se aplica.')
    d = {}
    for chave, pergunta in PERGUNTAS:
        valor = input(pergunta + '\n> ').strip()
        d[chave] = [p.strip() for p in re.split(r'[;,]', valor) if p.strip()] if chave == 'produtos_servicos' else valor
    d['perguntas_frequentes'] = []
    for i in range(5):
        pergunta = input(f'Pergunta frequente {i + 1} (Enter para terminar):\n> ').strip()
        if not pergunta:
            break
        resposta = input('Qual a resposta?\n> ').strip()
        d['perguntas_frequentes'].append({'pergunta': pergunta, 'resposta': resposta})
    return d


def main():
    parser = argparse.ArgumentParser(description='Cria a ficha do negócio para a IA, sem rede.')
    parser.add_argument('--de', metavar='RESPOSTAS.json')
    parser.add_argument('--saida', default='minha-ficha', metavar='PASTA')
    args = parser.parse_args()
    try:
        d = json.loads(Path(args.de).read_text(encoding='utf-8')) if args.de else interativo()
        gerar(d, args.saida)
    except (OSError, ValueError, EOFError) as erro:
        print(f'Não foi possível gerar a ficha: {erro}')
        return 2
    print(f'ficha do negócio para a IA gerada em {args.saida}/')
    print('Arquivos: ficha.md, jsonld.html, jsonld.json, checklist.md')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
