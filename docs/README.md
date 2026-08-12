# Docs / GitHub Pages

Partner-facing sources (edit these, don’t commit root `*.html` renders):

| Doc | Path |
|-----|------|
| Overview | `faa_overview.qmd` (+ optional `faa_overview.pdf`) |
| How it works | `faa_how_it_works.qmd` |
| Working brief | `next_gen_faa.md` |
| Design detail | `config/` (see `config/README.md`) |

## Quarto dashboard → Pages

**One-shot full site (recommended):**

- **RStudio:** open `northwoods_faa.Rproj` → **Build** pane → **Build All** / hammer icon (`Ctrl+Shift+B`). Runs the root `Makefile` → `quarto render` in `dashboard/`. (Optional: open `dashboard/dashboard.Rproj` instead to get Quarto’s native **Render Website** in Build.)
- **Cursor:** **Terminal → Run Build Task** (`Ctrl+Shift+B` / `Cmd+Shift+B`).

Or in a terminal:

```bash
cd dashboard
quarto render
```

**Why the per-file Render button feels incomplete:** `_quarto.yml` lives in `dashboard/`. Rendering only `index.qmd` builds that one page; Context/Methods stay stale or missing until you build the whole site.

Pages: **Actions** (`index.qmd`), **Context** (`context.qmd`), **Methods** (`methods.qmd`).

Configured to write `docs/dashboard/` (`dashboard/_quarto.yml`). For GitHub Pages: **Settings → Pages → Deploy from a branch → `main` / `/docs`**. Site root redirects to the dashboard; direct URL ends in `/dashboard/`. Re-render and commit `docs/dashboard/` when maps change.
