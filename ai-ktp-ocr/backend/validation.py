"""
Business rule validation — pure Python, runs AFTER the AI has already done the
OCR. This module never touches the image; it only checks the extracted fields
for internal consistency.

Indonesian NIK structure (16 digits): PP KK CC DD MM YY XXXX
  PP    = kode provinsi        (2 digits)
  KK    = kode kabupaten/kota  (2 digits)
  CC    = kode kecamatan       (2 digits)
  DD    = tanggal lahir        (2 digits; +40 if perempuan)
  MM    = bulan lahir          (2 digits)
  YY    = 2 digit tahun lahir  (2 digits)
  XXXX  = nomor urut           (4 digits)
"""
import re
from datetime import datetime
from typing import Optional, Tuple

from backend.schemas import KTPExtraction, ValidationResult

VALID = "VALID"
INVALID = "INVALID"
SKIPPED = "SKIPPED"

_DATE_PATTERNS = [
    r"(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})",  # dd-mm-yyyy or dd/mm/yyyy
]


def _extract_date(text: str) -> Optional[Tuple[int, int, int]]:
    """Pull the first (day, month, year) out of a free-text date string like
    'JAKARTA, 17-08-1990'. Returns None if nothing date-shaped is found."""
    if not text:
        return None
    for pattern in _DATE_PATTERNS:
        m = re.search(pattern, text)
        if m:
            day, month, year = m.groups()
            year = int(year)
            if year < 100:
                # 2-digit year: assume 1900s unless it implies a future birth year
                year += 1900 if year > (datetime.now().year % 100) else 2000
            try:
                return int(day), int(month), year
            except ValueError:
                return None
    return None


def decode_nik(nik: str) -> dict:
    """Raises ValueError if nik isn't a clean 16-digit string."""
    if not (nik.isdigit() and len(nik) == 16):
        raise ValueError("NIK must be exactly 16 numeric digits")
    dd = int(nik[6:8])
    mm = int(nik[8:10])
    yy = int(nik[10:12])
    is_female = dd > 40
    birth_day = dd - 40 if is_female else dd
    return {
        "kode_provinsi": nik[0:2],
        "kode_kabupaten_kota": nik[2:4],
        "kode_kecamatan": nik[4:6],
        "birth_day": birth_day,
        "birth_month": mm,
        "birth_year_2digit": yy,
        "gender_from_nik": "PEREMPUAN" if is_female else "LAKI-LAKI",
        "nomor_urut": nik[12:16],
    }


def _check_nik_format(nik: str, checks: dict, errors: list) -> bool:
    ok_len = len(nik) == 16
    ok_digits = nik.isdigit()
    if ok_len and ok_digits:
        checks["nik_format"] = VALID
        return True
    checks["nik_format"] = INVALID
    if not ok_digits:
        errors.append("NIK tidak valid: harus hanya berisi angka")
    if not ok_len:
        errors.append(f"NIK tidak valid: panjang harus 16 digit (ditemukan {len(nik)})")
    return False


def _check_gender_consistency(nik_info: dict, jenis_kelamin: str, checks: dict, errors: list) -> None:
    jk_normalized = (jenis_kelamin or "").strip().upper()
    jk_normalized = "LAKI-LAKI" if jk_normalized in {"LAKI-LAKI", "LAKI2", "L", "PRIA"} else jk_normalized
    jk_normalized = "PEREMPUAN" if jk_normalized in {"PEREMPUAN", "P", "WANITA"} else jk_normalized

    if jk_normalized not in {"LAKI-LAKI", "PEREMPUAN"}:
        checks["gender_consistency"] = INVALID
        errors.append(f"Jenis kelamin tidak dikenali dari hasil OCR: {jenis_kelamin!r}")
        return

    if jk_normalized == nik_info["gender_from_nik"]:
        checks["gender_consistency"] = VALID
    else:
        checks["gender_consistency"] = INVALID
        errors.append("Jenis kelamin tidak sesuai dengan NIK")


def _check_birthdate_consistency(nik_info: dict, tempat_tgl_lahir: str, checks: dict, errors: list) -> None:
    parsed = _extract_date(tempat_tgl_lahir)
    if parsed is None:
        checks["date_format"] = INVALID
        checks["birthdate_consistency"] = SKIPPED
        errors.append("Format tanggal lahir tidak dapat dibaca")
        return

    checks["date_format"] = VALID
    day, month, year = parsed
    if day == nik_info["birth_day"] and month == nik_info["birth_month"] and (year % 100) == nik_info["birth_year_2digit"]:
        checks["birthdate_consistency"] = VALID
    else:
        checks["birthdate_consistency"] = INVALID
        errors.append("Tanggal lahir tidak sesuai dengan NIK")


def _check_expiry(berlaku_hingga: str, checks: dict, errors: list) -> None:
    text = (berlaku_hingga or "").strip().upper()
    if not text:
        checks["expiry_status"] = INVALID
        errors.append("Status berlaku tidak ditemukan")
        return
    if "SEUMUR HIDUP" in text:
        checks["expiry_status"] = VALID
        return
    parsed = _extract_date(text)
    if parsed is None:
        checks["expiry_status"] = INVALID
        errors.append("Format tanggal berlaku hingga tidak dapat dibaca")
        return
    day, month, year = parsed
    try:
        expiry_date = datetime(year, month, day)
    except ValueError:
        checks["expiry_status"] = INVALID
        errors.append("Tanggal berlaku hingga tidak valid")
        return
    if expiry_date.date() >= datetime.now().date():
        checks["expiry_status"] = VALID
    else:
        checks["expiry_status"] = INVALID
        errors.append("KTP sudah tidak berlaku (kedaluwarsa)")


def validate_ktp(ocr: KTPExtraction) -> ValidationResult:
    checks: dict = {}
    errors: list = []

    nik = (ocr.nik or "").strip()
    nik_ok = _check_nik_format(nik, checks, errors)

    if nik_ok:
        nik_info = decode_nik(nik)
        _check_gender_consistency(nik_info, ocr.jenis_kelamin, checks, errors)
        _check_birthdate_consistency(nik_info, ocr.tempat_tgl_lahir, checks, errors)
    else:
        checks["gender_consistency"] = SKIPPED
        checks["date_format"] = SKIPPED
        checks["birthdate_consistency"] = SKIPPED

    _check_expiry(ocr.berlaku_hingga, checks, errors)

    overall = VALID if all(v == VALID for v in checks.values()) else INVALID
    return ValidationResult(checks=checks, overall_status=overall, errors=errors)
