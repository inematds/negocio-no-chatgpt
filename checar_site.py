#!/usr/bin/env python3
"""Checagem de leitura do site, sem promessa de posição."""
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request

PESOS = {'acesso': 30, 'jsonld': 20, 'metadados': 15, 'contato': 20, 'texto': 10, 'llms': 5}
LIMITE = 2 * 1024 * 1024
AVISO = 'Isso deixa o site fácil de ler para a IA. Não garante posição: quem escolhe o que aparecer é o ChatGPT.'
TIPOS_NEGOCIO = {'Organization', 'LocalBusiness', 'Store', 'Restaurant', 'Bakery', 'FoodEstablishment', 'ProfessionalService', 'MedicalBusiness', 'Dentist', 'LegalService', 'AutoRepair', 'AutomotiveBusiness', 'HealthAndBeautyBusiness', 'BeautySalon', 'HairSalon', 'HomeAndConstructionBusiness', 'Plumber', 'Electrician', 'LodgingBusiness', 'Hotel', 'ShoppingCenter', 'SportsActivityLocation', 'TravelAgency', 'RealEstateAgent', 'FinancialService', 'AccountingService', 'CafeOrCoffeeShop', 'OnlineStore', 'ClothingStore', 'GroceryStore', 'HardwareStore', 'PetStore', 'Pharmacy', 'Florist', 'BookStore', 'ComputerStore', 'FurnitureStore', 'ElectronicsStore'}


def permite(robots, agente, caminho='/'):
    """Agrupa agentes, combina grupos específicos e aplica maior especificidade."""
    grupos, agentes, regras = [], [], []
    iniciou = False
    for linha in robots.splitlines():
        linha = linha.split('#', 1)[0].strip()
        if ':' not in linha:
            continue
        chave, valor = (p.strip() for p in linha.split(':', 1))
        chave = chave.lower()
        if chave == 'user-agent':
            if iniciou:
                grupos.append((agentes, regras))
                agentes, regras, iniciou = [], [], False
            agentes.append(valor.lower())
        elif agentes:
            iniciou = True
            if chave in ('allow', 'disallow') and valor:
                regras.append((chave, valor))
    grupos.append((agentes, regras))
    especificos = [r for a, r in grupos if agente.lower() in a]
    selecionados = especificos if especificos else [r for a, r in grupos if '*' in a]
    candidatos = []
    for grupo in selecionados:
        for acao, padrao in grupo:
            ancora = padrao.endswith('$')
            literal = padrao[:-1] if ancora else padrao
            regex = '^' + re.escape(literal).replace(r'\*', '.*') + ('$' if ancora else '')
            if re.search(regex, caminho):
                candidatos.append((len(literal.replace('*', '').encode('utf-8')), acao == 'allow'))
    return max(candidatos)[1] if candidatos else True


class Pagina(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.textos, self.titulos, self.blocos, self.metas = [], [], [], {}
        self.pilha = []
        self.script = None
        self.ocultos = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'meta':
            self.metas[attrs.get('name', '').lower()] = attrs.get('content', '')
        if tag in ('area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'):
            return
        oculto = tag in ('script', 'style', 'template', 'noscript', 'head') or 'hidden' in attrs or bool(re.search(r'(?:display\s*:\s*none|visibility\s*:\s*hidden)', attrs.get('style', ''), re.I))
        self.pilha.append((tag, oculto))
        self.ocultos += oculto
        if tag == 'script' and attrs.get('type', '').lower() == 'application/ld+json':
            self.script = []

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag == 'script' and self.script is not None:
            self.blocos.append(''.join(self.script))
            self.script = None
        for i in range(len(self.pilha) - 1, -1, -1):
            if self.pilha[i][0] == tag:
                self.ocultos -= sum(x[1] for x in self.pilha[i:])
                del self.pilha[i:]
                break

    def handle_data(self, data):
        if self.script is not None:
            self.script.append(data)
        if any(t == 'title' for t, _ in self.pilha):
            self.titulos.append(data)
        if not self.ocultos:
            self.textos.append(data)


def nos(valor):
    if isinstance(valor, dict):
        yield valor
        for v in valor.values():
            yield from nos(v)
    elif isinstance(valor, list):
        for v in valor:
            yield from nos(v)


def constante_invalida(valor):
    raise ValueError(f"Constante fora do padrão JSON: {valor}")


def avaliar(html, robots='', llms='', caminho='/', erros_aux=None):
    p = Pagina()
    p.feed(html)
    texto = ' '.join(p.textos)
    ok, corrigir, info = [], [], []
    nota = 0

    def item(chave, passa, bom, ruim):
        nonlocal nota
        if passa:
            nota += PESOS[chave]
            ok.append(bom)
        else:
            corrigir.append(ruim)

    erros_aux = erros_aux or {}
    livre = permite(robots, 'OAI-SearchBot', caminho)
    noindex = any('noindex' in p.metas.get(k, '').lower().split(',') or re.search(r'\bnoindex\b', p.metas.get(k, ''), re.I) for k in ('robots', 'oai-searchbot'))
    motivo = 'OAI-SearchBot bloqueado nesta página: o robô de busca da OpenAI não pode entrar. No robots.txt, deixe estas duas linhas\n    User-agent: OAI-SearchBot\n    Allow: /\n  e apague o Disallow que barra esta página. A mudança leva cerca de 24 h para valer.'
    if 'robots' in erros_aux:
        motivo = 'Não foi possível conferir robots.txt: ' + erros_aux['robots'] + '. Confira o acesso e rode novamente.'
    elif noindex:
        motivo = 'Meta robots noindex na página. Remova noindex se deseja permitir indexação.' + (' OAI-SearchBot também está bloqueado no robots.txt.' if not livre else '')
    item('acesso', livre and not noindex and 'robots' not in erros_aux, 'OAI-SearchBot liberado nesta página; sem meta noindex.', motivo)
    for agente in ('GPTBot', 'ChatGPT-User'):
        estado = 'não conferido' if 'robots' in erros_aux else ('liberado' if permite(robots, agente, caminho) else 'bloqueado')
        info.append(f'{agente}: {estado} no robots.txt para esta página.' + (' Treino: bloquear NÃO tira da busca; sem desconto de pontos.' if agente == 'GPTBot' else ' Acesso solicitado pela pessoa; informativo, sem desconto de pontos.'))
    objetos, valido = [], bool(p.blocos)
    for bloco in p.blocos:
        try:
            objetos.extend(nos(json.loads(bloco, parse_constant=constante_invalida)))
        except (ValueError, RecursionError):
            valido = False
    negocio = any(any(str(t).rsplit('/', 1)[-1] in TIPOS_NEGOCIO for t in (n.get('@type', []) if isinstance(n.get('@type'), list) else [n.get('@type')])) for n in objetos)
    item('jsonld', valido and negocio, 'JSON-LD válido com tipo de negócio.', 'Inclua JSON-LD válido com @type de negócio (Organization, LocalBusiness, Store ou Restaurant); use jsonld.html da ficha.')
    titulo, descricao = ' '.join(''.join(p.titulos).split()), p.metas.get('description', '').strip()
    item('metadados', 10 <= len(titulo) <= 70 and 50 <= len(descricao) <= 160, 'Título e descrição dentro dos tamanhos recomendados pelo kit.', f'Ajuste <title> para 10–70 caracteres (atual: {len(titulo)}) e meta description para 50–160 (atual: {len(descricao)}).')
    contato = bool(re.search(r'\b[^\s<>@]+@[^\s<>@]+\.[a-zA-Z]{2,}\b|(?<!\d)(?:\+55\s*)?\(?[1-9]\d\)?[\s.-]*\d{4,5}[\s.-]*\d{4}(?!\d)', texto))
    cidades = [str(n['addressLocality']).strip() for n in objetos if n.get('addressLocality')]
    local = bool(re.search(r'\b\d{5}-?\d{3}\b', texto) or any(c and c.casefold() in texto.casefold() for c in cidades) or re.search(r'\b(?:cidade|município)\s*:\s*[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ -]+', texto, re.I) or re.search(r'\b[A-ZÀ-Ý][a-zà-ÿ]+(?: [A-Za-zÀ-ÿ]+){0,3}\s*/\s*[A-Z]{2}\b', texto))
    item('contato', contato and local, 'Contato e localização legíveis no texto da página.', 'Escreva telefone com DDD ou e-mail e localização no texto visível (ex.: Cidade: Joinville, Joinville/SC ou CEP). Cidade só no JSON-LD não basta.')
    palavras = len(re.findall(r'\b[\wÀ-ÿ]+\b', texto))
    item('texto', palavras >= 150, f'Texto visível: {palavras} palavras (mínimo do kit: 150).', f'Publique pelo menos 150 palavras úteis no HTML visível; encontradas {palavras}. Não dependa só de JavaScript, imagens ou texto oculto.')
    item('llms', bool(llms.strip()) and 'llms' not in erros_aux, 'llms.txt presente: opcional, sem garantia de efeito.', 'llms.txt é opcional (5 pontos), sem garantia de efeito. Se quiser, crie um resumo textual do site.' + (' Não foi possível conferir: ' + erros_aux['llms'] if 'llms' in erros_aux else ''))
    info.append('A nota é uma heurística do kit, não uma avaliação do ChatGPT. CSS externo, renderização por JS e liberação de IPs pelo servidor/CDN não são verificados.')
    return {'metodo': 'ficha do negócio para a IA', 'nota': nota, 'ok': ok, 'corrigir': corrigir, 'informacoes': info, 'aviso': AVISO}


class Redirecionamentos(urllib.request.HTTPRedirectHandler):
    def __init__(self):
        self.contagem = 0

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.contagem += 1
        if self.contagem > 5:
            raise OSError('Mais de 5 redirecionamentos.')
        if urllib.parse.urlsplit(newurl).scheme not in ('http', 'https'):
            raise OSError('Redirecionamento fora de HTTP(S).')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def buscar(url):
    if urllib.parse.urlsplit(url).scheme not in ('http', 'https'):
        raise ValueError('Use uma URL http:// ou https://.')
    req = urllib.request.Request(url, headers={'User-Agent': 'negocio-no-chatgpt-checador/1.0'}, method='GET')
    opener = urllib.request.build_opener(Redirecionamentos())
    with opener.open(req, timeout=15) as resposta:
        tamanho = resposta.headers.get('Content-Length')
        if tamanho and tamanho.isdigit() and int(tamanho) > LIMITE:
            raise OSError('Conteúdo excede 2 MB.')
        dados = resposta.read(LIMITE)
        if len(dados) == LIMITE:
            raise OSError('Conteúdo atingiu o limite de 2 MB; análise cancelada para não usar conteúdo truncado.')
        charset = resposta.headers.get_content_charset() or 'utf-8'
        return dados.decode(charset, errors='replace'), resposta.geturl()


def ler_local(caminho):
    with Path(caminho).open('rb') as f:
        if Path(caminho).stat().st_size > LIMITE:
            raise OSError('Arquivo excede 2 MB.')
        return f.read(LIMITE).decode('utf-8', errors='replace')


def checar(alvo, robots=None, llms=None):
    auxiliares, erros = {}, {}
    caminho = '/'
    if alvo.startswith(('http://', 'https://')):
        html, final = buscar(alvo)
        partes = urllib.parse.urlsplit(final)
        caminho = partes.path or '/'
        if partes.query:
            caminho += '?' + partes.query
        origem = urllib.parse.urlunsplit((partes.scheme, partes.netloc, '', '', ''))
        for nome in ('robots', 'llms'):
            try:
                auxiliares[nome], _ = buscar(origem + '/' + nome + '.txt')
            except urllib.error.HTTPError as erro:
                auxiliares[nome] = ''
                if erro.code not in (404, 410):
                    erros[nome] = f'HTTP {erro.code}'
            except (OSError, ValueError, LookupError) as erro:
                auxiliares[nome], erros[nome] = '', str(erro)
    else:
        html = ler_local(alvo)
        caminho = '/' + Path(alvo).name
        for nome, explicito in (('robots', robots), ('llms', llms)):
            arquivo = Path(explicito) if explicito else Path(alvo).parent / (nome + '.txt')
            try:
                auxiliares[nome] = ler_local(arquivo)
            except FileNotFoundError:
                auxiliares[nome] = ''
                if explicito:
                    erros[nome] = 'Arquivo indicado não existe'
            except OSError as erro:
                auxiliares[nome], erros[nome] = '', str(erro)
    return avaliar(html, auxiliares['robots'], auxiliares['llms'], caminho, erros)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Checa leitura do site para a ficha do negócio para a IA.')
    parser.add_argument('alvo', metavar='ARQUIVO.html_OU_URL')
    parser.add_argument('--robots')
    parser.add_argument('--llms')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)
    try:
        resultado = checar(args.alvo, args.robots, args.llms)
    except (OSError, ValueError, LookupError) as erro:
        resultado = {'erro': f'Não foi possível ler: {erro}', 'aviso': AVISO}
        print(json.dumps(resultado, ensure_ascii=False) if args.json else resultado['erro'] + '\n' + AVISO)
        return 2
    if args.json:
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
    else:
        print(f"ficha do negócio para a IA — nota: {resultado['nota']}/100")
        for chave, rotulo in [('ok', 'OK'), ('corrigir', 'CORRIGIR'), ('informacoes', 'INFORMAÇÕES')]:
            print('\n' + rotulo)
            for item in resultado[chave]:
                print('- ' + item)
            if not resultado[chave]:
                print('- Nenhum item.')
        print('\n' + AVISO)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
