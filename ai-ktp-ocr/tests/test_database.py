from backend.database import (
    init_db,
    get_session,
    save_record,
    get_all_records,
)
from backend.schemas import KTPExtraction
from backend.validation import validate_ktp

# Membuat database & tabel jika belum ada
init_db()

session = get_session()

# Dummy OCR data
ocr = KTPExtraction(
    nik="1234567890123456",
    nama="NADIRA AINI",
    tempat_tgl_lahir="JAKARTA, 07-02-2003",
    jenis_kelamin="PEREMPUAN",
    agama="ISLAM",
    alamat="JL. KALIURANG NO. 123",
    rt="001",
    rw="002",
    kelurahan="CATUR TUNGGAL",
    kecamatan="DEPOK",
    status_perkawinan="BELUM KAWIN",
    pekerjaan="CEO",
    kewarganegaraan="WNI",
    berlaku_hingga="SEUMUR HIDUP",
)

validation = validate_ktp(ocr)

record_id = save_record(session, ocr, validation)

print(f"Record berhasil disimpan dengan ID: {record_id}")

records = get_all_records(session)

print("\nSEMUA DATA")
print("=" * 50)

for r in records:
    print(
        f"""
ID      : {r.id}
Nama    : {r.nama}
NIK     : {r.nomor_dokumen}
Status  : {r.status_validasi}
Upload  : {r.tanggal_upload}
"""
    )

session.close()