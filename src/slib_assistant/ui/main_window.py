from __future__ import annotations

import threading
import tkinter as tk
from tkinter import messagebox, ttk

from slib_assistant.app import MetadataService
from slib_assistant.config import AppConfig
from slib_assistant.models import AppState, BookMetadata


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


class AssistantWindow:
    def __init__(self, root: tk.Tk, config: AppConfig, service: MetadataService):
        self.root = root
        self.config = config
        self.service = service
        self.metadata: BookMetadata | None = None
        self.state = AppState.IDLE
        self.entries: dict[str, tk.Entry] = {}
        self.status_vars: dict[str, tk.StringVar] = {}
        self.root.title("S-Lib Assistant")
        self.root.geometry("760x690")
        self.root.minsize(680, 560)
        self._build()

    def _build(self) -> None:
        top = ttk.Frame(self.root, padding=12)
        top.pack(fill="x")
        ttk.Label(top, text="ISBN").pack(side="left")
        self.isbn_var = tk.StringVar()
        isbn_entry = ttk.Entry(top, textvariable=self.isbn_var, width=28)
        isbn_entry.pack(side="left", padx=(8, 8))
        isbn_entry.bind("<Return>", lambda _event: self.lookup())
        ttk.Button(top, text="Cari", command=self.lookup).pack(side="left")
        ttk.Button(top, text="Refresh", command=lambda: self.lookup(True)).pack(
            side="left", padx=6
        )
        self.overall_status = tk.StringVar(value="Sedia")
        ttk.Label(top, textvariable=self.overall_status).pack(side="right")

        body = ttk.Frame(self.root, padding=(12, 0, 12, 8))
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)
        for row, (field_name, label) in enumerate(FIELDS):
            ttk.Label(body, text=label).grid(row=row, column=0, sticky="w", pady=3)
            entry = ttk.Entry(body)
            entry.grid(row=row, column=1, sticky="ew", padx=8, pady=3)
            self.entries[field_name] = entry
            status = tk.StringVar(value="MISSING")
            self.status_vars[field_name] = status
            ttk.Label(body, textvariable=status, width=10).grid(
                row=row, column=2, sticky="e"
            )

        self.source_text = tk.Text(body, height=8, wrap="word")
        self.source_text.grid(
            row=len(FIELDS), column=0, columnspan=3, sticky="nsew", pady=(10, 6)
        )
        body.rowconfigure(len(FIELDS), weight=1)

        bottom = ttk.Frame(self.root, padding=12)
        bottom.pack(fill="x")
        ttk.Button(bottom, text="Batal / ESC", command=self.abort).pack(side="left")
        self.root.bind("<Escape>", lambda _event: self.abort())
        ttk.Button(bottom, text="Isi S-Lib", command=self.fill_slib).pack(side="right")
        ttk.Label(bottom, text="S-Lib mapping: pending office verification").pack(
            side="right", padx=12
        )
        isbn_entry.focus_set()

    def lookup(self, force: bool = False) -> None:
        raw = self.isbn_var.get().strip()
        if not raw:
            return
        self.overall_status.set("Mencari...")
        self.state = AppState.LOOKING_UP
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


def run_ui(config: AppConfig, service: MetadataService) -> None:
    root = tk.Tk()
    AssistantWindow(root, config, service)
    root.mainloop()
