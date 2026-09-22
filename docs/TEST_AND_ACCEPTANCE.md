# Test & Acceptance

## Dataset

20–30 books including:
- DBP;
- other Malaysian publishers;
- English/import;
- ISBN-10;
- ISBN-13;
- novel;
- dictionary/reference;
- atlas;
- >3 authors;
- corporate author;
- series;
- edition;
- incomplete metadata;
- missing metadata;
- conflicting metadata;
- duplicate ISBN.

Discovery samples:

```text
9789836276964
9780786849567
9781921344503
9789836294845
9789676126139
```

## Automated tests

- ISBN checksum/normalization
- provider failure isolation
- resolver conflict/provenance
- cache hit/miss/stale/offline
- wrong-window block
- blank skip
- abort
- no Save invocation
- no MDB write path

## Office pilot

Start with 10 books.

For each:
- scan;
- lookup;
- review;
- fill;
- compare;
- operator saves only if correct.

Then expand to 30–50 only if stable.
