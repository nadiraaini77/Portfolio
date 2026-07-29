from pathlib import Path

from backend.ai_service import classify_document, extract_ktp_fields

# Ganti nama file jika berbeda
IMAGE_PATH = Path("samples/ktp1.png")

if not IMAGE_PATH.exists():
    raise FileNotFoundError(f"Gambar tidak ditemukan: {IMAGE_PATH}")

image_bytes = IMAGE_PATH.read_bytes()

print("=" * 50)
print("DOCUMENT CLASSIFICATION")
print("=" * 50)

classification = classify_document(image_bytes)

print(classification)

if classification.is_ktp:
    print("\n" + "=" * 50)
    print("OCR RESULT")
    print("=" * 50)

    result = extract_ktp_fields(image_bytes)

    print("\n" + "=" * 50)
    print("HASIL OCR KTP")
    print("=" * 50)
    for field, value in result.model_dump().items():
        print(f"{field.replace('_', ' ').title():25}: {value}")
    


else:
    print("\nBukan KTP. OCR tidak dijalankan.")