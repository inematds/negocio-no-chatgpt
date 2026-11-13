# Falhas corrigidas

| data | o que quebrou | menor correção | prompt ou infra |
|---|---|---|---|
| 2026-11-13 | json.loads aceita NaN como extensão, permitindo chamar JSON-LD inválido de válido | Recusar constantes fora do padrão JSON com parse_constant e teste de regressão | infra |
