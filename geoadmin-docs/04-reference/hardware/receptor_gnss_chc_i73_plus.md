# Hardware GNSS - CHC i73+
**Task 0.2:** Concluida  
**Documento criado:** Marco 2026

## Especificacoes relevantes

| Item | Detalhe |
|---|---|
| Fabricante | CHC Navigation |
| Receptor | i73+ |
| Conexao com app | Bluetooth classico via SPP |
| Protocolo | NMEA 0183 v4.1 |
| Taxa padrao | 1 Hz |
| Taxa maxima | ate 20 Hz |
| Precisao RTK Fix | H: 8mm + 1ppm / V: 15mm + 1ppm |
| Precisao RTK Float | cerca de 0.3m |
| Inclinacao | IMU integrado, ate 60 graus |
| NTRIP | via celular interno 4G |
| Energia | 5V USB |

## Sentencas NMEA prioritarias

| Sentenca | Conteudo | Prioridade |
|---|---|---|
| `$GNGGA` | posicao, altitude, HDOP, satelites, qualidade do fix | critica |
| `$GNRMC` | posicao, velocidade, data e hora | alta |
| `$GNGSV` | satelites em vista | media |
| `$GNGSA` | satelites usados, PDOP, HDOP, VDOP | alta |
| `$GNZDA` | data e hora UTC | media |
| `$PCHC` | inclinacao IMU CHC | alta |

## Campo fix da GGA

- `0`: sem fix, nao usar
- `1`: autonomo
- `2`: DGPS ou SBAS
- `4`: RTK Fix
- `5`: RTK Float

## Biblioteca mobile correta

Como o i73+ usa **Bluetooth classico SPP**, a biblioteca recomendada no mobile e:

```text
react-native-bluetooth-classic
```

Nao usar `react-native-ble-plx` para este receptor.

## Configuracao recomendada

- baud rate: `115200`
- output NMEA: `GGA + RMC + GSA + PCHC`
- taxa: `1 Hz` para coleta de pontos
- taxa: `5 Hz` para movimento
- NTRIP: IBGE-RNAV ou rede privada quando aplicavel

## Notas de campo

1. O Bluetooth demora cerca de 30 segundos para aparecer apos ligar.
2. Float prolongado sugere problema de NTRIP.
3. Tilt compensation desativa acima de 60 graus.
4. A bateria dura cerca de 8 horas de uso continuo.

## Implicacoes para o GeoAdmin

- O parser inicial deve priorizar `$GNGGA` e `$PCHC`.
- O app mobile precisa tratar porta serial, nao fluxo BLE.
- A Task 2.1 deve ser implementada com foco em Bluetooth classico e leitura continua de sentencas NMEA.
