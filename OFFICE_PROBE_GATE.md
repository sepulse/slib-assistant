# Office Probe Gate

Tujuan: dapatkan maklumat real S-Lib control tanpa coding di PC pejabat.

## Apa yang prime/worker mesti siapkan sebelum gate ini

- `SLibProbe.exe` atau equivalent diagnostic executable.
- Tidak memerlukan Python global jika boleh.
- Tidak menulis ke MDB.
- Tidak menekan Simpan.
- Output ke satu folder mudah dicopy.

## Operator steps di PC pejabat

1. Backup folder/data S-Lib.
2. Buka S-Lib.
3. Pergi ke `Kemaskini Bahan → Data Baru`.
4. Jangan simpan sebarang rekod.
5. Jalankan `SLibProbe.exe`.
6. Biarkan probe inspect window/control.
7. Jika diminta, klik/focus beberapa field sahaja.
8. Tutup probe.
9. Copy output folder.

Packaged executable:

dist/SLibProbe-OFFICE-GATE/SLibProbe.exe

## Output minimum

```text
probe-output/
├─ probe.json
├─ controls.txt
├─ environment.txt
└─ screenshots/   (optional)
```

## `probe.json` minimum

```json
{
  "slib_detected": true,
  "window_title": "Kemaskini Bahan",
  "process_name": "",
  "controls": [],
  "tab_order_observations": [],
  "notes": []
}
```

## Data yang diperlukan

- process name/path jika visible;
- top-level window title/class;
- child control classes;
- control names/automation IDs jika available;
- edit/combo positions in control tree;
- focused-control changes during Tab;
- modal behavior if any.

## Larangan

Probe tidak boleh:

- modify `.mdb`;
- save record;
- change S-Lib files;
- capture patron/member data;
- upload anything automatically.

## Selepas probe

User bawa `probe-output` kembali.

Prime:
1. map controls;
2. finalize adapter;
3. build new release candidate;
4. proceed to controlled 10-book office pilot.
