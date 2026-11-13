# Regras do kit

Kit público `inematds/negocio-no-chatgpt`. Autor e committer: `inematds <inematds@gmail.com>`.

- Nome do método: "ficha do negócio para a IA". Código e saídas em português do Brasil.
- Python 3, somente biblioteca padrão, sem pip.
- `ficha.py` nunca usa rede; `checar_site.py` só GET, timeout de 15 s, no máximo 5 redirecionamentos e 2 MB por recurso.
- Fatos somente de `FONTES.md`. Não prometer posição, vendas ou efeito de JSON-LD/llms.txt.
- Antes de commitar: `python3 testes/run.py`.
- Guia em `guia/`, PT + `en/` + `es/`; criação em etapa separada.
- Dados de exemplo devem ser explicitamente fictícios.

## Self-learning

Quando eu for corrigido ou perceber um erro: antes de seguir, acrescente a lição como regra de uma linha no TOPO de `## Lessons`.

## Lessons
