# S-Lib Field Mapping

## Main form

| S-Lib | Metadata | V1 |
|---|---|---:|
| No. Perolehan | local | No |
| No. Kawalan | local/S-Lib | No |
| ISBN/ISSN | isbn13 | Yes |
| Jenis Media | rule/preset | Conditional |
| Kod Produk | local | No |
| No. Naskhah | local | No |
| Kategori Bahan | school policy | Conditional |
| Pengarang | authors[0] | Yes |
| Pengarang 2 | authors[1] | Yes |
| Pengarang 3 | authors[2] | Yes |
| Judul | title | Yes |
| Judul Tambahan | subtitle | Yes |
| No. Panggilan | local policy | Review |
| Pengkelasan | ddc | Yes if sourced |

## Bibliographic/physical

| S-Lib | Metadata | V1 |
|---|---|---:|
| Edisi | edition | Yes |
| Tempat Terbit | publication_place | Yes |
| Penerbit | publisher | Yes |
| Tahun Terbit | publication_year | Yes/Review |
| Huraian Fizikal | physical_description | Yes |
| Muka Surat | page_count | Yes |
| Saiz | dimensions | Yes if sourced |
| Kenyataan Siri | series | Yes |
| Nota | notes | Review |
| Tajuk Perkara | subjects | Review initially |
| Bahasa | language | Conditional on dropdown mapping |

## Important

- >3 authors: do not silently discard; show extra count.
- DDC may be auto-filled only if sourced.
- Call number must not be invented without school rule.
- Price is not part of ISBN and is not default V1 autofill.
