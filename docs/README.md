# Docs / GitHub Pages

Partner-facing sources (edit these, don’t commit root `*.html` renders):

| Doc | Path |
|-----|------|
| Overview | `faa_overview.qmd` (+ optional `faa_overview.pdf`) |
| How it works | `faa_how_it_works.qmd` |
| Working brief | `next_gen_faa.md` |
| Design detail | `config/` (see `config/README.md`) |

## Quarto dashboard → Pages

```bash
cd dashboard
quarto render
```

Pages: **Actions** (`index.qmd`), **Context** (`context.qmd`), **Methods** (`methods.qmd`).

Configured to write `docs/dashboard/` (`dashboard/_quarto.yml`). Enable GitHub Pages from `/docs` if you want the site live. That build folder is gitignored until you choose to publish a render.
