from backend.schemas import KTPExtraction
from backend.validation import validate_ktp

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

result = validate_ktp(ocr)

print("=" * 50)
print("VALIDATION RESULT")
print("=" * 50)
print(result.model_dump())