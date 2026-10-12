# Release identities and version history

This repository stores release artifacts, not a single application. It has no
repository-wide application VERSION. `release-history.json` is a read-only,
reviewable provenance index observed on 2026-10-12: 17 application identities,
18 application releases and the separate `catalog` release. It does not replace
the signed catalog consumed by R-Box. All existing tags, assets and release
metadata remain unchanged.

Run with Python 3.11+:

```sh
python3 version_catalog.py show
python3 version_catalog.py check
python3 -m unittest discover -s tests -p 'test_version_catalog.py'
```

The validator runs offline and never writes, signs, commits, tags, uploads or
publishes. Source manifest versions are managed in each application's source
repository; the central preview artifact version can differ from a development
manifest. Central tags identify this artifact repository's commit, not an
application source commit. The exact source commits quoted in release evidence
are recorded separately.

`r-labelimg` remains explicitly unresolved. Its published Rust/Slint product
cannot be assigned to the current Python/Qt `a1112/labelImg` repository: neither
quoted source commit was found there. Preserve the artifacts while reconciling
that identity with source evidence before any further release.

R-Image retains both 0.1.0-preview.1 and 0.1.1-preview.1. The `catalog` tag has no
application SemVer. Historical R-MD 0.01/v0.0.1 source tags are not normalized or
replaced by its central preview tag.

For a future authorized release, use the existing source repository packaging,
attestation, acceptance and signing workflow documented in
[a1112/R-Box](https://github.com/a1112/R-Box/blob/main/docs/releasing.md).
Add an observed release to this provenance index only after publication is
verified, retaining earlier entries and running the checks above. Bumping this
index cannot release an application. These checks validate metadata only; they
do not verify downloadable bytes, signatures, platform packaging or native
runtime acceptance.
