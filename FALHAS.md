# Falhas corrigidas

| data | o que quebrou | menor correção | prompt ou infra |
|---|---|---|---|
| 2026-11-13 | ficha.py interativo só validava no fim: tipo "padaria" perdia as 18 respostas (achado do revisor do guia) | conferir tipo/telefone/e-mail/site na hora e perguntar de novo; tipo aceita número e sinônimo; 3 testes | prompt |
| 2026-11-13 | json.loads aceita NaN como extensão, permitindo chamar JSON-LD inválido de válido | Recusar constantes fora do padrão JSON com parse_constant e teste de regressão | infra |
