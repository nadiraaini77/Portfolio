const dropzone = document.getElementById("dropzone");
const imageInput = document.getElementById("imageInput");

const previewImage = document.getElementById("previewImage");
const fileName = document.getElementById("fileName");

const placeholder = document.getElementById("placeholder");

const changeImageBtn = document.getElementById("changeImageBtn");

const processBtn = document.getElementById("processBtn");

const statusBadge = document.getElementById("statusBadge");

let selectedFile = null;

// =========================
// CLICK DROPZONE
// =========================

dropzone.addEventListener("click", () => {
  imageInput.click();
});

changeImageBtn.addEventListener("click", () => {
  imageInput.click();
});

// =========================
// FILE SELECT
// =========================

imageInput.addEventListener("change", (event) => {
  if (!event.target.files.length) return;

  loadPreview(event.target.files[0]);
});

// =========================
// DRAG & DROP
// =========================

dropzone.addEventListener("dragover", (event) => {
  event.preventDefault();

  dropzone.classList.add("dragover");
});

dropzone.addEventListener("dragleave", () => {
  dropzone.classList.remove("dragover");
});

dropzone.addEventListener("drop", (event) => {
  event.preventDefault();

  dropzone.classList.remove("dragover");

  if (!event.dataTransfer.files.length) return;

  loadPreview(event.dataTransfer.files[0]);
});

// =========================
// PREVIEW
// =========================

function loadPreview(file) {
  selectedFile = file;

  const reader = new FileReader();

  reader.onload = function (e) {
    previewImage.src = e.target.result;

    previewImage.style.display = "block";

    placeholder.style.display = "none";

    dropzone.style.display = "none";

    changeImageBtn.style.display = "block";
  };

  reader.readAsDataURL(file);

  fileName.textContent = file.name;

  processBtn.disabled = false;

  statusBadge.textContent = "Ready to Process";

  statusBadge.className = "ready";
}

// =========================
// PROCESS IMAGE
// =========================

processBtn.addEventListener("click", processImage);

async function processImage() {
  if (!selectedFile) return;

  const startTime = performance.now();

  processBtn.disabled = true;

  processBtn.classList.add("loading");

  processBtn.textContent = "Processing...";

  statusBadge.textContent = "Processing...";

  statusBadge.className = "processing";

  const formData = new FormData();

  formData.append("file", selectedFile);

  try {
    const response = await fetch("/process", {
      method: "POST",

      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      console.log(data);
      alert(data.detail);
      throw new Error(data.detail);
    }

    console.log(data);

    // =========================
    // ANALYSIS SUMMARY
    // =========================

    const processingTime = ((performance.now() - startTime) / 1000).toFixed(2);

    document.getElementById("classification").innerHTML = data.is_ktp
      ? '<span class="badge badge-blue">🇮🇩 Indonesian KTP</span>'
      : '<span class="badge badge-red">📄 Non-KTP</span>';

    const validationEl = document.getElementById("validation");

    validationEl.innerHTML =
      data.overall_status === "VALID"
        ? '<span class="badge badge-green">🟢 VALID</span>'
        : '<span class="badge badge-red">🔴 INVALID</span>';

    validationEl.style.color =
      data.overall_status === "VALID" ? "#16a34a" : "#dc2626";

    document.getElementById("ocrStatus").innerHTML =
      data.ocr_status === "SUCCESS"
        ? '<span class="badge badge-green">✅ SUCCESS</span>'
        : `<span class="badge badge-red">${data.ocr_status}</span>`;

    document.getElementById("processingTime").textContent =
      processingTime + " s";

    document.getElementById("databaseId").textContent = data.record_id ?? "-";

    // =========================
    // OCR RESULT
    // =========================

    const ocr = data.ocr_data || {};

    document.getElementById("ocrNik").textContent = ocr.nik || "-";

    document.getElementById("ocrNama").textContent = ocr.nama || "-";

    document.getElementById("ocrTTL").textContent = ocr.tempat_tgl_lahir || "-";

    document.getElementById("ocrGender").textContent = ocr.jenis_kelamin || "-";

    document.getElementById("ocrAlamat").textContent = ocr.alamat || "-";

    document.getElementById("ocrRTRW").textContent =
      `${ocr.rt || "-"} / ${ocr.rw || "-"}`;

    document.getElementById("ocrKelurahan").textContent = ocr.kelurahan || "-";

    document.getElementById("ocrKecamatan").textContent = ocr.kecamatan || "-";

    document.getElementById("ocrAgama").textContent = ocr.agama || "-";

    document.getElementById("ocrStatusPerkawinan").textContent =
      ocr.status_perkawinan || "-";

    document.getElementById("ocrPekerjaan").textContent = ocr.pekerjaan || "-";

    document.getElementById("ocrKewarganegaraan").textContent =
      ocr.kewarganegaraan || "-";

    document.getElementById("ocrBerlaku").textContent =
      ocr.berlaku_hingga || "-";

    if (data.overall_status === "VALID") {
      statusBadge.textContent = "Verification Success";
      statusBadge.className = "success";
    } else {
      statusBadge.textContent = "Verification Failed";
      statusBadge.className = "error";
    }
  } catch (error) {
    console.error(error);

    statusBadge.textContent = "Processing Failed";
    statusBadge.className = "error";

    alert("Failed to process image. Please try again.");
  } finally {
    processBtn.disabled = false;
    processBtn.classList.remove("loading");
    processBtn.textContent = "Process Image";
  }
}
