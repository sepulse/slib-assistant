S-Lib Assistant - Office Probe Gate

1. Backup the S-Lib folder/data first.
2. Open S-Lib V1001r6.
3. Open Kemaskini Bahan -> Data Baru.
4. Do not save a record.
5. Run SLibProbe.exe.
6. The probe creates a probe-output folder.
7. Copy that whole output folder back to the development machine/chat.

The probe is read-only with respect to S-Lib data:
- it does not write to SLIBV1001.mdb
- it does not press Simpan
- it does not modify S-Lib files
- editable control contents are redacted from output

Expected files:
- probe.json
- controls.txt
- environment.txt

If SLibProbe reports Target window not found, confirm that the
Kemaskini Bahan window is open and visible, then run it again.
