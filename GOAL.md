# Goal — S-Lib Assistant V1

## Single project goal

Bina **S-Lib Assistant V1** sebagai Windows companion app yang membolehkan operator:

1. scan barcode ISBN;
2. validate dan normalize ISBN;
3. resolve metadata buku daripada beberapa provider;
4. merge dan normalize metadata;
5. tunjuk preview dengan provenance/conflict;
6. edit jika perlu;
7. tekan `Isi S-Lib`;
8. isi field bibliografi S-Lib V1001r6 secara selamat;
9. operator semak;
10. operator tekan `Simpan` sendiri dalam S-Lib.

## Definition of done

V1 hanya dianggap selesai apabila:

- ISBN-10 dan ISBN-13 berfungsi;
- multi-provider lookup berfungsi;
- local cache berfungsi;
- conflict/missing data tidak disembunyikan;
- preview boleh diedit;
- S-Lib adapter mempunyai UIA/Win32 + keyboard fallback;
- tiada direct `.mdb` write;
- tiada automatic `Simpan`;
- test suite hijau;
- executable Windows boleh dibina;
- probe/diagnostic tool siap;
- real S-Lib office acceptance telah dijalankan atau projek berhenti secara eksplisit pada physical gate dengan probe package lengkap.

## Autonomous instruction

Teruskan autonomously melalui implementation, tests, packaging, docs dan internal QA.

Jangan berhenti untuk:
- routine confirmation;
- file naming;
- minor refactors;
- dependency choice yang reversible;
- unit-test failures yang boleh dibaiki;
- ordinary implementation decisions.

Berhenti hanya jika:
- real PC S-Lib information diperlukan dan tidak boleh disimulasikan;
- keputusan boleh menyebabkan direct mutation kepada database S-Lib;
- user perlu memilih polisi katalog sekolah yang tidak boleh diinfer;
- credential / secret diperlukan;
- tindakan external irreversible diperlukan.

## Non-goals V1

- menggantikan S-Lib;
- direct DB write;
- auto-save;
- patron/circulation automation;
- OCR harga;
- cloud sync;
- batch migration;
- modify S-Lib executable/files.
