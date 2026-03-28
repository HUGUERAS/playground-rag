from __future__ import annotations

import argparse
import csv
import json
import math
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable
from xml.etree import ElementTree as ET

from pyproj import Transformer
from supabase import Client, create_client


REPORT_PATHS = [
    Path(r"C:\Users\User\Documents\Playground\geoadmin-docs\06-governance\Work_Folder_Import_2026-03-16.json"),
    Path(r"C:\Users\User\Documents\Playground\geoadmin-docs\06-governance\Work_Folder_Import_Moderate_2026-03-16.json"),
]

SUPPORTED_EXTENSIONS = {".kml", ".csv", ".txt"}
NAME_KEYS = {"nome", "name", "ponto", "point", "id", "codigo", "code"}
LAT_KEYS = {"latitude", "lat"}
LON_KEYS = {"longitude", "lon", "long"}
EAST_KEYS = {"este", "e", "x", "east", "easting"}
NORTH_KEYS = {"norte", "n", "y", "north", "northing"}
ALT_KEYS = {"altitude", "alt", "cota", "z"}
BRAZIL_LAT_RANGE = (-35.0, 6.0)
BRAZIL_LON_RANGE = (-75.0, -30.0)


@dataclass
class ParsedPoint:
    name: str
    latitude: float
    longitude: float
    altitude_m: float | None
    source_file: str
    source_kind: str


@dataclass
class ImportSummary:
    folder_name: str
    projeto_id: str
    scanned_files: int
    parsed_points: int
    inserted_points: int
    skipped_points: int
    invalid_points: int
    errors: list[str]


def get_client() -> Client:
    url = os.getenv("SUPABASE_URL") or os.getenv("GEOADMIN_SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY") or os.getenv("GEOADMIN_SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL/SUPABASE_KEY nao definidos.")
    return create_client(url, key)


def _rows(result: Any) -> list[dict[str, Any]]:
    data = getattr(result, "data", None)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return [data]
    return []


def load_project_mappings() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for report_path in REPORT_PATHS:
        if report_path.exists():
            rows.extend(json.loads(report_path.read_text(encoding="utf-8")))
    return rows


def list_target_mappings(folder_names: list[str] | None) -> list[dict[str, Any]]:
    mappings = load_project_mappings()
    if folder_names:
        wanted = {name.casefold() for name in folder_names}
        mappings = [row for row in mappings if row["folder_name"].casefold() in wanted]
    return mappings


def existing_point_names(client: Client, project_id: str) -> set[str]:
    result = (
        client.table("pontos")
        .select("nome")
        .eq("projeto_id", project_id)
        .is_("deleted_at", "null")
        .execute()
    )
    return {str(row["nome"]).upper() for row in _rows(result)}


def project_zone(client: Client, project_id: str) -> str:
    result = client.table("projetos").select("zona_utm").eq("id", project_id).execute()
    rows = _rows(result)
    if not rows:
        raise RuntimeError(f"Projeto {project_id} nao encontrado.")
    return str(rows[0].get("zona_utm") or "23S").upper()


def utm_epsg_for_zone(zone: str) -> int:
    zone = zone.strip().upper()
    if len(zone) < 2 or zone[-1] not in {"S", "N"}:
        raise RuntimeError(f"Zona UTM invalida: {zone}")
    zone_number = int(zone[:-1])
    hemisphere = zone[-1]
    if hemisphere == "S":
        return 31960 + zone_number
    raise RuntimeError(f"Zona UTM no hemisferio norte ainda nao suportada: {zone}")


def make_point_name(raw_name: str | None, source_file: Path, index: int) -> str:
    if raw_name:
        normalized = raw_name.strip().upper()
        if normalized:
            return normalized[:20]
    stem = source_file.stem.upper().replace(" ", "_")
    return f"{stem[:12]}_{index:03d}"[:20]


def is_valid_point(point: ParsedPoint) -> bool:
    if not point.name.strip():
        return False
    if not math.isfinite(point.latitude) or not math.isfinite(point.longitude):
        return False
    if not (-90.0 <= point.latitude <= 90.0):
        return False
    if not (-180.0 <= point.longitude <= 180.0):
        return False
    if not (BRAZIL_LAT_RANGE[0] <= point.latitude <= BRAZIL_LAT_RANGE[1]):
        return False
    if not (BRAZIL_LON_RANGE[0] <= point.longitude <= BRAZIL_LON_RANGE[1]):
        return False
    if point.altitude_m is not None and not math.isfinite(point.altitude_m):
        return False
    return True


def iter_source_files(folder_path: Path) -> Iterable[Path]:
    for path in folder_path.rglob("*"):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            yield path


def parse_kml(path: Path) -> list[ParsedPoint]:
    root = ET.fromstring(path.read_text(encoding="utf-8", errors="ignore"))
    namespace = {"kml": "http://www.opengis.net/kml/2.2"}
    points: list[ParsedPoint] = []
    placemarks = root.findall(".//kml:Placemark", namespace)
    for index, placemark in enumerate(placemarks, start=1):
        name = placemark.findtext("kml:name", default="", namespaces=namespace)
        coordinates = placemark.findtext(".//kml:Point/kml:coordinates", default="", namespaces=namespace)
        if not coordinates.strip():
            continue
        first_coord = coordinates.strip().split()[0]
        parts = [part.strip() for part in first_coord.split(",")]
        if len(parts) < 2:
            continue
        longitude = float(parts[0])
        latitude = float(parts[1])
        altitude = float(parts[2]) if len(parts) > 2 and parts[2] else None
        points.append(
            ParsedPoint(
                name=make_point_name(name, path, index),
                latitude=latitude,
                longitude=longitude,
                altitude_m=altitude,
                source_file=str(path),
                source_kind="kml",
            )
        )
    return points


def sniff_delimiter(sample: str) -> str:
    for delimiter in (";", ",", "\t"):
        if delimiter in sample:
            return delimiter
    return ","


def normalize_headers(headers: list[str]) -> list[str]:
    return [header.strip().lower() for header in headers]


def parse_table_file(path: Path, zone_utm: str) -> list[ParsedPoint]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return []
    delimiter = sniff_delimiter(lines[0])
    reader = csv.DictReader(lines, delimiter=delimiter)
    if reader.fieldnames is None:
        return []
    normalized_headers = normalize_headers(reader.fieldnames)
    header_map = dict(zip(normalized_headers, reader.fieldnames))
    has_latlon = any(key in LAT_KEYS for key in normalized_headers) and any(key in LON_KEYS for key in normalized_headers)
    has_utm = any(key in EAST_KEYS for key in normalized_headers) and any(key in NORTH_KEYS for key in normalized_headers)
    if not has_latlon and not has_utm:
        return []

    transformer: Transformer | None = None
    if has_utm:
        epsg = utm_epsg_for_zone(zone_utm)
        transformer = Transformer.from_crs(f"EPSG:{epsg}", "EPSG:4674", always_xy=True)

    points: list[ParsedPoint] = []
    for index, row in enumerate(reader, start=1):
        normalized_row = {key.strip().lower(): value for key, value in row.items() if key is not None}
        raw_name = next((normalized_row[key] for key in normalized_headers if key in NAME_KEYS and normalized_row.get(key)), None)

        latitude: float
        longitude: float
        altitude: float | None = None

        alt_raw = next((normalized_row[key] for key in normalized_headers if key in ALT_KEYS and normalized_row.get(key)), None)
        if alt_raw:
            try:
                altitude = float(str(alt_raw).replace(",", "."))
            except ValueError:
                altitude = None

        if has_latlon:
            lat_key = next(key for key in normalized_headers if key in LAT_KEYS)
            lon_key = next(key for key in normalized_headers if key in LON_KEYS)
            try:
                latitude = float(str(normalized_row[lat_key]).replace(",", "."))
                longitude = float(str(normalized_row[lon_key]).replace(",", "."))
            except (KeyError, TypeError, ValueError):
                continue
        else:
            east_key = next(key for key in normalized_headers if key in EAST_KEYS)
            north_key = next(key for key in normalized_headers if key in NORTH_KEYS)
            try:
                east = float(str(normalized_row[east_key]).replace(",", "."))
                north = float(str(normalized_row[north_key]).replace(",", "."))
                assert transformer is not None
                longitude, latitude = transformer.transform(east, north)
            except (KeyError, TypeError, ValueError, AssertionError):
                continue

        points.append(
            ParsedPoint(
                name=make_point_name(raw_name, path, index),
                latitude=round(latitude, 8),
                longitude=round(longitude, 8),
                altitude_m=altitude,
                source_file=str(path),
                source_kind=path.suffix.lower()[1:],
            )
        )
    return points


def parse_points_from_file(path: Path, zone_utm: str) -> list[ParsedPoint]:
    suffix = path.suffix.lower()
    if suffix == ".kml":
        return parse_kml(path)
    if suffix in {".csv", ".txt"}:
        return parse_table_file(path, zone_utm)
    return []


def insert_point(client: Client, project_id: str, point: ParsedPoint) -> None:
    payload = {
        "projeto_id": project_id,
        "nome": point.name,
        "descricao": f"Importado de {point.source_file}",
        "coordenada": f"SRID=4674;POINT({point.longitude} {point.latitude})",
        "altitude_m": point.altitude_m,
        "qualidade_fix": 1,
        "num_amostras": 1,
        "camada": "PONTOS",
        "receptor_gnss": "IMPORTADO",
        "sincronizado": True,
    }
    payload = {key: value for key, value in payload.items() if value is not None}
    client.table("pontos").insert(payload).execute()


def import_points_for_mapping(client: Client, mapping: dict[str, Any], dry_run: bool) -> ImportSummary:
    folder_path = Path(mapping["folder_path"])
    project_id = str(mapping["projeto_id"])
    errors: list[str] = []
    scanned_files = 0
    parsed_points = 0
    inserted_points = 0
    skipped_points = 0
    invalid_points = 0

    if not folder_path.exists():
        return ImportSummary(
            folder_name=mapping["folder_name"],
            projeto_id=project_id,
            scanned_files=0,
            parsed_points=0,
            inserted_points=0,
            skipped_points=0,
            invalid_points=0,
            errors=["Pasta nao encontrada."],
        )

    known_names = existing_point_names(client, project_id)
    zone_utm = project_zone(client, project_id)

    for source_file in iter_source_files(folder_path):
        scanned_files += 1
        try:
            parsed = parse_points_from_file(source_file, zone_utm)
        except Exception as exc:
            errors.append(f"{source_file.name}: falha ao parsear ({exc})")
            continue

        parsed_points += len(parsed)
        for point in parsed:
            if not is_valid_point(point):
                invalid_points += 1
                continue
            if point.name in known_names:
                skipped_points += 1
                continue
            if dry_run:
                inserted_points += 1
                known_names.add(point.name)
                continue
            try:
                insert_point(client, project_id, point)
                inserted_points += 1
                known_names.add(point.name)
            except Exception as exc:
                errors.append(f"{source_file.name}:{point.name} -> {exc}")

    return ImportSummary(
        folder_name=mapping["folder_name"],
        projeto_id=project_id,
        scanned_files=scanned_files,
        parsed_points=parsed_points,
        inserted_points=inserted_points,
        skipped_points=skipped_points,
        invalid_points=invalid_points,
        errors=errors,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Importa pontos reais de KML/CSV/TXT para projetos ja cadastrados.")
    parser.add_argument("--folders", nargs="*", help="Lista de pastas especificas a importar.")
    parser.add_argument("--dry-run", action="store_true", help="Nao grava no Supabase; apenas simula.")
    parser.add_argument(
        "--report",
        default=r"C:\Users\User\Documents\Playground\geoadmin-docs\06-governance\Work_Folder_Points_Import_2026-03-16.json",
        help="Arquivo JSON de relatorio.",
    )
    args = parser.parse_args()

    client = get_client()
    mappings = list_target_mappings(args.folders)
    summaries = [asdict(import_points_for_mapping(client, mapping, args.dry_run)) for mapping in mappings]

    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(summaries, ensure_ascii=False, indent=2), encoding="utf-8")

    inserted = sum(item["inserted_points"] for item in summaries)
    parsed = sum(item["parsed_points"] for item in summaries)
    print(f"Projetos processados: {len(summaries)}")
    print(f"Pontos lidos: {parsed}")
    print(f"Pontos {'simulados' if args.dry_run else 'inseridos'}: {inserted}")
    print(f"Relatorio: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
