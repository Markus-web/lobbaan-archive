# lobbaan-archive

Daily archive of the Finnish Transparency Register (Avoimuusrekisteri) and related open data, kept
by [Lobbaan.fi](https://lobbaan.fi). Every record the sources ever published stays here with its full
version history, even when the source later edits or removes it. The git history is the audit trail:
each nightly commit shows exactly what changed in the sources that day.

Lobbaan.fi is an independent hobby project. It is not affiliated with the National Audit Office of
Finland (VTV), which keeps the register, or with any other authority.

## Contents

| Path | What it is |
|------|------------|
| `raw/<source>.json` | The latest successful copy of each source list, sorted by record key |
| `state/<kind>/<shard>.json` | Every record ever seen, with all versions: first seen, replaced on, how it was observed, which fields changed |
| `changes/YYYY/MM/DD.json` | Records added, edited, removed or restored on that day |
| `manifest/YYYY/MM/DD.json` | Fetch log for the day: HTTP status, record count, SHA-256 of the exact bytes received |
| `imports/` | Historical copies used to start the archive (Internet Archive captures from January and February 2025, Lobbaan.fi's own copy from 7 August 2026) |

Record kinds: `registrations`, `activities` (activity disclosures), `exits`, `penalties`, `terms`,
`targets` (lobbying targets: organizations and decision makers), `initiatives`
(kansalaisaloite.fi) and `prh` (company data from the PRH YTJ API, refreshed in rotation).

## Sources

- Avoimuusrekisteri open data API, `https://public.api.avoimuusrekisteri.fi` (VTV)
- Kansalaisaloite.fi API, `https://www.kansalaisaloite.fi/api/v1/initiatives`
- PRH open data, YTJ API v3, `https://avoindata.prh.fi/opendata-ytj-api/v3`
- Tutkihankintoja procurement data, `https://avoindata.suomi.fi/data/fi/dataset/tutkihankintoja-data` (summarized per organization on Lobbaan.fi; the CSV files themselves are not stored here, their checksums are)

The exact upstream bytes of each fetch are stored gzipped next to the manifest on Lobbaan.fi
(`https://lobbaan.fi/api/archive/file/<snapshotKey>`); the SHA-256 in the manifest lets you verify them.

## How versions are decided

- A record is identified by its diary number (terms and targets by id; initiatives by URI; companies by business ID).
- A new version is stored when the record's content changes. List fields the source returns in varying order (memberships, trade names, contacted targets) are compared as sets.
- Changes that only add new source fields, or only touch embedded copies of other records, are flagged `formatOnly`.
- A record is marked removed only when the day's fetch succeeded and was at least half the size of the current set. A failed fetch never removes anything.

The archiver source code lives with the Lobbaan.fi site (`archiver/`, documentation in `docs/ARCHIVE.md`).

## Licence

The data is published by its sources under Creative Commons Attribution 4.0
(<https://creativecommons.org/licenses/by/4.0/>). When you use it, credit the original source
(for the register: "Avoimuusrekisteri, Valtiontalouden tarkastusvirasto") and, if you like, Lobbaan.fi.
