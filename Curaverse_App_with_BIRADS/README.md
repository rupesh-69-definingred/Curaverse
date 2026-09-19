# Curaverse — Prototype (Redesigned UI + Working Ultrasound)

A single-file Flask app that recreates the Curaverse reference UI (light &
dark themes) with a phone-number → OTP → dashboard login flow, subtle UI
animations, and **working** image-processing pipelines for both mammogram
images (Image Processing) and ultrasound scans (Ultrasound).

## What's new in this build
- **UI matches the reference screenshots**: sidebar, top bar, hero banner,
  stat cards, Recent Patients / Upcoming Appointments panels, footer — in
  both light and dark mode (toggle switch top-right).
- **Login flow now matches the reference exactly**: enter mobile number →
  6-digit OTP screen (auto-advancing boxes, countdown timer, Resend OTP,
  Change Number) → dashboard.
- **Ultrasound is fully working**, not a placeholder: upload an ultrasound
  image and it runs through the same preprocessing → K-Means segmentation
  pipeline as Image Processing, with real per-cluster statistics, a live
  pie chart, and an analysis note — labelled with ultrasound-specific terms
  (Hypoechoic / Isoechoic / Hyperechoic).
- **Animations**: fade-in panels, floating hero illustration, animated
  count-up numbers on stat cards, a loading overlay while an image is being
  processed, and a shake animation on an incomplete OTP.
- Demo data is seeded on first run so the dashboard numbers match the
  reference design (12 patients, 3 appointments, 5 reports, 2 pending).

## Login
1. Enter any 10-digit mobile number → Send OTP.
2. Enter the OTP shown in the demo note (**123456** always works).
3. You're in the dashboard.

> This remains a **prototype**: OTPs are simulated locally (no SMS is sent),
> and all image-analysis output is a demo visual segmentation — not a
> medical diagnosis. Every imaging screen carries this disclaimer.

## New: BI-RADS Report Analyzer
A new sidebar item, **BI-RADS Report** (`/birads-report`), has been added.
It uses `ultrasound_module.py` (OCR + text parsing, unchanged from the
supplied module) to read an uploaded ultrasound **report** — a photo/scan
or PDF of the radiologist's text report, not the ultrasound image itself —
and automatically extract:
- BI-RADS category and plain-English risk level
- Breast side, lesion type, size, location/clock position
- Lymph node mentions
- Recommendations (e.g. biopsy, follow-up, clinical correlation)
- A generated plain-text summary

Results are saved per patient (new `birads_reports` table, created
automatically) and shown alongside the existing Image Processing and
Ultrasound (K-Means) features — nothing about those was changed.

**Extra setup for this feature only:**
- `pip install -r requirements.txt` now also installs `easyocr` and
  `pdf2image` (the two extra dependencies the module needs). The OCR
  model is downloaded automatically the first time you analyze a report
  (needs internet access once).
- Image reports (.jpg/.png/etc.) work out of the box. PDF reports need
  [Poppler](https://github.com/oschwartz10612/poppler-windows/releases)
  extracted so that `poppler-26.07.0\Library\bin` sits under a `poppler`
  folder next to `app.py` (this matches the path `ultrasound_module.py`
  already expects) — otherwise PDF uploads on this feature will fail with
  a "Could not analyze this report" error while everything else keeps
  working.

## Project structure
```text
Curaverse/
├── app.py                 # Flask application (UI + logic, single file)
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── README_VSCODE.md       # VS Code setup notes
├── .gitignore
├── .vscode/
│   ├── launch.json
│   └── settings.json
├── uploads/
│   └── .keep
└── patients.db             # Created automatically on first run
```

## Run it (Windows + VS Code)
1. Install Python 3.10+ and VS Code with the Python extension.
2. Extract this ZIP and open the folder in VS Code.
3. Terminal → New Terminal, then:
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1        # or .venv\Scripts\activate.bat in cmd
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   python app.py
   ```
4. Open http://127.0.0.1:5000

Press `Ctrl+C` in the terminal to stop the server.
