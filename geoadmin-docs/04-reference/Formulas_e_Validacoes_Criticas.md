# Formulas e Validacoes Criticas

## Formulas documentadas

### Inverso

- `Delta X = X2 - X1`
- `Delta Y = Y2 - Y1`
- `Distancia = sqrt(Delta X^2 + Delta Y^2)`
- `Azimute = arctan2(Delta X, Delta Y)`

## Regras de entrada

- Dois pontos iguais invalidam o calculo de inverso.
- Coordenadas precisam respeitar o sistema configurado no projeto.
- Linhas e poligonos devem manter topologia valida.

## Regras de saida

- Resultados precisam informar unidade e sistema de referencia quando aplicavel.
- Cada calculo tecnico deve ser rastreavel no historico.

## Pendencias abertas

- Formalizar formulas e validacoes das demais ferramentas vistas nas telas, como `Interseccao`, `Rotacao`, `Least squares` e `Subdivisao de area`.
