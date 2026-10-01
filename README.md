# Crawler Depth Test Site — Set 2 (fresh hashes, PDFs per directory)

Same purpose and depth structure as the original `test-site/`, but with two differences:

1. **Unique PDF content** — each PDF embeds a per-file, per-run UUID, so its SHA-256 is new to
   the crawler's document registry. A crawl of this site actually **uploads** every PDF and runs
   it through the remediation (Adobe) pipeline, instead of skipping them as already-known.
2. **PDFs live in each directory** — every PDF sits in the same folder as the HTML page that
   links it, rather than in one central `docs/` folder. Links are same-directory relative paths.

## Serving / deploying

Local check:

```powershell
py -3.11 -m http.server 8000
```

GitHub project Pages: copy this folder's contents (except `_generate_pdfs.py`) to the repo root,
add an empty `.nojekyll`, commit, push. All links are relative, so they resolve under `/{repo}/`.

Regenerate PDFs with brand-new hashes (safe anytime):

```powershell
py -3.11 _generate_pdfs.py
```

## Layout / depth map

`depth` = number of link hops from `index.html` (depth 0). Each PDF is in the directory shown.

| Depth | Page | PDFs in that directory |
|-------|------|------------------------|
| 0 | `index.html` | `annual-summary.pdf` |
| 1 | `services.html` | `services/service-catalog.pdf`, `services/rate-card.pdf` |
| 1 | `insights.html` | `insights/market-outlook.pdf` |
| 1 | `support.html` | `support/faq-guide.pdf` |
| 2 | `services/consulting.html` | `services/consulting/consulting-brochure.pdf`, `services/consulting/engagement-model.pdf` |
| 2 | `insights/reports.html` | `insights/reports/q1-report.pdf`, `insights/reports/q2-report.pdf` |
| 2 | `insights/newsletters.html` | `insights/newsletters/newsletter-spring.pdf` |
| 3 | `services/consulting/methodology.html` | `services/consulting/methodology/methodology-whitepaper.pdf` |

`index.html` also links to `https://www.example.org` (off-domain), which the crawler must ignore.

## Expected results per max_depth

Rule: a page at depth D is crawled; its links are followed only if `D < max_depth`
(or `max_depth == 0` = unlimited). PDFs on any crawled page are always collected.

| max_depth | Pages crawled | PDFs collected |
|-----------|---------------|----------------|
| 0 (unlimited) | all 8 | all 11 |
| 1 | index + 3 depth-1 (4 total) | annual-summary, service-catalog, rate-card, market-outlook, faq-guide (5 PDFs) |
| 2 | index + 3 depth-1 + 3 depth-2 (7 total) | the 5 above + consulting-brochure, engagement-model, q1-report, q2-report, newsletter-spring (10 PDFs) |
| 3 | all 8 | all 11 |

`max_depth=1 -> exactly 5 PDFs` is the cleanest signal that depth gating works.

Total: 8 HTML pages, 11 PDFs.
