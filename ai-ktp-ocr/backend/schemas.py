"""
Pydantic schemas — the data contracts between ai_service, validation, and the UI.
Keeping these separate from models.py (DB layer) is deliberate: schemas describe
"data in transit," models describe "data at rest."
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ClassificationResult(BaseModel):
    is_ktp: bool
    raw_response: Optional[str] = None  # kept for debugging/testing page


class KTPExtraction(BaseModel):
    """Mirrors the 14 fields required by the project spec. All default to ""
    so a partial/failed extraction never crashes downstream code — it just
    surfaces as validation failures, which is the correct behavior."""
    nik: str = ""
    nama: str = ""
    tempat_tgl_lahir: str = ""
    jenis_kelamin: str = ""
    agama: str = ""
    alamat: str = ""
    rt: str = ""
    rw: str = ""
    kelurahan: str = ""
    kecamatan: str = ""
    status_perkawinan: str = ""
    pekerjaan: str = ""
    kewarganegaraan: str = ""
    berlaku_hingga: str = ""


class ValidationResult(BaseModel):
    # per-field check name -> "VALID" | "INVALID" | "SKIPPED"
    checks: Dict[str, str] = Field(default_factory=dict)
    overall_status: str = "INVALID"  # "VALID" | "INVALID"
    errors: List[str] = Field(default_factory=list)


class DocumentRecordOut(BaseModel):
    """What the frontend reads back from the database for the History page."""
    id: int
    nama: str
    nomor_dokumen: str
    jenis_dokumen: str
    tanggal_upload: str
    status_validasi: str
    ocr: KTPExtraction
    validation_errors: List[str] = Field(default_factory=list)

class ProcessResponse(BaseModel):
    is_ktp: bool
    overall_status: str
    ocr_status: str
    ocr_data: KTPExtraction
    validation_errors: List[str] = Field(default_factory=list)

class ProcessResponse(BaseModel):
    is_ktp: bool
    overall_status: str
    ocr_status: str
    ocr_data: KTPExtraction
    validation_errors: List[str] = Field(default_factory=list)
    record_id: Optional[int] = None
