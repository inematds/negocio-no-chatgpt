#!/usr/bin/env python3
"""Testes de comportamento sem rede, sem dependências externas."""
import ast
from contextlib import redirect_stdout
from email.message import Message
import io
import json
from pathlib import Path
import socket
import sys
import tempfile
import unittest
from unittest.mock import patch
import urllib.request
import urllib.error

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import ficha
import checar_site as site

BASE = json.loads((RAIZ / 'exemplos/padaria/respostas.json').read_text(encoding='utf-8'))
BOM = (RAIZ / 'exemplos/sites/bom/index.html').read_text(encoding='utf-8')


class Testes(unittest.TestCase):
    def gerar(self, dados=None):
        with tempfile.TemporaryDirectory() as pasta:
            obj = ficha.gerar(BASE if dados is None else dados, pasta)
            arquivos = {p.name: p.read_text(encoding='utf-8') for p in Path(pasta).iterdir()}
        return obj, arquivos

    def test_ficha_exemplo_quatro_arquivos(self):
        obj, arquivos = self.gerar()
        self.assertEqual(set(arquivos), {'ficha.md', 'jsonld.html', 'jsonld.json', 'checklist.md'})
        self.assertEqual(json.loads(arquivos['jsonld.json']), obj)
        self.assertIn('Joinville', arquivos['ficha.md'])

    def test_jsonld_graph_faq(self):
        obj, _ = self.gerar()
        self.assertEqual(obj['@graph'][1]['@type'], 'FAQPage')
        self.assertEqual(len(obj['@graph'][1]['mainEntity']), 2)
        self.assertEqual(obj['@graph'][1]['mainEntity'][0]['acceptedAnswer']['text'], BASE['perguntas_frequentes'][0]['resposta'])

    def test_jsonld_script_valido(self):
        obj, arquivos = self.gerar()
        p = site.Pagina()
        p.feed(arquivos['jsonld.html'])
        self.assertEqual(json.loads(p.blocos[0]), obj)

    def test_escape_fechamento_script(self):
        _, arquivos = self.gerar(dict(BASE, nome='Teste </script><script>alert(1)</script>'))
        self.assertEqual(arquivos['jsonld.html'].count('</script>'), 1)
        self.assertIn('</script>', json.loads(arquivos['jsonld.json'])['@graph'][0]['name'])

    def test_descricao_curta_limite(self):
        _, arquivos = self.gerar(dict(BASE, o_que_vende='Produto ' * 100))
        curta = arquivos['ficha.md'].split('## Descrição curta\n')[1].split('\n')[0]
        self.assertLessEqual(len(curta), 300)

    def test_online_sem_endereco(self):
        obj, _ = self.gerar({'nome': 'Exemplo', 'o_que_vende': 'Serviço fictício', 'tipo': 'serviço online', 'site': 'https://exemplo.com.br'})
        self.assertNotIn('address', obj['@graph'][0])

    def test_campos_jsonld(self):
        obj, _ = self.gerar()
        n = obj['@graph'][0]
        self.assertEqual(n['address']['addressCountry'], 'BR')
        self.assertEqual(n['openingHours'], ['Mo-Fr 09:00-18:00', 'Sa 09:00-13:00'])
        self.assertEqual(n['makesOffer'][0]['itemOffered']['@type'], 'Product')
        for chave in ('telephone', 'email', 'url', 'areaServed', 'paymentAccepted', 'priceRange'):
            self.assertIn(chave, n)

    def test_servico_offer(self):
        obj, _ = self.gerar(dict(BASE, tipo='serviço local'))
        self.assertEqual(obj['@graph'][0]['makesOffer'][0]['itemOffered']['@type'], 'Service')

    def test_horario_invalido_avisa(self):
        obj, arquivos = self.gerar(dict(BASE, horario='quando abrir'))
        self.assertNotIn('openingHours', obj['@graph'][0])
        self.assertIn('omitido', arquivos['checklist.md'])
        self.assertIn('quando abrir', arquivos['ficha.md'])

    def test_interativo_perguntas(self):
        respostas = ['; '.join(BASE.get(k, [])) if k == 'produtos_servicos' else BASE.get(k, '') for k, _ in ficha.PERGUNTAS] + ['Aceita encomenda?', 'Sim, exemplo.', '']
        with patch('builtins.input', side_effect=respostas), redirect_stdout(io.StringIO()):
            d = ficha.interativo()
        ficha.validar(d)
        self.assertEqual(d['perguntas_frequentes'][0]['resposta'], 'Sim, exemplo.')

    def test_modo_arquivo_nao_pergunta(self):
        with tempfile.TemporaryDirectory() as pasta, patch.object(sys, 'argv', ['ficha.py', '--de', str(RAIZ / 'exemplos/padaria/respostas.json'), '--saida', pasta]), patch('builtins.input', side_effect=AssertionError('Não perguntar')), redirect_stdout(io.StringIO()):
            self.assertEqual(ficha.main(), 0)
            self.assertTrue((Path(pasta) / 'ficha.md').is_file())

    def test_ficha_sem_imports_rede(self):
        arvore = ast.parse((RAIZ / 'ficha.py').read_text())
        imports = []
        for n in ast.walk(arvore):
            if isinstance(n, ast.Import):
                imports += [a.name for a in n.names]
            elif isinstance(n, ast.ImportFrom):
                imports.append(n.module or '')
        self.assertFalse(any(x.split('.')[0] in ('urllib', 'socket', 'http', 'requests') for x in imports))

    def test_meta_noindex(self):
        r = site.avaliar(BOM.replace('</head>', '<meta name="robots" content="follow, noindex"></head>'), llms='Opcional')
        self.assertEqual(r['nota'], 70)
        self.assertIn('noindex', ' '.join(r['corrigir']))

    def test_contato_so_jsonld_nao_basta(self):
        html = '<html><head>' + self.gerar()[1]['jsonld.html'] + '</head><body>Joinville</body></html>'
        self.assertIn('Escreva telefone', ' '.join(site.avaliar(html)['corrigir']))

    def test_oculta_script_style_hidden(self):
        p = site.Pagina()
        p.feed('<head><title>segredo</title></head><body><script>invisível</script><style>invisível</style><div hidden>invisível</div><p style="display:none">invisível</p><template>invisível</template><p>visível</p></body>')
        self.assertEqual(''.join(p.textos), 'visível')

    def test_jsonld_invalido(self):
        r = site.avaliar(BOM.replace('"@graph":', '"@graph" quebrado:'))
        self.assertIn('Inclua JSON-LD', ' '.join(r['corrigir']))

    def test_jsonld_nan_nao_e_json_valido(self):
        r = site.avaliar(BOM.replace('"@context":', '"valor_invalido": NaN, "@context":'))
        self.assertIn('Inclua JSON-LD', ' '.join(r['corrigir']))

    def test_auxiliares_404_liberam(self):
        erro = urllib.error.HTTPError('https://exemplo.com.br/robots.txt', 404, 'Ausente', {}, None)
        with patch.object(site, 'buscar', side_effect=[(BOM, 'https://exemplo.com.br/'), erro, erro]):
            r = site.checar('https://exemplo.com.br/')
        self.assertEqual(r['nota'], 95)
        self.assertIn('OAI-SearchBot liberado', ' '.join(r['ok']))

    def test_auxiliares_503_nao_liberam(self):
        erro = urllib.error.HTTPError('https://exemplo.com.br/robots.txt', 503, 'Indisponível', {}, None)
        with patch.object(site, 'buscar', side_effect=[(BOM, 'https://exemplo.com.br/'), erro, ('Resumo', '')]):
            r = site.checar('https://exemplo.com.br/')
        self.assertEqual(r['nota'], 70)
        self.assertIn('HTTP 503', ' '.join(r['corrigir']))

    def test_pesos_somam_cem(self):
        self.assertEqual(sum(site.PESOS.values()), 100)

    def test_llms_opcional_cinco_pontos(self):
        self.assertEqual(site.avaliar(BOM, llms='Resumo')['nota'] - site.avaliar(BOM)['nota'], 5)
        self.assertIn('opcional', ' '.join(site.avaliar(BOM)['corrigir']))

    def test_erro_robots_nao_libera(self):
        r = site.avaliar(BOM, erros_aux={'robots': 'HTTP 503'})
        self.assertIn('Não foi possível conferir robots.txt', ' '.join(r['corrigir']))
        self.assertIn('não conferido', ' '.join(r['informacoes']))

    def test_cli_json(self):
        saida = io.StringIO()
        with redirect_stdout(saida):
            codigo = site.main([str(RAIZ / 'exemplos/sites/bom/index.html'), '--json'])
        self.assertEqual(codigo, 0)
        r = json.loads(saida.getvalue())
        self.assertEqual(r['nota'], 100)
        self.assertEqual(r['aviso'], site.AVISO)

    def test_cli_nota_baixa_codigo_zero(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(site.main([str(RAIZ / 'exemplos/sites/so-js/index.html')]), 0)

    def test_cli_arquivo_ausente_codigo_dois(self):
        saida = io.StringIO()
        with tempfile.TemporaryDirectory() as pasta, redirect_stdout(saida):
            self.assertEqual(site.main([str(Path(pasta) / 'ausente.html'), '--json']), 2)
        self.assertIn('erro', json.loads(saida.getvalue()))

    def test_auxiliares_explicitos(self):
        r = site.checar(str(RAIZ / 'exemplos/sites/bom/index.html'), str(RAIZ / 'exemplos/sites/bloqueado/robots.txt'))
        self.assertEqual(r['nota'], 70)

    def test_local_limite(self):
        with tempfile.TemporaryDirectory() as pasta:
            p = Path(pasta) / 'grande.html'
            p.write_bytes(b'x' * (site.LIMITE + 1))
            with self.assertRaises(OSError):
                site.ler_local(p)

    def test_url_get_limite_timeout_user_agent(self):
        class Resposta(io.BytesIO):
            headers = Message()
            def geturl(self):
                return 'https://exemplo.com.br/'
        resposta = Resposta(b'<html>Teste</html>')
        class Abridor:
            def open(self, req, timeout):
                Testes.assertEqual(self_teste, req.get_method(), 'GET')
                Testes.assertEqual(self_teste, timeout, 15)
                Testes.assertEqual(self_teste, req.get_header('User-agent'), 'negocio-no-chatgpt-checador/1.0')
                return resposta
        self_teste = self
        with patch('urllib.request.build_opener', return_value=Abridor()):
            self.assertEqual(site.buscar('https://exemplo.com.br/')[0], '<html>Teste</html>')

    def test_url_corpo_limitado(self):
        class Resposta(io.BytesIO):
            headers = Message()
        resposta = Resposta(b'x' * (site.LIMITE + 50))
        with patch('urllib.request.build_opener') as op:
            op.return_value.open.return_value = resposta
            with self.assertRaises(OSError):
                site.buscar('https://exemplo.com.br/')
            self.assertEqual(resposta.tell() if not resposta.closed else site.LIMITE, site.LIMITE)

    def test_redirecionamentos_maximo_cinco(self):
        r = site.Redirecionamentos()
        req = urllib.request.Request('https://exemplo.com.br/')
        for _ in range(5):
            self.assertIsNotNone(r.redirect_request(req, None, 302, '', {}, 'https://exemplo.com.br/outra'))
        with self.assertRaises(OSError):
            r.redirect_request(req, None, 302, '', {}, 'https://exemplo.com.br/seis')

    def test_redirecionamento_nao_http(self):
        with self.assertRaises(OSError):
            site.Redirecionamentos().redirect_request(urllib.request.Request('https://exemplo.com.br'), None, 302, '', {}, 'file:///tmp/exemplo')

    def test_url_auxiliares_mesma_origem(self):
        with patch.object(site, 'buscar', side_effect=[(BOM, 'https://exemplo.com.br/loja'), ('', ''), ('Resumo', '')]) as buscar:
            r = site.checar('https://exemplo.com.br')
        self.assertEqual(r['nota'], 100)
        self.assertEqual([c.args[0] for c in buscar.call_args_list], ['https://exemplo.com.br', 'https://exemplo.com.br/robots.txt', 'https://exemplo.com.br/llms.txt'])

    def test_rede_bloqueada_na_suite(self):
        with self.assertRaises(AssertionError):
            urllib.request.urlopen('https://exemplo.com.br')
        with self.assertRaises(AssertionError):
            socket.create_connection(('exemplo.com.br', 443))


def horario_teste(entrada, esperado):
    def teste(self):
        self.assertEqual(ficha.converter_horario(entrada), esperado)
    return teste


for i, (entrada, esperado) in enumerate([
    ('seg-sex 9h-18h', ['Mo-Fr 09:00-18:00']), ('sáb 9h30-13h', ['Sa 09:30-13:00']),
    ('dom 09:00-12:30', ['Su 09:00-12:30']), ('ter 9-18', ['Tu 09:00-18:00']),
    ('qua 8h-12h; qui 13h-17h', ['We 08:00-12:00', 'Th 13:00-17:00']),
    ('seg-sex 9h-18h, sáb 9h-13h', ['Mo-Fr 09:00-18:00', 'Sa 09:00-13:00']),
    ('sex 22h-2h', ['Fr 22:00-02:00']), ('todos os dias', []), ('', []),
    ('seg 25h-26h', []), ('seg 9h70-18h', []), ('seg 9h-18h, feriados fechado', [])]):
    setattr(Testes, f'test_horario_{i+1:02}', horario_teste(entrada, esperado))

for i, (tipo, esperado) in enumerate(ficha.TIPOS.items()):
    def teste(self, tipo=tipo, esperado=esperado):
        self.assertEqual(self.gerar(dict(BASE, tipo=tipo))[0]['@graph'][0]['@type'], esperado)
    setattr(Testes, f'test_tipo_{i+1:02}', teste)

for i, alteracao in enumerate([{'nome': ''}, {'o_que_vende': ''}, {'tipo': ''}, {'tipo': 'outro'}, {'cidade': '', 'site': ''}, {'telefone': '0000-0000'}, {'email': 'sem-arroba'}, {'site': 'www.exemplo.com.br'}, {'whatsapp': 'abc'}, {'perguntas_frequentes': [{'pergunta': 'X', 'resposta': ''}]}, {'perguntas_frequentes': [{'pergunta': 'X', 'resposta': 'Y'}] * 6}, {'produtos_servicos': 'Pão'}, {'nome': 12}, {'site': 'https://'}]):
    def teste(self, alteracao=alteracao):
        with self.assertRaises(ValueError):
            ficha.validar(dict(BASE, **alteracao))
    setattr(Testes, f'test_validacao_{i+1:02}', teste)

for nome, nota, esperado in [('bom', 100, 'OAI-SearchBot liberado'), ('bloqueado', 70, 'OAI-SearchBot bloqueado'), ('so-js', 30, 'encontradas 0'), ('curinga', 70, 'OAI-SearchBot bloqueado'), ('so-gptbot', 100, 'GPTBot: bloqueado')]:
    def teste(self, nome=nome, nota=nota, esperado=esperado):
        r = site.checar(str(RAIZ / 'exemplos/sites' / nome / 'index.html'))
        self.assertEqual(r['nota'], nota)
        self.assertIn(esperado, json.dumps(r, ensure_ascii=False))
    setattr(Testes, 'test_site_' + nome.replace('-', '_'), teste)

for i, (robots, caminho, esperado) in enumerate([
    ('User-agent: *\nDisallow: /', '/', False),
    ('User-agent: *\nDisallow: /\nUser-agent: OAI-SearchBot\nAllow: /', '/', True),
    ('User-agent: OAI-SearchBot\nDisallow: /\nAllow: /publico', '/publico/a', True),
    ('User-agent: OAI-SearchBot\nDisallow:', '/', True),
    ('User-agent: GPTBot\nDisallow: /', '/', True),
    ('User-agent: OAI-SearchBot\nDisallow: /\nAllow: /', '/', True),
    ('User-agent: OAI-SearchBot\nDisallow: /privado\nAllow: /', '/privado/a', False),
    ('User-agent: GPTBot\nUser-agent: OAI-SearchBot\nDisallow: /', '/', False),
    ('User-agent: OAI-SearchBot\nDisallow: /*.pdf$', '/arquivo.pdf', False),
    ('User-agent: OAI-SearchBot\nDisallow: /*.pdf$', '/arquivo.pdfx', True),
    ('User-agent: OAI-SearchBot\nDisallow: /\nUser-agent: OAI-SearchBot\nAllow: /ok', '/ok', True),
    ('USER-AGENT: oai-searchbot # comentário\nDISALLOW: /', '/', False),
    ('User-agent: *\nDisallow: /\nUser-agent: OAI-SearchBot\nDisallow:', '/', True),
    ('', '/', True),
]):
    def teste(self, robots=robots, caminho=caminho, esperado=esperado):
        self.assertEqual(site.permite(robots, 'OAI-SearchBot', caminho), esperado)
    setattr(Testes, f'test_robots_{i+1:02}', teste)


if __name__ == '__main__':
    with patch('urllib.request.urlopen', side_effect=AssertionError('Rede proibida nos testes')), patch('urllib.request.OpenerDirector.open', side_effect=AssertionError('Rede proibida nos testes')), patch('socket.create_connection', side_effect=AssertionError('Rede proibida nos testes')), patch('socket.socket.connect', side_effect=AssertionError('Rede proibida nos testes')), patch('socket.socket.connect_ex', side_effect=AssertionError('Rede proibida nos testes')), patch('socket.getaddrinfo', side_effect=AssertionError('Rede proibida nos testes')):
        resultado = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Testes))
    if not resultado.wasSuccessful():
        raise SystemExit(1)
    print('todos os testes passaram')
