"""
Milestone 3 — Document Ingestion
Scrapes all 20 sources, cleans HTML, saves plain text to data/raw/.
Run: python ingest.py
"""

import os
import time
import json
import requests
import pdfplumber
from bs4 import BeautifulSoup

OUTPUT_DIR = "data/raw"
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# All 20 sources: name, url, source_site, date, type
SOURCES = [
    # RamblerTempe — detailed student reviews
    {
        "name": "apollo_tempe",
        "apartment": "Apollo Tempe",
        "source": "RamblerTempe",
        "url": "https://ramblertempe.com/resources/apartment-review-apollo-tempe/",
        "date": "2026",
        "type": "web",
    },
    {
        "name": "university_house_tempe",
        "apartment": "University House Tempe",
        "source": "RamblerTempe",
        "url": "https://ramblertempe.com/resources/apartment-review-university-house-tempe/",
        "date": "2026",
        "type": "web",
    },
    {
        "name": "union_tempe",
        "apartment": "Union Tempe",
        "source": "RamblerTempe",
        "url": "https://ramblertempe.com/resources/apartment-review-union-tempe/",
        "date": "2026",
        "type": "web",
    },
    {
        "name": "oliv_tempe",
        "apartment": "oLiv Tempe",
        "source": "RamblerTempe",
        "url": "https://ramblertempe.com/resources/arizona-state-apartment-review-oliv-tempe/",
        "date": "2026",
        "type": "web",
    },
    {
        "name": "canvas_tempe",
        "apartment": "Canvas Tempe",
        "source": "RamblerTempe",
        "url": "https://ramblertempe.com/resources/tempe-student-apartment-review-canvas-tempe/",
        "date": "2026",
        "type": "web",
    },
    {
        "name": "district_on_apache",
        "apartment": "The District on Apache",
        "source": "RamblerTempe",
        "url": "https://ramblertempe.com/resources/asu-apartment-review-district-on-apache/",
        "date": "2026",
        "type": "web",
    },
    {
        "name": "verve_tempe",
        "apartment": "Verve Tempe",
        "source": "RamblerTempe",
        "url": "https://ramblertempe.com/resources/tempe-student-apartment-review-verve-tempe/",
        "date": "2026",
        "type": "web",
    },
    {
        "name": "marshall_tempe",
        "apartment": "Marshall Tempe",
        "source": "RamblerTempe",
        "url": "https://ramblertempe.com/resources/tempe-student-apartment-review-marshall-tempe/",
        "date": "2026",
        "type": "web",
    },
    {
        "name": "nine20_tempe",
        "apartment": "Nine20 Tempe",
        "source": "RamblerTempe",
        "url": "https://ramblertempe.com/resources/arizona-state-apartment-review-nine20-tempe/",
        "date": "2026",
        "type": "web",
    },
    {
        "name": "best_apartments_asu",
        "apartment": "Various ASU Apartments",
        "source": "RamblerTempe",
        "url": "https://ramblertempe.com/resources/best-student-apartments-asu-tempe/",
        "date": "2026",
        "type": "web",
    },
    # ApartmentRatings — raw tenant reviews
    {
        "name": "vertex_student_apartments",
        "apartment": "Vertex Student Apartments",
        "source": "ApartmentRatings",
        "url": "https://www.apartmentratings.com/az/tempe/vertex-student-apartments_9199332346275160627/",
        "date": "2024",
        "type": "web",
    },
    {
        "name": "district_on_apache_ratings",
        "apartment": "The District on Apache",
        "source": "ApartmentRatings",
        "url": "https://www.apartmentratings.com/az/tempe/the-district-on-apache_9199332346275170990/",
        "date": "2024",
        "type": "web",
    },
    {
        "name": "gateway_at_tempe",
        "apartment": "Gateway at Tempe",
        "source": "ApartmentRatings",
        "url": "https://www.apartmentratings.com/az/tempe/gateway-at-tempe_9199332346275143488/",
        "date": "2024",
        "type": "web",
    },
    {
        "name": "sol_tempe",
        "apartment": "SoL Tempe",
        "source": "ApartmentRatings",
        "url": "https://www.apartmentratings.com/az/tempe/sol_480894194985281/",
        "date": "2024",
        "type": "web",
    },
    {
        "name": "paseo_on_university",
        "apartment": "Paseo on University",
        "source": "ApartmentRatings",
        "url": "https://www.apartmentratings.com/az/tempe/paseo-on-university_4809688118852818420/",
        "date": "2024",
        "type": "web",
    },
    # Official / guide sources
    {
        "name": "asu_offcampus_portal",
        "apartment": "Various ASU Apartments",
        "source": "ASU Off-Campus Housing Portal",
        "url": "https://offcampushousing.asu.edu/",
        "date": "2026",
        "type": "web",
    },
    {
        "name": "thunderbird_housing_guide",
        "apartment": "Various ASU Apartments",
        "source": "ASU Thunderbird Housing Guide",
        "url": "https://thunderbird.asu.edu/sites/default/files/2022-04/ThunderbirdOffCampusHousingGuide20222023.pdf",
        "date": "2023",
        "type": "pdf",
    },
    {
        "name": "amber_student_tempe",
        "apartment": "Various ASU Apartments",
        "source": "Amber Student",
        "url": "https://amberstudent.com/places/search/tempe-1811051325535",
        "date": "2026",
        "type": "web",
    },
    {
        "name": "statepress_housing_prices",
        "apartment": "Tempe Housing Market",
        "source": "ASU State Press",
        "url": "https://www.statepress.com/article/2026/04/college-town-housing-prices",
        "date": "2026",
        "type": "web",
    },
    # University Village — extra source to reach 20
    {
        "name": "university_village_apartments",
        "apartment": "University Village Apartments",
        "source": "ApartmentRatings",
        "url": "https://www.apartmentratings.com/az/tempe/university-village-apartments_480967666585281/",
        "date": "2024",
        "type": "web",
    },
]


def clean_html(soup: BeautifulSoup) -> str:
    # Remove nav, header, footer, ads, scripts, styles
    for tag in soup(["nav", "header", "footer", "script", "style",
                     "aside", "form", "button", "iframe", "noscript"]):
        tag.decompose()

    # Extract main content area if present
    main = soup.find("main") or soup.find("article") or soup.find(id="content")
    target = main if main else soup.body if soup.body else soup

    text = target.get_text(separator="\n")

    # Collapse excessive whitespace
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    return "\n".join(lines)


def scrape_web(source: dict) -> str:
    try:
        resp = requests.get(source["url"], headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        return clean_html(soup)
    except Exception as e:
        print(f"  [WARN] Failed to scrape {source['url']}: {e}")
        return ""


def extract_pdf(source: dict) -> str:
    # Download PDF then extract text
    try:
        resp = requests.get(source["url"], headers=HEADERS, timeout=30)
        resp.raise_for_status()
        pdf_path = os.path.join(OUTPUT_DIR, f"{source['name']}.pdf")
        with open(pdf_path, "wb") as f:
            f.write(resp.content)

        text_parts = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)

        os.remove(pdf_path)
        return "\n".join(text_parts)
    except Exception as e:
        print(f"  [WARN] Failed to extract PDF {source['url']}: {e}")
        return ""


def save_source(source: dict, text: str):
    if not text.strip():
        print(f"  [SKIP] Empty content for {source['name']}")
        return False

    out_path = os.path.join(OUTPUT_DIR, f"{source['name']}.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)

    # Save metadata alongside
    meta_path = os.path.join(OUTPUT_DIR, f"{source['name']}.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in source.items() if k != "type"}, f, indent=2)

    print(f"  [OK] {source['name']} — {len(text):,} chars")
    return True


def main():
    print(f"Ingesting {len(SOURCES)} sources into {OUTPUT_DIR}/\n")
    success, failed = 0, 0

    for source in SOURCES:
        print(f"Fetching: {source['name']} ({source['source']})")

        if source["type"] == "pdf":
            text = extract_pdf(source)
        else:
            text = scrape_web(source)

        if save_source(source, text):
            success += 1
        else:
            failed += 1

        time.sleep(1.5)  # polite delay between requests

    print(f"\nDone: {success} saved, {failed} failed/skipped")
    print(f"Raw documents in: {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
