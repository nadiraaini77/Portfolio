"""
SQLAlchemy ORM model — "data at rest" in SQLite.
One row per uploaded document, valid or invalid (full audit trail).
"""
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class KTPRecord(Base):
    __tablename__ = "ktp_records"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Required minimal columns per project spec
    nama = Column(String, default="")
    nomor_dokumen = Column(String, default="")  # NIK
    jenis_dokumen = Column(String, default="KTP")
    tanggal_upload = Column(DateTime, default=datetime.now)
    status_validasi = Column(String, default="INVALID")  # VALID | INVALID

    # Full OCR fields (kept flat for simple querying/CSV export)
    tempat_tgl_lahir = Column(String, default="")
    jenis_kelamin = Column(String, default="")
    agama = Column(String, default="")
    alamat = Column(String, default="")
    rt = Column(String, default="")
    rw = Column(String, default="")
    kelurahan = Column(String, default="")
    kecamatan = Column(String, default="")
    status_perkawinan = Column(String, default="")
    pekerjaan = Column(String, default="")
    kewarganegaraan = Column(String, default="")
    berlaku_hingga = Column(String, default="")

    # Audit trail extras
    validation_errors = Column(Text, default="[]")  # JSON-encoded list[str]
    raw_ocr_json = Column(Text, default="{}")        # full raw OCR JSON backup

    def __repr__(self) -> str:
        return f"<KTPRecord id={self.id} nama={self.nama!r} status={self.status_validasi}>"
