from __future__ import annotations

import logging
import queue
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from slib_assistant import __version__
from slib_assistant.app import MetadataService
from slib_assistant.config import AppConfig
from slib_assistant.models import AppState, BookMetadata
from slib_assistant.scanner import ScannerRouter
from slib_assistant.update import (
    UpdateError,
    UpdateInfo,
    check_for_update,
    download_update,
    launch_updater,
)


FIELDS = [
    ("title", "Judul"),
    ("subtitle", "Judul Tambahan"),
    ("authors", "Pengarang"),
    ("publisher", "Penerbit"),
    ("publication_place", "Tempat Terbit"),
    ("publication_year", "Tahun"),
    ("edition", "Edisi"),
    ("page_count", "Muka Surat"),
    ("dimensions", "Saiz"),
    ("series", "Siri"),
    ("ddc", "Pengkelasan"),
    ("language", "Bahasa"),
]

FIELD_HELP = {
    "title": "Judul utama buku. Semak ejaan dan tanda baca sebelum isi ke S-Lib.",
    "subtitle": "Judul tambahan/subtajuk jika tersedia. Kosong tidak akan menimpa medan S-Lib.",
    "authors": "Pisahkan beberapa pengarang dengan titik koma (;). Tiga pengarang pertama dipetakan ke S-Lib V1.",
    "publisher": "Nama penerbit seperti yang dilaporkan oleh sumber metadata.",
    "publication_place": "Tempat penerbitan. Biarkan kosong jika sumber tidak membekalkannya.",
    "publication_year": "Tahun penerbitan dalam nombor empat digit apabila tersedia.",
    "edition": "Maklumat edisi buku, contohnya Edisi Kedua.",
    "page_count": "Jumlah muka surat apabila tersedia daripada sumber.",
    "dimensions": "Saiz fizikal buku apabila tersedia.",
    "series": "Nama siri buku jika buku sebahagian daripada siri.",
    "ddc": "Nombor pengkelasan Dewey (DDC) jika sumber yang dipercayai membekalkannya.",
    "language": "Bahasa bahan. Semak jika provider menggunakan kod bahasa.",
}

CONFIDENCE_HELP = (
    "HIGH = lebih daripada satu sumber bersetuju; MEDIUM = satu sumber; "
    "REVIEW = sumber bercanggah/perlu semakan; MISSING = tiada metadata."
)


class ToolTip:
    def __init__(self, widget: tk.Widget, text: str):
        self.widget = widget
        self.text = text
        self.window: tk.Toplevel | None = None
        widget.bind("<Enter>", self._show, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<ButtonPress>", self._hide, add="+")

    def _show(self, _event: tk.Event | None = None) -> None:
        if self.window is not None:
            return
        x = self.widget.winfo_rootx() + 18
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self.window = tk.Toplevel(self.widget)
        self.window.wm_overrideredirect(True)
        self.window.wm_geometry(f"+{x}+{y}")
        ttk.Label(
            self.window,
            text=self.text,
            padding=(8, 5),
            relief="solid",
            borderwidth=1,
            wraplength=320,
        ).pack()

    def _hide(self, _event: tk.Event | None = None) -> None:
        if self.window is not None:
            self.window.destroy()
            self.window = None


class AssistantWindow:
    def __init__(self, root: tk.Tk, config: AppConfig, service: MetadataService):
        self.root = root
        self.config = config
        self.service = service
        self.metadata: BookMetadata | None = None
        self.state = AppState.IDLE
        self.entries: dict[str, tk.Entry] = {}
        self.status_vars: dict[str, tk.StringVar] = {}
        self.scanner_router: ScannerRouter | None = None
        self.scanner_events: queue.SimpleQueue[tuple[str, str]] = queue.SimpleQueue()
        self._closing = False
        self.root.title("S-Lib Assistant")
        self.root.geometry("760x690")
        self.root.minsize(680, 560)
        self._build()
        self._start_scanner_router()
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        if self.config.check_updates_on_startup:
            self.root.after(1200, lambda: self.check_updates(manual=False))

    def _build(self) -> None:
        menubar = tk.Menu(self.root)
        help_menu = tk.Menu(menubar, tearoff=False)
        help_menu.add_command(
            label="Semak Kemas Kini", command=lambda: self.check_updates(manual=True)
        )
        help_menu.add_separator()
        help_menu.add_command(label="Tentang", command=self.show_about)
        menubar.add_cascade(label="Bantuan", menu=help_menu)
        self.root.configure(menu=menubar)

        top = ttk.Frame(self.root, padding=12)
        top.pack(fill="x")
        ttk.Label(top, text="ISBN").pack(side="left")
        self.isbn_var = tk.StringVar()
        self.isbn_entry = ttk.Entry(top, textvariable=self.isbn_var, width=28)
        self.isbn_entry.pack(side="left", padx=(8, 8))
        self.isbn_entry.bind("<Return>", lambda _event: self.lookup())
        ToolTip(
            self.isbn_entry,
            "Imbas barcode ISBN atau taip ISBN-10/ISBN-13, kemudian tekan Enter.",
        )
        search_button = ttk.Button(top, text="Cari", command=self.lookup)
        search_button.pack(side="left")
        ToolTip(search_button, "Cari metadata buku daripada sumber yang diaktifkan.")
        refresh_button = ttk.Button(
            top, text="Refresh", command=lambda: self.lookup(True)
        )
        refresh_button.pack(side="left", padx=6)
        ToolTip(
            refresh_button,
            "Abaikan cache tempatan dan cari semula metadata daripada provider.",
        )
        self.scanner_enabled = tk.BooleanVar(value=True)
        scanner_toggle = ttk.Checkbutton(
            top,
            text="Scanner Mode",
            variable=self.scanner_enabled,
            command=self._toggle_scanner_mode,
        )
        scanner_toggle.pack(side="left", padx=(4, 6))
        ToolTip(
            scanner_toggle,
            "Bila aktif, scan ISBN pada medan ISBN/ISSN S-Lib dialihkan terus "
            "ke Assistant tanpa Scanner Guard berasingan.",
        )
        self.overall_status = tk.StringVar(value="Sedia")
        ttk.Label(top, textvariable=self.overall_status).pack(side="right")

        body = ttk.Frame(self.root, padding=(12, 0, 12, 8))
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)
        for row, (field_name, label) in enumerate(FIELDS):
            label_widget = ttk.Label(body, text=label)
            label_widget.grid(row=row, column=0, sticky="w", pady=3)
            entry = ttk.Entry(body)
            entry.grid(row=row, column=1, sticky="ew", padx=8, pady=3)
            self.entries[field_name] = entry
            status = tk.StringVar(value="MISSING")
            self.status_vars[field_name] = status
            status_widget = ttk.Label(body, textvariable=status, width=10)
            status_widget.grid(row=row, column=2, sticky="e")
            help_text = FIELD_HELP[field_name]
            ToolTip(label_widget, help_text)
            ToolTip(entry, help_text)
            ToolTip(status_widget, CONFIDENCE_HELP)

        self.source_text = tk.Text(body, height=8, wrap="word")
        self.source_text.grid(
            row=len(FIELDS), column=0, columnspan=3, sticky="nsew", pady=(10, 6)
        )
        ToolTip(
            self.source_text,
            "Menunjukkan provider yang digunakan, konflik metadata dan perkara yang perlu disemak staf.",
        )
        body.rowconfigure(len(FIELDS), weight=1)

        bottom = ttk.Frame(self.root, padding=12)
        bottom.pack(fill="x")
        abort_button = ttk.Button(bottom, text="Batal / ESC", command=self.abort)
        abort_button.pack(side="left")
        ToolTip(abort_button, "Kosongkan rekod semasa dan kembali ke keadaan sedia.")
        self.root.bind("<Escape>", lambda _event: self.abort())
        fill_button = ttk.Button(bottom, text="Isi S-Lib", command=self.fill_slib)
        fill_button.pack(side="right")
        ToolTip(
            fill_button,
            "Isi medan S-Lib selepas mapping pejabat disahkan. Butang ini tidak menekan Simpan.",
        )
        ttk.Label(bottom, text="S-Lib mapping: pending office verification").pack(
            side="right", padx=12
        )
        self.isbn_entry.focus_set()

    def _start_scanner_router(self) -> None:
        self.scanner_router = ScannerRouter(
            on_scan=lambda isbn: self.scanner_events.put(("scan", isbn)),
            on_status=lambda status: self.scanner_events.put(("status", status)),
        )
        started = self.scanner_router.start()
        if not started:
            self.scanner_enabled.set(False)
        self.root.after(50, self._poll_scanner_events)

    def _poll_scanner_events(self) -> None:
        if self._closing:
            return
        while True:
            try:
                kind, value = self.scanner_events.get_nowait()
            except queue.Empty:
                break
            if kind == "scan":
                self._receive_scanned_isbn(value)
            else:
                self._scanner_status(value)
        self.root.after(50, self._poll_scanner_events)

    def _scanner_status(self, status: str) -> None:
        logging.info("Scanner: %s", status)
        lowered = status.casefold()
        if "gagal" in lowered or "fail-open" in lowered:
            self.overall_status.set(status)

    def _toggle_scanner_mode(self) -> None:
        if self.scanner_router is None:
            self.scanner_enabled.set(False)
            return
        enabled = self.scanner_enabled.get()
        self.scanner_router.set_enabled(enabled)
        self.overall_status.set("Scanner Mode aktif" if enabled else "Scanner Mode dimatikan")

    def _receive_scanned_isbn(self, isbn: str) -> None:
        """Receive a scan directly from the in-process Windows scanner router."""
        if not self.scanner_enabled.get():
            return
        self.root.deiconify()
        self.root.lift()
        try:
            self.root.focus_force()
        except tk.TclError:
            pass
        self.isbn_var.set(isbn)
        self.isbn_entry.icursor("end")
        self.isbn_entry.focus_set()
        self.overall_status.set(f"ISBN scanner diterima: {isbn}")
        self.root.after(80, self.lookup)

    def show_about(self) -> None:
        messagebox.showinfo(
            "Tentang S-Lib Assistant",
            f"S-Lib Assistant v{__version__}\n\n"
            "Pembantu metadata untuk S-Lib V1001r6.\n"
            "S-Lib kekal sebagai sistem rekod rasmi dan Simpan kekal tindakan staf.",
        )

    def check_updates(self, manual: bool = False) -> None:
        if self.state == AppState.LOOKING_UP and manual:
            messagebox.showinfo(
                "S-Lib Assistant",
                "Tunggu carian metadata selesai sebelum menyemak kemas kini.",
            )
            return
        if manual:
            self.overall_status.set("Menyemak kemas kini...")
        threading.Thread(
            target=self._check_updates_thread, args=(manual,), daemon=True
        ).start()

    def _check_updates_thread(self, manual: bool) -> None:
        try:
            info = check_for_update()
        except Exception as exc:
            self.root.after(0, lambda: self._handle_update_error(exc, manual))
            return
        self.root.after(0, lambda: self._handle_update_result(info, manual))

    def _handle_update_error(self, exc: Exception, manual: bool) -> None:
        logging.info("Update check failed: %s", exc)
        if manual:
            self.overall_status.set("Semakan kemas kini gagal")
            messagebox.showwarning(
                "Kemas Kini",
                "Tidak dapat menyemak kemas kini sekarang. "
                "Aplikasi masih boleh digunakan seperti biasa.\n\n"
                f"{exc}",
            )

    def _handle_update_result(
        self, info: UpdateInfo | None, manual: bool
    ) -> None:
        if info is None:
            if manual:
                self.overall_status.set("Versi terkini")
                messagebox.showinfo(
                    "Kemas Kini",
                    f"S-Lib Assistant v{__version__} ialah versi terkini.",
                )
            return
        self.overall_status.set(f"Kemas kini v{info.version} tersedia")
        notes = info.notes.strip()
        if len(notes) > 900:
            notes = notes[:900].rstrip() + "..."
        detail = f"Versi {info.version} tersedia."
        if notes:
            detail += f"\n\nPerubahan:\n{notes}"
        detail += (
            "\n\nMuat turun dan pasang sekarang? "
            "Aplikasi akan ditutup dan dibuka semula selepas kemas kini."
        )
        if messagebox.askyesno("Kemas Kini S-Lib Assistant", detail):
            self._start_update_download(info)

    def _start_update_download(self, info: UpdateInfo) -> None:
        self.overall_status.set(f"Memuat turun v{info.version}...")
        threading.Thread(
            target=self._download_update_thread, args=(info,), daemon=True
        ).start()

    def _download_update_thread(self, info: UpdateInfo) -> None:
        try:
            package = download_update(info, self.config.data_dir)
            launch_updater(package)
        except (UpdateError, OSError, ValueError) as exc:
            self.root.after(0, lambda: self._handle_update_install_error(exc))
            return
        except Exception as exc:
            logging.exception("Unexpected update failure")
            self.root.after(0, lambda: self._handle_update_install_error(exc))
            return
        self.root.after(0, self._close_for_update)

    def _handle_update_install_error(self, exc: Exception) -> None:
        self.overall_status.set("Kemas kini gagal")
        messagebox.showerror(
            "Kemas Kini Gagal",
            "Kemas kini tidak dipasang. Versi semasa dikekalkan.\n\n"
            f"{exc}",
        )

    def _close_for_update(self) -> None:
        self.overall_status.set("Memasang kemas kini...")
        self.root.after(150, self.root.destroy)

    def lookup(self, force: bool = False) -> None:
        raw = self.isbn_var.get().strip()
        if not raw:
            return
        self.overall_status.set("Mencari...")
        self.state = AppState.LOOKING_UP
        if self.scanner_router is not None:
            self.scanner_router.set_enabled(False)
        threading.Thread(
            target=self._lookup_thread, args=(raw, force), daemon=True
        ).start()

    def _lookup_thread(self, raw: str, force: bool) -> None:
        try:
            metadata = self.service.lookup(raw, force_refresh=force)
        except Exception as exc:
            self.root.after(0, lambda: self._show_error(str(exc)))
            return
        self.root.after(0, lambda: self._render(metadata))

    def _show_error(self, message: str) -> None:
        self.overall_status.set("Ralat")
        self.state = AppState.ERROR
        if self.scanner_router is not None:
            self.scanner_router.set_enabled(self.scanner_enabled.get())
        messagebox.showerror("S-Lib Assistant", message)

    def _render(self, metadata: BookMetadata) -> None:
        self.metadata = metadata
        self.state = AppState.REVIEW
        self.isbn_var.set(metadata.isbn13)
        for field_name, _label in FIELDS:
            widget = self.entries[field_name]
            widget.delete(0, "end")
            value = getattr(metadata, field_name)
            if isinstance(value, list):
                value = "; ".join(value)
            if value not in (None, ""):
                widget.insert(0, str(value))
            confidence = metadata.field_confidence.get(field_name)
            self.status_vars[field_name].set(
                confidence.value if confidence else "MISSING"
            )
        self.source_text.delete("1.0", "end")
        sources = ", ".join(metadata.sources) if metadata.sources else "tiada"
        self.source_text.insert("end", "Sumber: " + sources + "\n")
        for conflict in metadata.conflicts:
            self.source_text.insert(
                "end",
                f"Semak {conflict.field}: {conflict.selected!r}; alternatif {conflict.alternatives!r}\n",
            )
        if len(metadata.authors) > 3:
            self.source_text.insert(
                "end",
                f"{len(metadata.authors) - 3} pengarang tambahan perlu disemak manual.\n",
            )
        self.overall_status.set("Sedia untuk semakan")
        self.state = AppState.READY_TO_FILL
        if self.scanner_router is not None:
            self.scanner_router.set_enabled(self.scanner_enabled.get())

    def _apply_edits(self) -> None:
        if self.metadata is None:
            return
        for field_name, _label in FIELDS:
            raw = self.entries[field_name].get().strip()
            if field_name == "authors":
                value = [x.strip() for x in raw.split(";") if x.strip()]
            elif field_name in {"publication_year", "page_count"}:
                value = int(raw) if raw.isdigit() else None
            else:
                value = raw or None
            setattr(self.metadata, field_name, value)

    def fill_slib(self) -> None:
        if self.metadata is None:
            messagebox.showinfo("S-Lib Assistant", "Cari dan semak buku dahulu.")
            return
        self._apply_edits()
        messagebox.showwarning(
            "Office verification diperlukan",
            "Autofill belum diaktifkan kerana control mapping S-Lib belum disahkan. "
            "Jalankan SLibProbe di PC pejabat dahulu.",
        )

    def abort(self) -> None:
        self.overall_status.set("Dibatalkan")
        self.state = AppState.ABORTED
        self.isbn_var.set("")
        self.metadata = None
        for entry in self.entries.values():
            entry.delete(0, "end")
        for status in self.status_vars.values():
            status.set("MISSING")
        self.source_text.delete("1.0", "end")
        if self.scanner_router is not None:
            self.scanner_router.set_enabled(self.scanner_enabled.get())
        self.isbn_entry.focus_set()

    def close(self) -> None:
        self._closing = True
        if self.scanner_router is not None:
            self.scanner_router.stop()
        self.root.destroy()


def run_ui(config: AppConfig, service: MetadataService) -> None:
    root = tk.Tk()
    AssistantWindow(root, config, service)
    root.mainloop()
