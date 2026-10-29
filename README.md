# lobbaan-archive

Daily archive of the Finnish Transparency Register (Avoimuusrekisteri) and related open data, kept by [Lobbaan.fi](https://lobbaan.fi). Every record the sources ever published stays here with its full version history, even when the source later edits or removes it. The git history is the audit trail: each nightly commit shows exactly what changed in the sources that day.

Lobbaan.fi is an independent service run by [Markus Media](https://markusmedia.fi). It is not the Transparency Register and is not affiliated with the National Audit Office of Finland (VTV), which keeps the register, or with any other authority. The official data is always at the source, [avoimuusrekisteri.fi](https://www.avoimuusrekisteri.fi).

## Contents

| Path | What it is |
|------|------------|
| `raw/<source>.json` | The latest successful copy of each source list, sorted by record key |
| `state/<kind>/<shard>.json` | Every record ever seen, with all versions: first seen, replaced on, how it was observed, which fields changed ([schema](docs/schema/state-shard.schema.json)) |
| `changes/YYYY/MM/DD.json` | Records added, edited, removed or restored on that day ([schema](docs/schema/changes-day.schema.json)) |
| `manifest/YYYY/MM/DD.json`, `manifest/latest.json` | Fetch log for the day: HTTP status, record count, SHA-256 of the exact bytes received ([schema](docs/schema/manifest.schema.json)) |
| `imports/` | Historical copies used to start the archive (Internet Archive captures from January and February 2025, Lobbaan.fi's own copy from 7 August 2026) |
| `tools/validate.py` | Structure check run on every push |

Record kinds: `registrations`, `activities` (activity disclosures), `exits`, `penalties`, `terms`, `targets` (lobbying targets: organisations and decision makers), `initiatives` (kansalaisaloite.fi) and `prh` (company data from the PRH YTJ API, refreshed in rotation).

**Finding a record:** state files are sharded. The shard is the first byte of the SHA-1 of the record key, modulo 64, as two hex digits:

```bash
python3 -c "import hashlib,sys; print('%02x' % (hashlib.sha1(sys.argv[1].encode()).digest()[0] % 64))" ELI-24-447-R
# -> 14, so the registration is in state/registrations/14.json
```

Each lobbyist page on Lobbaan.fi links its exact files here ("Todisteet julkisessa arkistossa").

## Update schedule

Every night at about 01:30 UTC a GitHub Action fetches the sources, updates `state/`, writes the day's `changes/` and `manifest/` and commits. A fetch that fails or looks incomplete never removes anything; the manifest records it (`ok: false` or `partial: true`). Known gaps are listed in the manifests' `note` fields; for example kansalaisaloite.fi refuses requests from GitHub's servers, so that list is refreshed by hand.

## Verify the data

1. **Integrity of a fetch:** `manifest/YYYY/MM/DD.json` lists the SHA-256 of the exact bytes each source returned. The gzipped bytes are at `https://lobbaan.fi/api/archive/file/<snapshotKey>`:
   ```bash
   curl -s https://lobbaan.fi/api/archive/file/snapshots/2026-10-29/register-notification.json.gz | gunzip | sha256sum
   ```
2. **History of a record:** `git log -p -- state/registrations/14.json`, or the file's history on GitHub.
3. **A fixed state:** every month a release `YYYY-MM` publishes `SHA256SUMS` of all data files. After checking out the tag, `sha256sum -c SHA256SUMS` must pass.
4. **Structure:** `python3 tools/validate.py` (standard library only).

## Sources and licences

- Avoimuusrekisteri open data API, `https://public.api.avoimuusrekisteri.fi` (VTV), CC BY 4.0
- PRH open data, YTJ API v3, `https://avoindata.prh.fi/opendata-ytj-api/v3`, CC BY 4.0
- Kansalaisaloite.fi API, `https://www.kansalaisaloite.fi/api/v1/initiatives` (Ministry of Justice)
- Tutkihankintoja procurement data, `https://avoindata.suomi.fi/data/fi/dataset/tutkihankintoja-data`, CC BY 4.0 (summarised per organisation on Lobbaan.fi; the CSV files are not stored here, their checksums are)

See [LICENSE](LICENSE). In short: credit the original source (for the register: "Avoimuusrekisteri, Valtiontalouden tarkastusvirasto") and the archive.

## How to cite

Use [CITATION.cff](CITATION.cff) (GitHub shows "Cite this repository"), name the release you used, and the original source. Example:

> Avoimuusrekisteri, Valtiontalouden tarkastusvirasto (CC BY 4.0). Lobbaan.fi archive, release 2026-10, https://github.com/Markus-web/lobbaan-archive.

## How versions are decided

- A record is identified by its diary number (terms and targets by id; initiatives by URI; companies by business ID).
- A new version is stored when the record's content changes. List fields the source returns in varying order (memberships, trade names, contacted targets) are compared as sets.
- Changes that only add new source fields, or only touch embedded copies of other records, are flagged `formatOnly`.
- A record is marked removed only when the day's fetch succeeded and was at least half the size of the current set. A failed fetch never removes anything.

The archiver is part of Lobbaan.fi's own code, which is not public; its behaviour is documented here and in the data itself.

## Corrections and personal data

The archive keeps what the sources published. Errors in the source can only be corrected at the source. To report a problem, use the form at [lobbaan.fi/korjaukset](https://lobbaan.fi/korjaukset); handled reports are published in the corrections log there. Requests about personal data: info@lobbaan.fi (privacy notice: [lobbaan.fi/privacy](https://lobbaan.fi/privacy)). If data must be removed, the removal is announced in the corrections log; history is not rewritten silently.

## Size

The repository grows by a few megabytes a month. The nightly job warns when it passes 1 GB; raw upstream bytes stay outside git (Cloudflare R2), only their checksums are here.
