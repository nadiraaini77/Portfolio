from fastapi import (
    FastAPI,
    Request,
    UploadFile,
    File,
    HTTPException,
)
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from backend import ai_service, validation, database
from backend.schemas import (
    ClassificationResult,
    KTPExtraction,
    ValidationResult,
    ProcessResponse,
)

app = FastAPI(
    title="AI KTP Verification",
    description="AI-powered Indonesian ID Card Verification System",
    version="1.0.0"
)
@app.on_event("startup")
def startup():
    database.init_db()

# Folder static (CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Folder HTML
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {"request": request, "active_page": "home"},
    )

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
    
from backend.database import SessionLocal, get_all_records, records_to_dicts, records_to_history_dicts
from backend.models import KTPRecord


@app.get("/api/history")
def get_history_json():
    """JSON API — kept for programmatic access. The HTML history page below
    renders server-side instead of calling this."""
    db = SessionLocal()

    try:

        records = (
            db.query(KTPRecord)
            .order_by(KTPRecord.id.desc())
            .all()
        )

        history = []

        for item in records:

            history.append({

                "id": item.id,

                "nama": item.nama,

                "nik": item.nomor_dokumen,

                "status": item.status_validasi,

                "tanggal_upload": (
                    item.tanggal_upload.strftime("%Y-%m-%d %H:%M:%S")
                    if item.tanggal_upload
                    else "-"
                )

            })

        return history

    finally:

        db.close()


@app.get("/history", response_class=HTMLResponse)
async def history_page(request: Request):
    """Page 2 (last page): Database History — server-rendered, with CSV export."""
    db = SessionLocal()
    try:
        records = get_all_records(db)
        rows = records_to_history_dicts(records)
    finally:
        db.close()

    total = len(rows)
    total_valid = sum(1 for r in rows if r["status_validasi"] == "VALID")
    total_invalid = sum(1 for r in rows if r["status_validasi"] == "INVALID")

    return templates.TemplateResponse(
        request,
        "history.html",
        {
            "request": request,
            "active_page": "history",
            "records": rows,
            "total": total,
            "total_valid": total_valid,
            "total_invalid": total_invalid,
        },
    )


@app.get("/history/export")
def export_history_csv():
    """CSV export required by the project spec's 'Export CSV' output item."""
    import csv
    import io
    from fastapi.responses import StreamingResponse

    db = SessionLocal()
    try:
        records = get_all_records(db)
        rows = records_to_dicts(records)
    finally:
        db.close()

    buffer = io.StringIO()
    fieldnames = list(rows[0].keys()) if rows else [
        "id", "nama", "nomor_dokumen", "jenis_dokumen", "tanggal_upload",
        "status_validasi",
    ]
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    buffer.seek(0)

    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=riwayat_ktp.csv"},
    )