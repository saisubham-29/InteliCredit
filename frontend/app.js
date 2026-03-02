const companySelect = document.getElementById('company-select');
const uploadForm = document.getElementById('upload-form');
const analyzeBtn = document.getElementById('analyze-btn');
const officerForm = document.getElementById('officer-form');
const downloadBtn = document.getElementById('download-btn');

const uploadStatus = document.getElementById('upload-status');
const analysisStatus = document.getElementById('analysis-status');
const officerStatus = document.getElementById('officer-status');
const downloadStatus = document.getElementById('download-status');

const gaugeFill = document.getElementById('gauge-fill');
const gaugeValue = document.getElementById('gauge-value');
const driversList = document.getElementById('drivers-list');

async function loadCompanies() {
  const res = await fetch('/companies');
  const data = await res.json();
  companySelect.innerHTML = '';
  data.forEach((company) => {
    const option = document.createElement('option');
    option.value = company.id;
    option.textContent = `${company.name} (${company.sector})`;
    companySelect.appendChild(option);
  });
}

function updateGauge(score, band) {
  const pct = Math.min(100, Math.max(0, score));
  gaugeFill.style.width = `${pct}%`;
  gaugeValue.textContent = `${score} (${band})`;
}

function renderDrivers(drivers) {
  driversList.innerHTML = '';
  drivers.slice(0, 6).forEach((driver) => {
    const li = document.createElement('li');
    li.textContent = driver;
    driversList.appendChild(li);
  });
}

uploadForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  uploadStatus.textContent = 'Uploading...';

  const formData = new FormData();
  const files = document.getElementById('files').files;
  const companyName = document.getElementById('company-name').value;
  const sector = document.getElementById('company-sector').value;

  if (companyName) {
    formData.append('company_name', companyName);
  }
  if (sector) {
    formData.append('sector', sector);
  }

  Array.from(files).forEach((file) => formData.append('files', file));

  const res = await fetch('/upload-documents', {
    method: 'POST',
    body: formData,
  });

  if (res.ok) {
    uploadStatus.textContent = 'Upload complete.';
    await loadCompanies();
  } else {
    uploadStatus.textContent = 'Upload failed.';
  }
});

analyzeBtn.addEventListener('click', async () => {
  analysisStatus.textContent = 'Running analysis...';
  const companyId = companySelect.value;

  const res = await fetch('/analyze-company', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ company_id: companyId }),
  });

  if (!res.ok) {
    analysisStatus.textContent = 'Analysis failed.';
    return;
  }

  const data = await res.json();
  const report = data.risk_report;
  updateGauge(report.total_score, report.risk_band);
  renderDrivers(report.drivers || []);
  analysisStatus.textContent = 'Analysis complete.';
});

officerForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  officerStatus.textContent = 'Submitting...';

  const payload = {
    company_id: companySelect.value,
    factory_utilization_pct: document.getElementById('utilization').value || null,
    management_quality_notes: document.getElementById('management-notes').value,
    site_visit_observations: document.getElementById('site-notes').value,
  };

  const res = await fetch('/submit-officer-input', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  officerStatus.textContent = res.ok ? 'Inputs saved.' : 'Submission failed.';
});

downloadBtn.addEventListener('click', () => {
  const companyId = companySelect.value;
  if (!companyId) {
    downloadStatus.textContent = 'Select a company first.';
    return;
  }
  const url = `/download-cam/${companyId}`;
  const link = document.createElement('a');
  link.href = url;
  link.target = '_blank';
  link.click();
  downloadStatus.textContent = 'Downloading CAM...';
});

loadCompanies();
