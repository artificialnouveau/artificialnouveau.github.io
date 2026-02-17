"""
Scrape executive profile pictures from Shell, Heineken, Philips, and ING.
Each company's photos are saved to a separate folder.
After scraping, generates photo-data.js with base64-embedded images
so the web page works without hosting image files.

Requirements:
    pip install requests beautifulsoup4 selenium webdriver-manager
"""

import os
import re
import time
import json
import base64
import mimetypes
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

OUTPUT_DIR = "profile_photos"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

# Collect all downloaded images for base64 embedding
all_photos = {}  # { company: [{ name, data_url }] }


def setup_driver():
    """Create a headless Chrome driver."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"user-agent={HEADERS['User-Agent']}")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def download_image(url):
    """Download image bytes, return (bytes, content_type) or None."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        ct = resp.headers.get("content-type", "image/jpeg").split(";")[0].strip()
        return resp.content, ct
    except Exception as e:
        print(f"  Failed to download {url}: {e}")
        return None


def save_image(url, folder, filename, company):
    """Download, save to disk, and store base64 for embedding."""
    os.makedirs(folder, exist_ok=True)
    filename = re.sub(r'[^\w\-.]', '_', filename)
    filepath = os.path.join(folder, filename)

    result = download_image(url)
    if not result:
        return False

    img_bytes, content_type = result
    with open(filepath, "wb") as f:
        f.write(img_bytes)

    # Store base64 for web embedding
    b64 = base64.b64encode(img_bytes).decode("ascii")
    data_url = f"data:{content_type};base64,{b64}"
    if company not in all_photos:
        all_photos[company] = []
    name_label = os.path.splitext(filename)[0].replace("_", " ").replace("-", " ").title()
    all_photos[company].append({"name": name_label, "dataUrl": data_url})

    print(f"  Saved: {filename}")
    return True


def slugify(name):
    """Turn a person's name into a safe filename."""
    return re.sub(r'[^\w]+', '-', name.strip().lower()).strip('-')


# ──────────────────────────────────────────────
# PHILIPS  (static HTML — requests + BS4)
# ──────────────────────────────────────────────
def scrape_philips():
    print("\n=== Philips ===")
    folder = os.path.join(OUTPUT_DIR, "philips")
    base = "https://www.philips.com"
    url = f"{base}/a-w/about/executive-committee.html"

    resp = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")

    images = soup.find_all("img", src=re.compile(r"executive-commitee", re.I))
    if not images:
        images = soup.find_all("img", src=re.compile(r"c-dam/corporate.*about", re.I))

    count = 0
    for img in images:
        src = img.get("src") or img.get("data-src") or ""
        if not src:
            continue
        img_url = urljoin(base, src)
        name = img.get("alt", "").strip()
        if not name:
            name = os.path.splitext(os.path.basename(src))[0]
        ext = os.path.splitext(src)[-1] or ".jpg"
        filename = f"{slugify(name)}{ext}"
        if save_image(img_url, folder, filename, "philips"):
            count += 1

    print(f"  Philips total: {count} images")


# ──────────────────────────────────────────────
# ING  (static HTML — requests + BS4)
# ──────────────────────────────────────────────
def scrape_ing():
    print("\n=== ING ===")
    folder = os.path.join(OUTPUT_DIR, "ing")
    base = "https://www.ing.com"
    url = f"{base}/about-us/management-structure/executive-board-and-management-board-banking"

    resp = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")

    images = soup.find_all("img", src=re.compile(r"/mgmt/", re.I))
    if not images:
        images = soup.find_all("img", src=re.compile(r"binaries.*gallery", re.I))

    count = 0
    for img in images:
        src = img.get("src") or img.get("data-src") or ""
        if not src:
            continue
        img_url = urljoin(base, src)
        name = img.get("alt", "").strip()
        if not name:
            name = os.path.splitext(os.path.basename(src))[0]
        ext = os.path.splitext(src)[-1] or ".png"
        filename = f"{slugify(name)}{ext}"
        if save_image(img_url, folder, filename, "ing"):
            count += 1

    print(f"  ING total: {count} images")


# ──────────────────────────────────────────────
# SHELL  (JS-rendered — needs Selenium)
# ──────────────────────────────────────────────
def scrape_shell(driver):
    print("\n=== Shell ===")
    folder = os.path.join(OUTPUT_DIR, "shell")
    base = "https://www.shell.com"
    url = f"{base}/who-we-are/leadership/executive-committee.html"

    driver.get(url)

    # Accept cookies if prompt appears
    try:
        accept_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        )
        accept_btn.click()
        time.sleep(1)
    except Exception:
        pass

    # Wait for profile images to load
    time.sleep(5)

    # Scroll down to trigger lazy-loaded images
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Exclude known non-portrait images from Shell
    shell_exclude_keywords = ["headquarters", "plant", "annual", "cover",
                              "woman-at-work", "employee", "background", "header",
                              "footer", "banner", "building", "office", "report"]

    candidates = []
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src") or img.get("data-lazy") or ""
        alt = (img.get("alt") or "").strip()
        if not src or src.endswith(".svg") or "1x1" in src or "logo" in src.lower():
            continue
        # Skip non-portrait images
        src_lower = src.lower()
        alt_lower = alt.lower()
        if any(kw in src_lower or kw in alt_lower for kw in shell_exclude_keywords):
            continue
        if any(kw in src_lower for kw in ["leadership", "executive", "portrait",
                                           "headshot", "profile", "team", "people",
                                           "committee"]):
            candidates.append((src, alt))
        elif alt and len(alt) > 3 and not any(skip in alt_lower for skip in
                                                ["logo", "icon", "banner", "arrow"]):
            candidates.append((src, alt))

    count = 0
    seen = set()
    for src, alt in candidates:
        img_url = urljoin(base, src)
        if img_url in seen:
            continue
        seen.add(img_url)
        name = alt if alt else os.path.splitext(os.path.basename(src))[0]
        ext = os.path.splitext(src.split("?")[0])[-1] or ".jpg"
        filename = f"{slugify(name)}{ext}"
        if save_image(img_url, folder, filename, "shell"):
            count += 1

    print(f"  Shell total: {count} images")


# ──────────────────────────────────────────────
# HEINEKEN  (JS-rendered + age gate — Selenium)
# ──────────────────────────────────────────────
def scrape_heineken(driver):
    print("\n=== Heineken ===")
    folder = os.path.join(OUTPUT_DIR, "heineken")
    base = "https://www.theheinekencompany.com"
    url = f"{base}/our-company/our-leadership"

    driver.get(url)
    time.sleep(5)

    # Handle Heineken age gate: fill DOB + select Netherlands + submit
    try:
        print("  Filling age gate form...")
        driver.execute_script("""
            function setInput(id, val) {
                var el = document.getElementById(id);
                if (el) {
                    var nativeSetter = Object.getOwnPropertyDescriptor(
                        window.HTMLInputElement.prototype, 'value').set;
                    nativeSetter.call(el, val);
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }
            setInput('edit-dob-day', '15');
            setInput('edit-dob-month', '6');
            setInput('edit-dob-year', '1990');
        """)
        time.sleep(1)

        from selenium.webdriver.support.ui import Select
        country_el = driver.find_element(By.ID, "edit-country")
        Select(country_el).select_by_value("NL")
        time.sleep(1)

        driver.find_element(By.ID, "edit-submit-button").click()
        print("  Submitted age gate form")
        time.sleep(8)

    except Exception as e:
        print(f"  Age gate handling failed: {e}")

    # Scroll to load lazy images
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Heineken leadership portraits use 480x570 style images
    candidates = []
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src") or img.get("data-lazy-src") or ""
        alt = (img.get("alt") or "").strip()
        if not src or src.endswith(".svg") or "logo" in src.lower():
            continue
        # Skip banners, annual reports, and non-portrait images
        if any(kw in src.lower() for kw in ["banner", "annual-report", "cover"]):
            continue
        # Target the 480x570 portrait-style images
        if "480x570" in src:
            candidates.append((src, alt))
        elif "our-leadership" in src.lower() and not "banner" in src.lower():
            candidates.append((src, alt))

    count = 0
    seen = set()
    for src, alt in candidates:
        img_url = urljoin(base, src)
        if img_url in seen:
            continue
        seen.add(img_url)
        name = alt if alt else os.path.splitext(os.path.basename(src))[0]
        ext = os.path.splitext(src.split("?")[0])[-1] or ".jpg"
        filename = f"{slugify(name)}{ext}"
        if save_image(img_url, folder, filename, "heineken"):
            count += 1

    print(f"  Heineken total: {count} images")


# ──────────────────────────────────────────────
# Generate photo-data.js with base64 images
# ──────────────────────────────────────────────
def generate_photo_data_js():
    """Write all scraped photos as base64 data URLs into a JS file."""
    output_path = "photo-data.js"
    print(f"\nGenerating {output_path}...")

    # Build the JS content
    lines = ["// Auto-generated by scrape_profiles.py — base64-embedded profile photos"]
    lines.append("// Do not edit manually. Re-run the scraper to regenerate.")
    lines.append(f"const PHOTO_DATA = {json.dumps(all_photos, indent=2)};")

    with open(output_path, "w") as f:
        f.write("\n".join(lines) + "\n")

    total = sum(len(v) for v in all_photos.values())
    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"  Written {output_path}: {total} photos, {size_mb:.1f} MB")


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Scrape static sites first (no browser needed)
    scrape_philips()
    scrape_ing()

    # Scrape JS-rendered sites with Selenium
    print("\nStarting browser for JS-rendered sites...")
    driver = setup_driver()
    try:
        scrape_shell(driver)
        scrape_heineken(driver)
    finally:
        driver.quit()

    # Generate base64-embedded JS file for the web page
    generate_photo_data_js()

    print(f"\nDone! Photos saved to: {os.path.abspath(OUTPUT_DIR)}/")
    for company in ["philips", "ing", "shell", "heineken"]:
        folder = os.path.join(OUTPUT_DIR, company)
        if os.path.isdir(folder):
            files = os.listdir(folder)
            print(f"  {company}: {len(files)} photos")

    print(f"\nWeb page data: photo-data.js")
    print("Open index.html in a browser to use the face averager.")


if __name__ == "__main__":
    main()
