"""
Optional standalone API. The deployed Streamlit app does NOT call this over
HTTP — it imports ai_service/validation/database directly (see the hybrid
architecture decision). This file exists so the same backend/ package can
also run as a real FastAPI service if you ever want to serve other clients.

Run with: uvicorn backend.main:app --reload
"""
from fastapi import FastAPI, UploadFile, File, HTTPException

from backend import ai_service, validation, database
from backend.schemas import (
    ClassificationResult,
    KTPExtraction,
    ValidationResult,
    ProcessResponse,
)

app = FastAPI(title="AI KTP Classifier & OCR API")

@app.on_event("startup")
def on_startup():
    database.init_db()


@app.post("/classify", response_model=ClassificationResult)
async def classify(file: UploadFile = File(...)):
    image_bytes = await file.read()
    try:
        return ai_service.classify_document(image_bytes)
    except ai_service.OpenRouterError as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/ocr", response_model=KTPExtraction)
async def ocr(file: UploadFile = File(...)):
    image_bytes = await file.read()
    try:
        return ai_service.extract_ktp_fields(image_bytes)
    except ai_service.OpenRouterError as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/validate", response_model=ValidationResult)
async def validate(ocr_data: KTPExtraction):
    return validation.validate_ktp(ocr_data)


@app.post("/process", response_model=ProcessResponse)
async def process(file: UploadFile = File(...)):

    image_bytes = await file.read()

    try:

        classification = ai_service.classify_document(image_bytes)

        if not classification.is_ktp:

            return ProcessResponse(
                is_ktp=False,
                overall_status="INVALID",
                ocr_status="SKIPPED",
                ocr_data=KTPExtraction(),
                validation_errors=["Dokumen bukan KTP Indonesia."],
                record_id=None
            )

        ocr = ai_service.extract_ktp_fields(image_bytes)

        validation_result = validation.validate_ktp(ocr)

        session = database.get_session()

        try:

            record_id = database.save_record(
                session,
                ocr,
                validation_result
            )

        finally:

            session.close()

        return ProcessResponse(
            is_ktp=True,
            overall_status=validation_result.overall_status,
            ocr_status="SUCCESS",
            ocr_data=ocr,
            validation_errors=validation_result.errors,
            record_id=record_id
        )

    except ai_service.OpenRouterError as e:

        raise HTTPException(
            status_code=502,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )