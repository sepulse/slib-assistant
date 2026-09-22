# S-Lib Assistant — Office Handoff

This handoff is for continuing the project from the office PC without the home
Chat On Steroids tunnel.

## What to take to the office

Use the latest SLibAssistant-OFFICE-HANDOFF-*.zip bundle. It contains:

- SLibAssistant.exe — PRE-OFFICE RC metadata assistant.
- SLibProbe.exe — read-only S-Lib control probe.
- config.example.toml.
- office probe instructions.

## Tomorrow at the office

1. Open ChatGPT on the web using the same ChatGPT account.
2. Open this same S-Lib Assistant conversation if it is available in chat
   history. If continuing in a new chat, link or mention the GitHub repository
   and upload the probe output described below.
3. Back up the S-Lib application/data folder before testing.
4. Open S-Lib V1001r6.
5. Navigate to Kemaskini Bahan -> Data Baru.
6. Do not press Simpan.
7. Run SLibProbe.exe.
8. When it finishes, zip the generated probe-output folder.
9. Upload that zip to ChatGPT.

Expected probe files:

- probe.json
- controls.txt
- environment.txt

The probe is intentionally read-only with respect to S-Lib. It does not write
to SLIBV1001.mdb, does not modify the S-Lib installation, and does not press
Simpan.

## What happens after the probe is returned

The next implementation step is to map the real S-Lib controls and verify:

- editable fields and dropdowns,
- automation IDs/classes/names,
- tab order where UI Automation is insufficient,
- window/form anchors,
- safe pre-fill verification,
- blank-field skipping,
- abort behaviour.

Only after this evidence is available should the real Isi S-Lib action be
enabled for an office pilot.

## Important safety rules

- Never write directly to the MDB.
- Never auto-click Simpan.
- Never fabricate missing metadata.
- Human staff remain the final review/save checkpoint.
- Do not describe autofill as confirmed on S-Lib until office evidence passes.
