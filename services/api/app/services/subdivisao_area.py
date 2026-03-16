from __future__ import annotations

import math
from dataclasses import dataclass

from shapely.geometry import LineString, Polygon, Point, MultiPoint
from shapely.ops import split
from shapely.validation import explain_validity


@dataclass
class PontoUTM:
    nome: str
    este: float
    norte: float

    def como_tupla(self) -> tuple[float, float]:
        return (self.este, self.norte)


@dataclass
class ResultadoSubdivisao:
    poligono_a: list[tuple[float, float]]
    poligono_b: list[tuple[float, float]]
    area_a_m2: float
    area_b_m2: float
    area_total_m2: float
    linha_divisoria: list[tuple[float, float]]
    erro_m2: float
    metodo: str


def _validar_poligono(pontos: list[tuple[float, float]]) -> Polygon:
    if len(pontos) < 3:
        raise ValueError(f"[ERRO-101] Poligono requer minimo 3 vertices. Recebidos: {len(pontos)}")

    poligono = Polygon(pontos)

    if not poligono.is_valid:
        motivo = explain_validity(poligono)
        raise ValueError(f"[ERRO-201] Poligono invalido: {motivo}")

    if poligono.area == 0:
        raise ValueError("[ERRO-202] Poligono com area zero, vertices colineares.")

    return poligono


def _extrair_vertices(poligono: Polygon) -> list[tuple[float, float]]:
    coords = list(poligono.exterior.coords)
    if coords[0] == coords[-1]:
        coords = coords[:-1]
    return [(round(x, 6), round(y, 6)) for x, y in coords]


def _area_segura(poligono: Polygon) -> float:
    return round(poligono.area, 6)


def _comprimento_lado(p1: tuple[float, float], p2: tuple[float, float]) -> float:
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


def _ponto_na_linha(p1: tuple[float, float], p2: tuple[float, float], t: float) -> tuple[float, float]:
    x = p1[0] + t * (p2[0] - p1[0])
    y = p1[1] + t * (p2[1] - p1[1])
    return (round(x, 6), round(y, 6))


def _bissetar_poligono(poligono: Polygon, linha: LineString) -> tuple[Polygon, Polygon]:
    try:
        resultado = split(poligono, linha)
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"[ERRO-401] Falha ao dividir poligono: {exc}") from exc

    geoms = list(resultado.geoms)
    if len(geoms) < 2:
        raise ValueError(
            "[ERRO-402] A linha de corte nao atravessa o poligono completamente. "
            "Verifique se os dois pontos estao em lados opostos."
        )

    geoms.sort(key=lambda geom: geom.area)
    return geoms[0], geoms[1]


def _coletar_pontos_intersecao(geometry: object) -> list[tuple[float, float]]:
    if hasattr(geometry, "is_empty") and geometry.is_empty:  # type: ignore[attr-defined]
        return []
    if isinstance(geometry, Point):
        return [(geometry.x, geometry.y)]
    if isinstance(geometry, MultiPoint):
        return [(point.x, point.y) for point in geometry.geoms]
    if isinstance(geometry, LineString):
        coords = list(geometry.coords)
        return [coords[0], coords[-1]]
    if hasattr(geometry, "geoms"):
        points: list[tuple[float, float]] = []
        for geom in geometry.geoms:  # type: ignore[attr-defined]
            points.extend(_coletar_pontos_intersecao(geom))
        return points
    return []


def subdividir_por_area(
    pontos: list[tuple[float, float]],
    area_desejada_m2: float,
    lado_base: int = 0,
    tolerancia_m2: float = 0.001,
    max_iter: int = 100,
) -> ResultadoSubdivisao:
    poligono = _validar_poligono(pontos)
    area_total = poligono.area

    if area_desejada_m2 <= 0:
        raise ValueError(f"[ERRO-102] Area desejada deve ser positiva. Recebido: {area_desejada_m2}")

    if area_desejada_m2 >= area_total:
        raise ValueError(
            f"[ERRO-103] Area desejada ({area_desejada_m2:.2f} m2) e maior ou igual "
            f"a area total ({area_total:.2f} m2)."
        )

    vertices = list(poligono.exterior.coords)[:-1]
    total_lados = len(vertices)
    if lado_base >= total_lados:
        raise ValueError(f"[ERRO-104] Indice de lado invalido: {lado_base}. Poligono tem {total_lados} lados.")

    v1 = vertices[lado_base]
    v2 = vertices[(lado_base + 1) % total_lados]

    dx = v2[0] - v1[0]
    dy = v2[1] - v1[1]
    comprimento_base = math.sqrt(dx**2 + dy**2)
    if comprimento_base == 0:
        raise ValueError(f"[ERRO-203] Lado base {lado_base} tem comprimento zero.")

    perp_x = -dy / comprimento_base
    perp_y = dx / comprimento_base

    def projecao(ponto: tuple[float, float]) -> float:
        return (ponto[0] - v1[0]) * perp_x + (ponto[1] - v1[1]) * perp_y

    proj_max = max(projecao(v) for v in vertices)
    if proj_max <= 0:
        proj_max = abs(min(projecao(v) for v in vertices))
        perp_x, perp_y = -perp_x, -perp_y

    bounds = poligono.bounds
    ext = max(bounds[2] - bounds[0], bounds[3] - bounds[1]) * 2

    t_min, t_max = 0.001, 0.999
    t = 0.5
    melhor_resultado: tuple[Polygon, Polygon, LineString] | None = None
    menor_erro = float("inf")

    for _ in range(max_iter):
        cx = v1[0] + t * proj_max * perp_x
        cy = v1[1] + t * proj_max * perp_y

        lx1 = cx - ext * (dx / comprimento_base)
        ly1 = cy - ext * (dy / comprimento_base)
        lx2 = cx + ext * (dx / comprimento_base)
        ly2 = cy + ext * (dy / comprimento_base)

        linha_corte = LineString([(lx1, ly1), (lx2, ly2)])

        if not linha_corte.intersects(poligono.exterior):
            t_max = t
            t = (t_min + t_max) / 2
            continue

        try:
            parte_a, parte_b = _bissetar_poligono(poligono, linha_corte)
            if parte_a.area < parte_b.area:
                area_a = parte_a.area
                poly_a, poly_b = parte_a, parte_b
            else:
                area_a = parte_b.area
                poly_a, poly_b = parte_b, parte_a
        except ValueError:
            t_max = t
            t = (t_min + t_max) / 2
            continue

        erro = abs(area_a - area_desejada_m2)
        if erro < menor_erro:
            menor_erro = erro
            melhor_resultado = (poly_a, poly_b, linha_corte)

        if erro <= tolerancia_m2:
            break

        if area_a < area_desejada_m2:
            t_min = t
        else:
            t_max = t

        t = (t_min + t_max) / 2

    if melhor_resultado is None:
        raise ValueError("[ERRO-403] Nao foi possivel encontrar linha de corte valida.")

    poly_a, poly_b, linha_final = melhor_resultado
    intersecao = linha_final.intersection(poligono.exterior)
    pts_linha = _coletar_pontos_intersecao(intersecao)[:2]
    if len(pts_linha) < 2:
        pts_linha = [(round(x, 6), round(y, 6)) for x, y in list(linha_final.coords)[:2]]

    return ResultadoSubdivisao(
        poligono_a=_extrair_vertices(poly_a),
        poligono_b=_extrair_vertices(poly_b),
        area_a_m2=_area_segura(poly_a),
        area_b_m2=_area_segura(poly_b),
        area_total_m2=_area_segura(poligono),
        linha_divisoria=[(round(p[0], 6), round(p[1], 6)) for p in pts_linha],
        erro_m2=round(menor_erro, 6),
        metodo="paralela_ao_lado",
    )


def subdividir_por_percentual(
    pontos: list[tuple[float, float]],
    percentual_a: float,
    lado_base: int = 0,
) -> ResultadoSubdivisao:
    if not (0 < percentual_a < 100):
        raise ValueError(f"[ERRO-105] Percentual deve estar entre 0 e 100. Recebido: {percentual_a}")

    poligono = _validar_poligono(pontos)
    area_desejada = poligono.area * (percentual_a / 100.0)

    resultado = subdividir_por_area(pontos, area_desejada, lado_base)
    resultado.metodo = f"percentual_{percentual_a:.2f}pct"
    return resultado


def subdividir_por_vertice(
    pontos: list[tuple[float, float]],
    indice_vertice: int,
    area_desejada_m2: float,
    tolerancia_m2: float = 0.001,
    max_iter: int = 100,
) -> ResultadoSubdivisao:
    poligono = _validar_poligono(pontos)
    area_total = poligono.area
    vertices = list(poligono.exterior.coords)[:-1]
    total_vertices = len(vertices)

    if not (0 <= indice_vertice < total_vertices):
        raise ValueError(
            f"[ERRO-106] Indice de vertice {indice_vertice} invalido. Poligono tem {total_vertices} vertices."
        )

    if area_desejada_m2 <= 0 or area_desejada_m2 >= area_total:
        raise ValueError(
            f"[ERRO-107] Area desejada ({area_desejada_m2:.2f} m2) fora do intervalo (0, {area_total:.2f}]."
        )

    pivo = vertices[indice_vertice]
    lados_nao_adjacentes: list[tuple[int, tuple[float, float], tuple[float, float]]] = []
    for i in range(total_vertices):
        v_ini = vertices[i]
        v_fim = vertices[(i + 1) % total_vertices]
        if v_ini == pivo or v_fim == pivo:
            continue
        lados_nao_adjacentes.append((i, v_ini, v_fim))

    if not lados_nao_adjacentes:
        raise ValueError("[ERRO-204] Nao ha lados nao adjacentes ao vertice pivo.")

    melhor_resultado: tuple[Polygon, Polygon, list[tuple[float, float]]] | None = None
    menor_erro = float("inf")

    for _, v_ini, v_fim in lados_nao_adjacentes:
        comprimento = _comprimento_lado(v_ini, v_fim)
        if comprimento == 0:
            continue

        t_min, t_max = 0.0, 1.0

        for _ in range(max_iter):
            t = (t_min + t_max) / 2
            pt_corte = _ponto_na_linha(v_ini, v_fim, t)

            linha_corte = LineString([pivo, pt_corte])
            ext = comprimento * 0.001
            dx = pt_corte[0] - pivo[0]
            dy = pt_corte[1] - pivo[1]
            dist = math.sqrt(dx**2 + dy**2)
            if dist == 0:
                continue
            linha_ext = LineString(
                [
                    pivo,
                    (pt_corte[0] + ext * dx / dist, pt_corte[1] + ext * dy / dist),
                ]
            )

            try:
                parte_a, parte_b = _bissetar_poligono(poligono, linha_ext)
                pt_pivo = Point(pivo)
                if not parte_a.contains(pt_pivo) and not parte_a.touches(pt_pivo):
                    parte_a, parte_b = parte_b, parte_a
                area_a = parte_a.area
            except ValueError:
                break

            erro = abs(area_a - area_desejada_m2)
            if erro < menor_erro:
                menor_erro = erro
                melhor_resultado = (parte_a, parte_b, [pivo, pt_corte])

            if erro <= tolerancia_m2:
                break

            if area_a < area_desejada_m2:
                t_min = t
            else:
                t_max = t

        if melhor_resultado and menor_erro <= tolerancia_m2:
            break

    if melhor_resultado is None:
        raise ValueError(
            f"[ERRO-404] Nao foi possivel subdividir pelo vertice {indice_vertice}. "
            "Verifique se a area solicitada e geometricamente possivel com este vertice."
        )

    poly_a, poly_b, pts_linha = melhor_resultado
    return ResultadoSubdivisao(
        poligono_a=_extrair_vertices(poly_a),
        poligono_b=_extrair_vertices(poly_b),
        area_a_m2=_area_segura(poly_a),
        area_b_m2=_area_segura(poly_b),
        area_total_m2=_area_segura(poligono),
        linha_divisoria=pts_linha,
        erro_m2=round(menor_erro, 6),
        metodo=f"por_vertice_{indice_vertice}",
    )


def subdividir_por_ponto_fixo(
    pontos: list[tuple[float, float]],
    ponto_fixo: tuple[float, float],
    area_desejada_m2: float,
    tolerancia_m2: float = 0.001,
    max_iter: int = 200,
) -> ResultadoSubdivisao:
    poligono = _validar_poligono(pontos)
    area_total = poligono.area
    pt = Point(ponto_fixo)

    if area_desejada_m2 <= 0 or area_desejada_m2 >= area_total:
        raise ValueError(
            f"[ERRO-108] Area desejada ({area_desejada_m2:.2f} m2) fora do intervalo (0, {area_total:.2f}]."
        )

    if not (poligono.contains(pt) or poligono.touches(pt) or poligono.exterior.distance(pt) < 1.0):
        raise ValueError(
            "[ERRO-205] Ponto fixo esta fora do poligono ou muito distante da borda. "
            "O ponto de divisao deve estar dentro ou sobre a borda do lote."
        )

    bounds = poligono.bounds
    ext = max(bounds[2] - bounds[0], bounds[3] - bounds[1]) * 2

    melhor_resultado: tuple[Polygon, Polygon, list[tuple[float, float]]] | None = None
    menor_erro = float("inf")

    angulo_min, angulo_max = 0.0, 360.0

    for _ in range(max_iter):
        angulo = (angulo_min + angulo_max) / 2
        rad = math.radians(angulo)

        lx1 = ponto_fixo[0] - ext * math.cos(rad)
        ly1 = ponto_fixo[1] - ext * math.sin(rad)
        lx2 = ponto_fixo[0] + ext * math.cos(rad)
        ly2 = ponto_fixo[1] + ext * math.sin(rad)

        linha_corte = LineString([(lx1, ly1), (lx2, ly2)])

        if not linha_corte.intersects(poligono.exterior):
            angulo_max = angulo
            continue

        try:
            parte_a, parte_b = _bissetar_poligono(poligono, linha_corte)
            area_a = parte_a.area
        except ValueError:
            angulo_max = angulo
            continue

        erro = abs(area_a - area_desejada_m2)
        if erro < menor_erro:
            menor_erro = erro
            intersecao = linha_corte.intersection(poligono.exterior)
            pts = _coletar_pontos_intersecao(intersecao)[:2]
            melhor_resultado = (parte_a, parte_b, pts)

        if erro <= tolerancia_m2:
            break

        if area_a < area_desejada_m2:
            angulo_min = angulo
        else:
            angulo_max = angulo

    if melhor_resultado is None:
        raise ValueError("[ERRO-405] Nao foi possivel encontrar angulo de corte valido para o ponto fixo fornecido.")

    poly_a, poly_b, pts_linha = melhor_resultado
    return ResultadoSubdivisao(
        poligono_a=_extrair_vertices(poly_a),
        poligono_b=_extrair_vertices(poly_b),
        area_a_m2=_area_segura(poly_a),
        area_b_m2=_area_segura(poly_b),
        area_total_m2=_area_segura(poligono),
        linha_divisoria=[(round(p[0], 6), round(p[1], 6)) for p in pts_linha],
        erro_m2=round(menor_erro, 6),
        metodo="por_ponto_fixo",
    )


def formatar_resultado(resultado: ResultadoSubdivisao) -> str:
    linhas = [
        f"Metodo:         {resultado.metodo}",
        f"Area total:     {resultado.area_total_m2:>15.4f} m2  ({resultado.area_total_m2 / 10000:.4f} ha)",
        "",
        f"  Parte A:      {resultado.area_a_m2:>15.4f} m2  ({resultado.area_a_m2 / 10000:.4f} ha)"
        f"  [{resultado.area_a_m2 / resultado.area_total_m2 * 100:.2f}%]",
        f"  Parte B:      {resultado.area_b_m2:>15.4f} m2  ({resultado.area_b_m2 / 10000:.4f} ha)"
        f"  [{resultado.area_b_m2 / resultado.area_total_m2 * 100:.2f}%]",
        "",
        f"Erro obtido:    {resultado.erro_m2:.6f} m2",
        "",
        "Linha divisoria:",
        f"  P1: E={resultado.linha_divisoria[0][0]:.3f}  N={resultado.linha_divisoria[0][1]:.3f}",
    ]
    if len(resultado.linha_divisoria) > 1:
        linhas.append(
            f"  P2: E={resultado.linha_divisoria[1][0]:.3f}  N={resultado.linha_divisoria[1][1]:.3f}"
        )
    linhas.append("")
    linhas.append(f"Vertices Parte A ({len(resultado.poligono_a)} pontos):")
    for index, (este, norte) in enumerate(resultado.poligono_a):
        linhas.append(f"  V{index + 1:02d}: E={este:.3f}  N={norte:.3f}")
    return "\n".join(linhas)
