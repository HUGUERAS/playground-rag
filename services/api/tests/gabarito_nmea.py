def construir_sentenca(corpo: str) -> str:
    checksum = 0
    for caractere in corpo:
        checksum ^= ord(caractere)
    return f"${corpo}*{checksum:02X}"


GGA_FIX_BODY = "GNGGA,120000.00,1546.7500,S,04755.7833,W,4,24,0.6,-950.5,M,0.0,M,1.0,0000"
GGA_FIX_SENTENCE = construir_sentenca(GGA_FIX_BODY)

GGA_NO_FIX_BODY = "GNGGA,120000.00,1546.7500,S,04755.7833,W,0,00,99.9,0.0,M,0.0,M,,"
GGA_NO_FIX_SENTENCE = construir_sentenca(GGA_NO_FIX_BODY)

RMC_BODY = "GNRMC,120000.00,A,1546.7500,S,04755.7833,W,0.52,127.4,160326,,,A"
RMC_SENTENCE = construir_sentenca(RMC_BODY)

GSA_BODY = "GNGSA,A,3,10,12,14,18,20,23,25,27,29,31,32,,1.2,0.6,1.0"
GSA_SENTENCE = construir_sentenca(GSA_BODY)

PCHC_SENTENCE = "$PCHC,3.2,-1.5,0.0,127.4*00"
PCHC_LEGACY_SENTENCE = "$PCHC,3.2,-1.5,127.4*00"
