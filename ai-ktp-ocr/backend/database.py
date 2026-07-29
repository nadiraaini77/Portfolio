"""
Database layer: engine, session, and CRUD helpers.
Streamlit imports these functions directly (no HTTP hop) per the hybrid
architecture — this module is the "backend" without needing a running server.
"""
import json
from pathlib import Path
from typing import List, Optional

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, Session

from backend.config import DB_PATH
from backend.models import Base, KTPRecord
from backend.schemas import KTPExtraction, ValidationResult

# Ensure the data/ directory exists before SQLite tries to create the file
Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    """Create tables if they don't exist yet. Safe to call on every app start."""
    Base.metadata.create_all(engine)


def get_session() -> Session:
    return SessionLocal()


def save_record(
    session: Session,
    ocr: KTPExtraction,
    validation: ValidationResult,
    jenis_dokumen: str = "KTP",
) -> int:
    """Persist one record — valid or invalid — for the full audit trail."""
    record = KTPRecord(
        nama=ocr.nama,
        nomor_dokumen=ocr.nik,
        jenis_dokumen=jenis_dokumen,
        status_validasi=validation.overall_status,
        tempat_tgl_lahir=ocr.tempat_tgl_lahir,
        jenis_kelamin=ocr.jenis_kelamin,
        agama=ocr.agama,
        alamat=ocr.alamat,
        rt=ocr.rt,
        rw=ocr.rw,
        kelurahan=ocr.kelurahan,
        kecamatan=ocr.kecamatan,
        status_perkawinan=ocr.status_perkawinan,
        pekerjaan=ocr.pekerjaan,
        kewarganegaraan=ocr.kewarganegaraan,
        berlaku_hingga=ocr.berlaku_hingga,
        validation_errors=json.dumps(validation.errors, ensure_ascii=False),
        raw_ocr_json=ocr.model_dump_json(),
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return record.id


def get_all_records(session: Session) -> List[KTPRecord]:
    return session.query(KTPRecord).order_by(desc(KTPRecord.tanggal_upload)).all()


def get_record_by_id(session: Session, record_id: int) -> Optional[KTPRecord]:
    return session.query(KTPRecord).filter(KTPRecord.id == record_id).first()


def records_to_dicts(records: List[KTPRecord]) -> List[dict]:
    """Flat list[dict] — hand this straight to pandas.DataFrame() for the
    History page and CSV export."""
    out = []
    for r in records:
        out.append(
            {
                "id": r.id,
                "nama": r.nama,
                "nomor_dokumen": r.nomor_dokumen,
                "jenis_dokumen": r.jenis_dokumen,
                "tanggal_upload": r.tanggal_upload.isoformat() if r.tanggal_upload else "",
                "status_validasi": r.status_validasi,
                "tempat_tgl_lahir": r.tempat_tgl_lahir,
                "jenis_kelamin": r.jenis_kelamin,
                "agama": r.agama,
                "alamat": r.alamat,
                "rt": r.rt,
                "rw": r.rw,
                "kelurahan": r.kelurahan,
                "kecamatan": r.kecamatan,
                "status_perkawinan": r.status_perkawinan,
                "pekerjaan": r.pekerjaan,
                "kewarganegaraan": r.kewarganegaraan,
                "berlaku_hingga": r.berlaku_hingga,
                "validation_errors": "; ".join(json.loads(r.validation_errors or "[]")),
            }
        )
    return out

def records_to_history_dicts(records: List[KTPRecord]) -> List[dict]:
    """Data khusus untuk ditampilkan di halaman History."""
    out = []

    for r in records:
        out.append(
            {
                "id": r.id,
                "nama": r.nama,
                "nomor_dokumen": (
                     f"{r.nomor_dokumen[:4]}{'*' * (len(r.nomor_dokumen) - 8)}{r.nomor_dokumen[-4:]}"
                     if r.nomor_dokumen and len(r.nomor_dokumen) >= 8
                     else r.nomor_dokumen
                ),
                "jenis_dokumen": r.jenis_dokumen,
                "tanggal_upload": (
                    r.tanggal_upload.strftime("%d %b %Y • %H:%M WIB")
                    if r.tanggal_upload
                    else ""
                ),
                "status_validasi": r.status_validasi,
                "tempat_tgl_lahir": r.tempat_tgl_lahir,
                "jenis_kelamin": r.jenis_kelamin,
                "agama": r.agama,
                "alamat": r.alamat,
                "rt": r.rt,
                "rw": r.rw,
                "kelurahan": r.kelurahan,
                "kecamatan": r.kecamatan,
                "status_perkawinan": r.status_perkawinan,
                "pekerjaan": r.pekerjaan,
                "kewarganegaraan": r.kewarganegaraan,
                "berlaku_hingga": r.berlaku_hingga,
                "validation_errors": "; ".join(json.loads(r.validation_errors or "[]")),
            }
        )

    return out
