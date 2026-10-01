"""Generate test PDFs for test-site-2, one or more PER DIRECTORY, each with UNIQUE content.

Every PDF embeds a fresh UUID in its metadata, so its SHA-256 is new to the crawler's document
registry on each run. A crawl therefore uploads every PDF and runs it through the remediation
(Adobe) pipeline instead of skipping it as already-known.

Each PDF lives in the same directory as the HTML page that links to it (relative links like
`service-catalog.pdf`, not `../docs/service-catalog.pdf`).

Run from this directory:  py -3.11 _generate_pdfs.py
Safe to re-run; overwrites the PDFs and mints new UUIDs (= new hashes again).
"""

import uuid
from pathlib import Path

from pypdf import PdfWriter

# Relative path (from site root) -> list of PDF filenames to create in that directory.
LAYOUT: dict[str, list[str]] = {
    ".": ["annual-summary.pdf"],
    "services": ["service-catalog.pdf", "rate-card.pdf"],
    "services/consulting": ["consulting-brochure.pdf", "engagement-model.pdf"],
    "services/consulting/methodology": ["methodology-whitepaper.pdf"],
    "insights": ["market-outlook.pdf"],
    "insights/reports": ["q1-report.pdf", "q2-report.pdf"],
    "insights/newsletters": ["newsletter-spring.pdf"],
    "support": ["faq-guide.pdf"],
}


def main() -> None:
    root = Path(__file__).parent
    count = 0
    for rel_dir, names in LAYOUT.items():
        target_dir = root if rel_dir == "." else root / rel_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        for name in names:
            unique = uuid.uuid4().hex
            writer = PdfWriter()
            writer.add_blank_page(width=612, height=792)
            writer.add_metadata(
                {
                    "/Title": name.replace("-", " ").replace(".pdf", "").title(),
                    "/Author": "Depth Test Site 2",
                    "/Subject": f"unique-content-marker:{unique}",
                }
            )
            out = target_dir / name
            with open(out, "wb") as handle:
                writer.write(handle)
            print(f"created {out.relative_to(root).as_posix()}  (marker {unique})")
            count += 1
    print(f"\n{count} PDFs across {len(LAYOUT)} directories")


if __name__ == "__main__":
    main()
