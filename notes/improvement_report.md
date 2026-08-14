# Improvement Report — Fallen Aces Russian Localization

> Prepared for repository improvement. This is an **analysis only** — no changes were
> applied. Items are grouped by area, each with a one-line description, priority
> (P0 = must fix / blocks release credibility, P1 = should fix, P2 = nice to have),
> and effort (S/M/L). A senior engineer can act on any item without further context.

---

## 1. Documentation

| # | Item | Priority | Effort |
|---|------|----------|--------|
| 1.1 | **README status table is factually wrong**: it still lists "Меню / UI (зашито в DLL/ассеты) \| ⬜ Не переведено", but `mod_ui/` now ships a working XUnity.AutoTranslator dictionary. Update the row to "✅ Переведено (XUnity.AutoTranslator)" or mark partial, and delete the stale paragraph claiming UI is untranslated. | P0 | S |
| 1.2 | **README does not document `mod_ui/` at all**: the "Структура репозитория" tree omits `mod_ui/`, `notes/`, `packs/`, `strings.json`; and the "Установка" section only covers the narrative `mod/` → `AcesData` swap. Add a "Установка локализации UI" section (or link to `notes/ui-localization.md`) covering BepInEx + AutoTranslator + dictionary + font bundle, and the rollback path (delete BepInEx/, winhttp.dll, doorstop_config.ini). | P0 | M |
| 1.3 | **AGENTS.md status section is stale**: line 54 still says "⬜ Меню / UI ... НЕ переведено (опционально, позже)". Update to reflect that `mod_ui/` exists, and add `mod_ui/` to the repo-structure documentation. | P1 | S |
| 1.4 | **Add CONTRIBUTING.md** describing: how to report a bad line, the mandatory rules for editing `mod/` files (only text inside quotes, keep line count, keep filenames, UTF-8 no BOM, keep rich-text tags), how to contribute to the `mod_ui/` dictionary (format `orig=trans`, keep `{0}` placeholders), and the glossary-first workflow. | P1 | M |
| 1.5 | **Add GitHub issue templates**: a "Translation bug report" template (game location, English source, current Russian, suggested Russian, screenshot) and a "Tooling bug" template. This lowers the bar for the community proofreading the AI translation. | P2 | S |
| 1.6 | **Add a CHANGELOG.md** and start a versioning scheme (the repo ships a "v1.0" zip but there is no changelog or tag discipline). | P2 | S |

---

## 2. Tooling / Pipeline

| # | Item | Priority | Effort |
|---|------|----------|--------|
| 2.1 | **Hardcoded machine-specific paths block reproducibility**: every script hardcodes `GAME = "/mnt/c/Program Files (x86)/Steam/steamapps/common/Fallen Aces"` and `BACKUP = ".../Fallen Aces_backup_txt"` (WSL mounts). Read these from `env` (e.g. `FALLEN_ACES_DIR`, `FALLEN_ACES_BACKUP_DIR`) with the current paths as defaults. Without this, no contributor or CI can run the pipeline. | P0 | S |
| 2.2 | **`verify.py` is incomplete / misleading**: (a) the line-count check is a no-op — `n_lines_orig` is computed then never used, and it counts only records, not actual file lines; (b) it validates files under `GAME` (live AcesData), not the generated `mod/` output, so it cannot be run in CI without the game installed. Rewrite it to validate `mod/` itself: assert byte-identical line count vs the committed source, no BOM, valid UTF-8, balanced `{ T }`/`I N {}` structure, and that every file referenced by `SpeakDialogue` exists. | P1 | M |
| 2.3 | **`inject_rest.py` replace is fragile**: `new_txt.replace(e["orig"], new_fragment, 1)` replaces only the **first** occurrence. If the same `orig` appears twice in one file, the second stays English and the script silently under-reports (`errors` only catches "not found"). Replace by anchored index (use `find` in a loop or replace all occurrences that map to the same id), and add a leftover-English warning. | P1 | S |
| 2.4 | **No automated tests**: zero test files. Add a `tests/` dir with a small pytest suite (stdlib-only, no install needed) covering the regex extractors (`extract_subtitles` / `extract_rest` prefix/text/suffix splitting), inject round-trip on a fixture, and `verify`'s BOM/line-count checks. This protects the translation data format. | P1 | M |
| 2.5 | **Duplicated helpers**: `make_id`/`load_translations`/path constants are copy-pasted across `extract.py`, `inject.py`, `verify.py`, `make_packs.py`. Extract into a shared `tools/lib.py` (single `GAME`/`BACKUP` resolution, id generation, translation loader). Reduces drift risk (2.2/2.3 bugs partly stem from this). | P2 | M |
| 2.6 | **One-off scripts pollute `tools/`**: `pilot_batch09.py` (15KB) is a legacy pilot, not part of the pipeline. Move it to `tools/archive/` or `scripts/` and reference it from the README only if it still has value. | P2 | S |
| 2.7 | **No placeholder/format validation**: the dictionary and injected strings can silently drop `{0}`, `{1}`, `$`, or `<color>` tags. Add a check (in verify) that every original string's `{N}` placeholders and `\n` escapes survive into the translation. | P2 | S |
| 2.8 | **No pipeline orchestration / documentation of "how to re-run"**: the README step list references scripts but there is no single documented end-to-end command sequence for regenerating `mod/`. Add a `tools/README.md` or a `Makefile`/`Justfile` with `extract → make_packs → inject → verify` targets. | P2 | M |

---

## 3. Repository Hygiene

| # | Item | Priority | Effort |
|---|------|----------|--------|
| 3.1 | **`.gitignore` gaps leave build artifacts untracked at repo root**: `FallenAces_Russian_Translation_v1.0.zip`, `.staging/` (downloaded BepInEx/plugin zips), `.venv/`, `__pycache__/`, and `.omo/` are all currently untracked and unignored. Add `*.zip`, `/.staging/`, `.venv/`, `__pycache__/`, `/.omo/` to `.gitignore`. | P0 | S |
| 3.2 | **No LICENSE file**: the README "Лицензия" section is prose only. Pick and commit an actual license. Recommended split: translation text under CC BY-SA 4.0; `tools/` Python and the C# font-builder under MIT; `DejaVuSans-Regular.ttf` under SIL OFL 1.1 (already redistributable — add its license text and note the attribution). Add a `THIRD_PARTY_NOTICES.md` for the OFL font and the XUnity/BepInEx runtime deps. | P1 | S |
| 3.3 | **No CI (GitHub Actions)**: add a workflow that runs on PR: `python -m pytest tests/`, run `verify.py` in a "source-strings only" mode (see 2.2), and a UTF-8/BOM + line-count sweep over `mod/`. This is the single highest-leverage way to keep the fan-mod data correct as contributors edit files. | P1 | M |
| 3.4 | **No release automation**: the "v1.0" zip is a local manual artifact (not even committed). Add a GitHub Actions release workflow that, on tag push, assembles `mod/` + `mod_ui/` into a release zip (consistent with the README's "download the zip" instructions) and attaches it to the release. | P1 | M |
| 3.5 | **`mod_ui/` is entirely untracked** (`git ls-files` shows 0 files under it). Commit it, but first resolve 4.1 (layout) and 3.1 so the committed tree is the intended one. | P0 | S |
| 3.6 | **Pin and checksum third-party runtime archives**: `.staging/` holds BepInEx 5.4.23.5, XUnity.AutoTranslator 5.6.1, XUnity.ResourceRedirector 2.1.0 zips. Record their source URLs + SHA-256 in `mod_ui/THIRD_PARTY_NOTICES.md` (or a `mod_ui/SOURCES.md`) so the distribution is reproducible. | P2 | S |

---

## 4. mod_ui Integration

| # | Item | Priority | Effort |
|---|------|----------|--------|
| 4.1 | **Contradictory directory layout is a packaging bug**: `notes/ui-localization.md` and `unity_font_build/README.md` both say the dictionary lives at `BepInEx/Translation/ru/Text/ui_dictionary.txt`, but `mod_ui/BepInEx/Translation/ru/Text/` is **empty** while the real file sits at `mod_ui/Translation/ru/Text/ui_dictionary.txt`. Decide one canonical location — either copy the dictionary into `mod_ui/BepInEx/Translation/ru/Text/` and make the whole `mod_ui/` tree copy verbatim into the game root, or delete the empty `BepInEx/Translation/...` dir and update the docs. Pick the layout that lets a user copy `mod_ui/` wholesale. | P0 | S |
| 4.2 | **Dictionary contains many likely non-visible entries**: entries like "Player Bought Item", "Player Looking At Item", "Player Cant Pay Toll", "Collected {0}/5" look like internal event/log keys rather than user-facing UI text. XUnity only rewrites text that reaches a UI component, so dead entries are harmless but bloat the dict and mislead translators. Verify in-game which entries actually appear (ALT+T toggle), and curate the dictionary down to real strings — document this "curated" workflow. | P1 | M |
| 4.3 | **Font bundle is referenced but not shipped**: the config has empty `OverrideFontTextMeshPro=` / `FallbackFontTextMeshPro=`, and `unity_font_build` is a source-only builder (`.ttf` + editor script) — the built `fallenaces_cyr_ru` asset bundle is **not committed** and the fallback path is explicitly "unverified on TMP 1.4.0" (`notes/ui-font.md`). Decide whether Cyrillic in UI works without it; if not, build once and commit the bundle with install instructions; if it's unconfirmed, mark the whole font section as "experimental — test first" and remove it from default install. | P1 | M |
| 4.4 | **`mod_ui/` not integrated into README install/rollback** (see 1.2): the main README is the single place users land, and it currently has zero UI-mod coverage. This is the most visible gap. | P0 | M |
| 4.5 | **Dictionary has no automated hygiene checks**: no enforcement of UTF-8 no BOM, no duplicate-`orig` detection, no `{N}`-placeholder preservation (overlaps 2.7). Add a small validator in `tools/` (or CI) run over `ui_dictionary.txt`. | P2 | S |
| 4.6 | **UI terminology not in the glossary**: glossary.md is narrative-only (characters/factions/slang). UI strings use different consistent terms (e.g. "gadget", "Hideout", "chapter"). Either extend the glossary with a UI-terms section or add a `glossary/ui_glossary.md` so UI and narrative translations don't diverge (e.g. "Hideout" → "Притон" everywhere). | P2 | S |

---

## 5. Contributor Experience

| # | Item | Priority | Effort |
|---|------|----------|--------|
| 5.1 | **Add CONTRIBUTING.md** (see 1.4) — the biggest CE gap; the project already frames itself as "help proofread the AI translation", so this is on-message. | P1 | M |
| 5.2 | **Issue templates** (see 1.5) tailored to translation proofreading and tooling. | P2 | S |
| 5.3 | **Establish a clear "source of truth" policy**: the repo does not commit `strings.json`/`subtitle_strings.json` (gitignored) or the game backup — only the built `mod/`. Document explicitly that `mod/` (and `mod_ui/`) are the shipped source of truth and that the pipeline is for regeneration only, so contributors don't try to edit intermediate JSON. Consider committing `*.in.json`/`*.out.json` if re-running the pipeline becomes important. | P2 | M |
| 5.4 | **Code review / style guide for tools**: if CI tests land (3.3), add a minimal `pyproject.toml` with ruff/black config and a short style note so multiple people can touch the pipeline consistently. | P2 | S |

---

## Suggested execution order

1. **P0, S items first** (half a day): 1.1, 3.1, 3.5, 4.1, 2.1 — these are correctness/credibility blockers.
2. **P0 documentation integration** (1.2, 4.4): make README truthful and complete for both mods.
3. **P1 safety** (2.2, 2.3, 3.2, 3.3, 4.2, 4.3, 1.4): verify/test the pipeline, license, and CI.
4. **P2 polish** as capacity allows.

This is a fan project — the P0/P1 set is the realistic target for "polished open-source mod repo"; P2 items are stretch goals.
