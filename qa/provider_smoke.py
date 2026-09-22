from __future__ import annotations

from slib_assistant.providers import GoogleBooksProvider, OpenLibraryProvider


ISBN = "9789836276964"


def main() -> int:
    successful = 0
    for provider in (GoogleBooksProvider(), OpenLibraryProvider()):
        try:
            record = provider.lookup(ISBN, 8)
        except Exception as exc:
            print(
                provider.name,
                "ERROR",
                type(exc).__name__,
                str(exc),
            )
            continue
        successful += 1
        print(
            provider.name,
            "OK",
            record.data.get("title"),
            sorted(record.data),
        )
    print("successful_providers", successful)
    return 0 if successful >= 1 else 1


if __name__ == "__main__":
    raise SystemExit(main())
