#!/usr/bin/env python3
"""Validate deterministic properties of the generated Jekyll site."""

from __future__ import annotations

import gzip
import html
import posixpath
import sys
from collections import Counter
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
SITE_HOST = "yingfeilu.github.io"

GLOBAL_ASSET_BUDGET = 25 * 1024
FIRST_PARTY_JS_BUDGET = 10 * 1024
HOME_TRANSFER_BUDGET = 500 * 1024
GALLERY_INITIAL_TRANSFER_BUDGET = 400 * 1024
GENERATED_SITE_BUDGET = 8 * 1024 * 1024


@dataclass
class Page:
    file: Path
    public_path: str
    html_lang: str | None = None
    body_classes: set[str] = field(default_factory=set)
    description: str | None = None
    ids: list[str] = field(default_factory=list)
    references: list[tuple[str, str, str]] = field(default_factory=list)
    blank_links: list[dict[str, str]] = field(default_factory=list)
    images: list[dict[str, str]] = field(default_factory=list)
    alternates: dict[str, str] = field(default_factory=dict)
    site_brand_href: str | None = None
    navigation_hrefs: list[str] = field(default_factory=list)
    active_locale: str | None = None
    social_image: str | None = None


class Inspector(HTMLParser):
    def __init__(self, page: Page) -> None:
        super().__init__(convert_charrefs=True)
        self.page = page

    def handle_starttag(self, tag: str, raw_attrs: list[tuple[str, str | None]]) -> None:
        attrs = {name.lower(): (value or "") for name, value in raw_attrs}

        if tag == "html":
            self.page.html_lang = attrs.get("lang")
        elif tag == "body":
            self.page.body_classes = set(attrs.get("class", "").split())
        elif tag == "meta" and attrs.get("name", "").lower() == "description":
            self.page.description = attrs.get("content", "").strip()
        elif tag == "meta" and attrs.get("property", "").lower() == "og:image":
            self.page.social_image = attrs.get("content", "").strip()

        if attrs.get("id"):
            self.page.ids.append(attrs["id"])

        for attribute in ("href", "src"):
            if attrs.get(attribute):
                self.page.references.append((tag, attribute, attrs[attribute]))

        if attrs.get("srcset"):
            for candidate in attrs["srcset"].split(","):
                url = candidate.strip().split()[0] if candidate.strip() else ""
                if url:
                    self.page.references.append((tag, "srcset", url))

        if tag == "a" and attrs.get("target", "").lower() == "_blank":
            self.page.blank_links.append(attrs)

        if tag == "a":
            classes = set(attrs.get("class", "").split())
            if "site-brand" in classes:
                self.page.site_brand_href = attrs.get("href")
            if "site-nav__link" in classes and attrs.get("href"):
                self.page.navigation_hrefs.append(attrs["href"])
            if "locale-switcher__link" in classes and attrs.get("aria-current") == "page":
                self.page.active_locale = attrs.get("lang")

        if tag == "img":
            self.page.images.append(attrs)

        if tag == "link" and "alternate" in attrs.get("rel", "").lower().split():
            language = attrs.get("hreflang", "").lower()
            if language and attrs.get("href"):
                self.page.alternates[language] = attrs["href"]


def public_path_for(file: Path) -> str:
    relative = file.relative_to(SITE).as_posix()
    if relative == "index.html":
        return "/"
    return f"/{relative}"


def parse_pages() -> list[Page]:
    pages: list[Page] = []
    for file in sorted(SITE.rglob("*.html")):
        page = Page(file=file, public_path=public_path_for(file))
        Inspector(page).feed(file.read_text(encoding="utf-8"))
        pages.append(page)
    return pages


def candidate_files(path: str) -> list[Path]:
    clean_path = unquote(path or "/")
    if not clean_path.startswith("/"):
        raise ValueError(f"Expected an absolute public path, received {clean_path!r}")

    relative = clean_path.lstrip("/")
    if clean_path.endswith("/") or not relative:
        return [SITE / relative / "index.html"]

    target = SITE / relative
    candidates = [target]
    if not Path(relative).suffix:
        candidates.extend([SITE / f"{relative}.html", target / "index.html"])
    return candidates


def resolve_reference(raw_url: str, source_page: Page) -> tuple[Path | None, str | None]:
    value = html.unescape(raw_url.strip())
    parsed = urlsplit(value)

    if parsed.scheme in {"mailto", "tel", "data", "javascript"}:
        return None, None
    if parsed.scheme and parsed.scheme not in {"http", "https"}:
        return None, None
    if parsed.netloc and parsed.netloc != SITE_HOST:
        return None, None

    path = parsed.path
    if not path:
        path = source_page.public_path
    elif not path.startswith("/"):
        source_directory = posixpath.dirname(source_page.public_path)
        path = posixpath.normpath(posixpath.join(source_directory, path))
        if not path.startswith("/"):
            path = f"/{path}"

    for candidate in candidate_files(path):
        if candidate.exists():
            return candidate, unquote(parsed.fragment) or None
    return candidate_files(path)[0], unquote(parsed.fragment) or None


def gzip_size(file: Path) -> int:
    return len(gzip.compress(file.read_bytes(), compresslevel=9, mtime=0))


def page_by_file(pages: list[Page]) -> dict[Path, Page]:
    return {page.file.resolve(): page for page in pages}


def check_pages(pages: list[Page]) -> list[str]:
    errors: list[str] = []
    pages_by_file = page_by_file(pages)

    for page in pages:
        duplicate_ids = [value for value, count in Counter(page.ids).items() if count > 1]
        if duplicate_ids:
            errors.append(f"{page.public_path}: duplicate IDs: {', '.join(duplicate_ids)}")

        if page.html_lang:
            expected_lang = "zh" if page.public_path.startswith("/zh/") else "en"
            if page.html_lang != expected_lang:
                errors.append(
                    f"{page.public_path}: html lang is {page.html_lang!r}, expected {expected_lang!r}"
                )
            if not page.description:
                errors.append(f"{page.public_path}: missing a generated meta description")
            if page.active_locale != expected_lang:
                errors.append(
                    f"{page.public_path}: active locale is {page.active_locale!r}, "
                    f"expected {expected_lang!r}"
                )

            expected_home = "/zh/" if expected_lang == "zh" else "/"
            if page.site_brand_href != expected_home:
                errors.append(
                    f"{page.public_path}: site brand links to {page.site_brand_href!r}, "
                    f"expected {expected_home!r}"
                )

            for navigation_href in page.navigation_hrefs:
                is_chinese_href = navigation_href.startswith("/zh/")
                if is_chinese_href != (expected_lang == "zh"):
                    errors.append(
                        f"{page.public_path}: navigation target uses the wrong locale: "
                        f"{navigation_href}"
                    )

            if not page.social_image:
                errors.append(f"{page.public_path}: missing generated og:image metadata")
            else:
                social_file, _ = resolve_reference(page.social_image, page)
                if social_file is None or not social_file.exists():
                    errors.append(
                        f"{page.public_path}: og:image target does not exist: {page.social_image}"
                    )

        for attrs in page.blank_links:
            rel_values = set(attrs.get("rel", "").lower().split())
            required = {"noopener", "noreferrer"}
            if not required.issubset(rel_values):
                errors.append(
                    f"{page.public_path}: target=_blank link lacks rel=\"noopener noreferrer\": "
                    f"{attrs.get('href', '')}"
                )

        for attrs in page.images:
            is_dynamic_gallery_image = "data-gallery-image" in attrs
            if not is_dynamic_gallery_image:
                if not attrs.get("alt", "").strip():
                    errors.append(f"{page.public_path}: rendered image has empty alt text")
                for dimension in ("width", "height"):
                    try:
                        if int(attrs.get(dimension, "0")) <= 0:
                            raise ValueError
                    except ValueError:
                        errors.append(
                            f"{page.public_path}: image {attrs.get('src', '')} lacks a valid {dimension}"
                        )

            if page.public_path.endswith(("/gallery.html", "/contact.html")) and not is_dynamic_gallery_image:
                if attrs.get("loading") != "lazy":
                    errors.append(
                        f"{page.public_path}: {attrs.get('src', '')} must use loading=\"lazy\""
                    )
                if attrs.get("decoding") != "async":
                    errors.append(
                        f"{page.public_path}: {attrs.get('src', '')} must use decoding=\"async\""
                    )

            if page.public_path in {"/", "/zh/index.html"} and not is_dynamic_gallery_image:
                if attrs.get("fetchpriority") != "high":
                    errors.append(f"{page.public_path}: home portrait must use fetchpriority=\"high\"")
                if attrs.get("loading") == "lazy":
                    errors.append(f"{page.public_path}: home portrait must not be lazy-loaded")

        for tag, attribute, raw_url in page.references:
            target, fragment = resolve_reference(raw_url, page)
            if target is None:
                continue
            if not target.exists():
                errors.append(
                    f"{page.public_path}: missing local {attribute} target {raw_url!r} on <{tag}>"
                )
                continue
            if fragment and target.suffix == ".html":
                target_page = pages_by_file.get(target.resolve())
                if target_page and fragment not in target_page.ids:
                    errors.append(
                        f"{page.public_path}: missing fragment #{fragment} in "
                        f"{public_path_for(target)}"
                    )

        if page.alternates:
            expected_languages = {"en", "zh", "x-default"}
            if set(page.alternates) != expected_languages:
                errors.append(
                    f"{page.public_path}: language alternates are "
                    f"{sorted(page.alternates)}, expected {sorted(expected_languages)}"
                )
            for language, raw_url in page.alternates.items():
                target, _ = resolve_reference(raw_url, page)
                if target is None or not target.exists():
                    errors.append(
                        f"{page.public_path}: {language} alternate does not exist: {raw_url}"
                    )

            counterpart_language = "en" if page.html_lang == "zh" else "zh"
            counterpart_url = page.alternates.get(counterpart_language)
            if counterpart_url:
                counterpart_file, _ = resolve_reference(counterpart_url, page)
                counterpart = (
                    pages_by_file.get(counterpart_file.resolve()) if counterpart_file else None
                )
                own_language = "zh" if page.html_lang == "zh" else "en"
                if not counterpart or own_language not in counterpart.alternates:
                    errors.append(
                        f"{page.public_path}: counterpart does not declare a reciprocal alternate"
                    )
                else:
                    reciprocal_file, _ = resolve_reference(
                        counterpart.alternates[own_language], counterpart
                    )
                    if not reciprocal_file or reciprocal_file.resolve() != page.file.resolve():
                        errors.append(
                            f"{page.public_path}: counterpart alternate is not reciprocal"
                        )

    return errors


def check_budgets(pages: list[Page]) -> tuple[list[str], dict[str, int]]:
    errors: list[str] = []
    css_files = sorted((SITE / "assets" / "css").glob("*.css"))
    js_files = sorted((SITE / "assets" / "js").glob("*.js"))
    published_css_js = sorted(SITE.rglob("*.css")) + sorted(SITE.rglob("*.js"))

    global_assets = sum(gzip_size(file) for file in published_css_js)
    first_party_js = sum(gzip_size(file) for file in js_files)
    generated_site = sum(file.stat().st_size for file in SITE.rglob("*") if file.is_file())

    if global_assets >= GLOBAL_ASSET_BUDGET:
        errors.append(
            f"Global local CSS + JavaScript is {global_assets:,} bytes gzip "
            f"(budget: < {GLOBAL_ASSET_BUDGET:,})"
        )
    if first_party_js >= FIRST_PARTY_JS_BUDGET:
        errors.append(
            f"First-party JavaScript is {first_party_js:,} bytes gzip "
            f"(budget: < {FIRST_PARTY_JS_BUDGET:,})"
        )
    if generated_site >= GENERATED_SITE_BUDGET:
        errors.append(
            f"Generated site is {generated_site:,} bytes "
            f"(budget: < {GENERATED_SITE_BUDGET:,})"
        )

    shared_transfer = sum(gzip_size(file) for file in css_files + js_files)
    pages_by_path = {page.public_path: page for page in pages}

    home = pages_by_path.get("/")
    home_transfer = shared_transfer + (gzip_size(home.file) if home else 0)
    if home and home.images:
        image_file, _ = resolve_reference(home.images[0].get("src", ""), home)
        if image_file and image_file.exists():
            home_transfer += image_file.stat().st_size
    if home_transfer >= HOME_TRANSFER_BUDGET:
        errors.append(
            f"Home local transfer estimate is {home_transfer:,} bytes "
            f"(budget: < {HOME_TRANSFER_BUDGET:,})"
        )

    gallery = pages_by_path.get("/gallery.html")
    gallery_transfer = shared_transfer + (gzip_size(gallery.file) if gallery else 0)
    if gallery:
        for attrs in gallery.images:
            if attrs.get("src") and attrs.get("loading") != "lazy":
                image_file, _ = resolve_reference(attrs["src"], gallery)
                if image_file and image_file.exists():
                    gallery_transfer += image_file.stat().st_size
    if gallery_transfer >= GALLERY_INITIAL_TRANSFER_BUDGET:
        errors.append(
            f"Gallery initial local transfer estimate is {gallery_transfer:,} bytes "
            f"(budget: < {GALLERY_INITIAL_TRANSFER_BUDGET:,})"
        )

    metrics = {
        "global_assets_gzip": global_assets,
        "first_party_js_gzip": first_party_js,
        "home_transfer": home_transfer,
        "gallery_initial_transfer": gallery_transfer,
        "generated_site": generated_site,
    }
    return errors, metrics


def main() -> int:
    if not SITE.is_dir():
        print("Generated site not found. Run bundle exec jekyll build first.", file=sys.stderr)
        return 1

    pages = parse_pages()
    errors = check_pages(pages)
    budget_errors, metrics = check_budgets(pages)
    errors.extend(budget_errors)

    if any("fontawesome" in file.as_posix().lower() for file in SITE.rglob("*")):
        errors.append("The generated site still contains a Font Awesome runtime asset")

    if errors:
        print("Site validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "Site validation passed: "
        f"{len(pages)} HTML pages; "
        f"global CSS+JS {metrics['global_assets_gzip']:,} B gzip; "
        f"first-party JS {metrics['first_party_js_gzip']:,} B gzip; "
        f"home {metrics['home_transfer']:,} B; "
        f"gallery initial {metrics['gallery_initial_transfer']:,} B; "
        f"site {metrics['generated_site']:,} B."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
