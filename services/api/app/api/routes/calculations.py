from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.services.geodesy import GeodesyError
from app.services.calculations import (
    calculate_inverse,
    calculate_polygon_area,
    convert_geographic_to_utm,
)
from geoadmin_shared_types.calculations import (
    AreaRequest,
    AreaResponse,
    ConvertCoordinateRequest,
    ConvertCoordinateResponse,
    ErrorResponse,
    InverseRequest,
    InverseResponse,
)

router = APIRouter(prefix="/geo", tags=["geo"])


def _raise_bad_request(exc: GeodesyError) -> HTTPException:
    return HTTPException(status_code=400, detail=ErrorResponse(erro=exc.message, codigo=exc.code).model_dump())


@router.post("/inverso", response_model=InverseResponse)
@router.post("/inverse", response_model=InverseResponse, include_in_schema=False)
def post_inverse(payload: InverseRequest) -> InverseResponse:
    try:
        return calculate_inverse(payload)
    except GeodesyError as exc:
        raise _raise_bad_request(exc) from exc


@router.post("/area", response_model=AreaResponse)
def post_area(payload: AreaRequest) -> AreaResponse:
    try:
        return calculate_polygon_area(payload)
    except GeodesyError as exc:
        raise _raise_bad_request(exc) from exc


@router.post("/converter", response_model=ConvertCoordinateResponse)
@router.post("/convert", response_model=ConvertCoordinateResponse, include_in_schema=False)
def post_convert(payload: ConvertCoordinateRequest) -> ConvertCoordinateResponse:
    try:
        return convert_geographic_to_utm(payload)
    except GeodesyError as exc:
        raise _raise_bad_request(exc) from exc
