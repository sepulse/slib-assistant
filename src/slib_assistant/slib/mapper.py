from __future__ import annotations

from slib_assistant.models import BookMetadata


def map_book_to_slib(metadata: BookMetadata) -> dict[str, str]:
    authors = list(metadata.authors)
    return {
        "isbn": metadata.isbn13,
        "author_1": authors[0] if len(authors) > 0 else "",
        "author_2": authors[1] if len(authors) > 1 else "",
        "author_3": authors[2] if len(authors) > 2 else "",
        "title": metadata.title or "",
        "subtitle": metadata.subtitle or "",
        "classification": metadata.ddc or "",
        "edition": metadata.edition or "",
        "publication_place": metadata.publication_place or "",
        "publisher": metadata.publisher or "",
        "publication_year": str(metadata.publication_year or ""),
        "physical_description": metadata.physical_description or "",
        "page_count": str(metadata.page_count or ""),
        "dimensions": metadata.dimensions or "",
        "series": metadata.series or "",
        "notes": metadata.notes or "",
    }
