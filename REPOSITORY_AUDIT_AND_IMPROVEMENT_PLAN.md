---
published: false
---

# Repository audit and improvement plan

Audit date: 2026-07-30

## Goal and constraints

Improve performance, reliability, accessibility, SEO, and maintainability without changing the site's visible identity. The current typography, colors, spacing, responsive layouts, dark mode, gallery crops, and content should remain visually stable unless a separate design change is explicitly approved.

The preferred changes are static, measurable, and easy to reverse. This plan deliberately avoids adding a JavaScript framework, a complex asset pipeline, critical-CSS generation, or a service worker.

## Audit scope and validation boundary

The audit covered:

- Jekyll configuration, Ruby dependencies, and the build path
- All layouts, includes, data files, Markdown pages, posts, CSS, and first-party JavaScript
- English and Chinese page structure and translation routing
- Generated HTML, local links, IDs, image attributes, and external-link attributes
- Repository, generated-site, image, CSS, and JavaScript sizes
- Accessibility, SEO, security hygiene, and maintainability signals
- Git history for likely starter-theme files

Validation completed:

- `bundle check`
- `bundle exec jekyll build --trace`
- `git diff --check`
- Generated-output checks across 50 HTML pages
- Local-link existence checks
- Duplicate-ID, image-alt, lazy-loading, and `target="_blank"` checks
- Raw and gzip size measurements for local CSS and JavaScript

The build succeeds in about 0.29 seconds on the audit machine. A live browser/Lighthouse pass was not completed because no browser surface was available in the environment. External URLs and dependency vulnerabilities were not checked live; `bundle-audit` is not installed. Those checks are included in the implementation plan rather than being presented as completed.

## Implementation status — 2026-07-30

The repository now implements the audit’s safe, deterministic recommendations:

- Added `script/validate` and generated-output checks for internal links and fragments, duplicate IDs, image contracts, external-link safety attributes, language metadata, and the acceptance-criteria size budgets
- Added GitHub Actions validation for pushes and pull requests
- Replaced the 1.53 MB Font Awesome runtime with six shared inline SVG brand icons and retained the existing circular footer controls
- Re-encoded the ten active photographs, added committed responsive candidates, preserved original public image URLs, kept the home portrait eager/high-priority, and made contact/gallery images lazy with asynchronous decoding
- Added a deliberately cropped 1200 × 630 social-preview image
- Removed confirmed starter-theme pages, data, layouts, libraries, images, PDFs, malformed duplicate files, and unrelated documentation imagery; retained the favicon master under the publication-excluded `source-assets/` directory
- Replaced path-derived language switching with explicit reciprocal `translation_url` values for every English/Chinese pair
- Added valid `en`, `zh`, and `x-default` alternates only for paired pages
- Localized shared Chinese assistive labels and added mobile-menu background inertness, focus containment, Escape handling, and focus restoration
- Added the missing `rel="noopener noreferrer"` values
- Added language-specific core-page descriptions, a static sitemap, and a bilingual 404 page
- Consolidated the low-risk contact, publications, conferences, and post layout/include pairs around `_data/i18n.yml`
- Replaced theme-gem scaffolding with direct dependencies, committed the multi-platform lockfile, added the explicit `logger` dependency, and documented the operating workflow in `README.md` and `AGENTS.md`

After implementation, the deterministic validation reports 44 HTML pages, 6,682 bytes of global local CSS/JavaScript gzip, 1,104 bytes of first-party JavaScript gzip, a 102,749-byte home transfer estimate, a 13,131-byte gallery initial transfer estimate, and a 5,001,746-byte generated site.

The following items remain deliberately unresolved because they need information or capabilities outside the repository:

- Browser screenshots, Lighthouse, rendered contrast measurements, and real-device interaction checks; no browser surface was available in the implementation environment
- A live external-URL and dependency-vulnerability audit
- Whether the placeholder contact email should become a functional address or non-clickable anti-spam text
- Migration of the public `denfense` URL, which should wait until a real permanent redirect can be guaranteed
- Confirmation of the GitHub Pages source setting in repository settings; CI validates the expected `main`-branch build but does not change deployment settings

## Executive summary

The site has a good performance foundation: static Jekyll output, small first-party CSS and JavaScript, no analytics or framework runtime, explicit image dimensions, deferred scripts, native gallery controls, responsive styling, dark mode, and reduced-motion support.

The main performance problem is highly concentrated. Every page loads the complete Font Awesome brands runtime—1.53 MB raw and about 548 KB compressed—to render six footer icons. Replacing it with a small local SVG sprite or six inline SVG symbols should preserve the footer exactly while removing nearly all of that transfer, parsing, and execution cost.

The next largest user-facing gains are to lazy-load below-the-fold gallery/contact images and optimize the ten actively rendered photographs. The next largest repository/deployment gain is removing or excluding starter-theme material: 30.85 MB of unreferenced images, a 7.09 MB unrelated publication PDF, unused Bootstrap files, sample course PDFs/pages, and other dead source.

CSS splitting, page-specific first-party JavaScript bundles, a service worker, or a framework migration are not justified. The site's own stylesheet is only 27.6 KB raw/5.6 KB compressed, and `main.js` is only 3.0 KB raw/842 bytes compressed.

## Measured baseline

| Metric | Current result | Interpretation |
| --- | ---: | --- |
| Tracked repository files | 143 | Small codebase |
| Tracked file size | 44,396,621 bytes | Dominated by legacy images/PDFs |
| Generated `_site` files | 106 | Includes assets and 50 HTML pages |
| Generated `_site` size | 44,753,342 bytes | Roughly the same dead weight is deployed |
| Generated HTML pages | 50 | English, Chinese, posts, and legacy pages |
| Generated CSS | 27,605 bytes raw / 5,603 bytes gzip | Already lean |
| First-party `main.js` | 2,970 bytes raw / 842 bytes gzip | Already lean |
| Font Awesome runtime | 1,530,755 bytes raw / 548,405 bytes gzip | Largest global payload and JS cost |
| Global local CSS + JS | 1,561,330 bytes raw / 554,850 bytes gzip | Almost entirely Font Awesome |
| Home portrait | 760,098 bytes | Large for its maximum rendered dimensions |
| Eight gallery images | 1,755,503 bytes | All currently load eagerly |
| Unreferenced images | 30,854,837 bytes | Repository/deploy weight, not current page transfer |
| Estimated home transfer | 1,319,624 bytes | Gzipped local text + image; excludes web fonts/favicons |
| Estimated gallery transfer | 2,314,527 bytes | Gzipped local text + all eager images; excludes web fonts/favicons |

The transfer estimates are static calculations, not Lighthouse results. They assume HTTP compression for text assets and do not include Google Fonts.

## What should be preserved

- Static Jekyll architecture and server-free runtime
- Current light/dark palette and typography
- Current responsive breakpoints and one-tap navigation
- Native `<dialog>` gallery rather than a gallery library
- Existing keyboard behavior: Escape, arrow navigation, and focus restoration
- Explicit image dimensions, which protect against layout shift
- `fetchpriority="high"` on the home portrait
- Deferred JavaScript
- Google Fonts `display=swap` and existing preconnects
- Reduced-motion behavior
- Human-readable Markdown/YAML content ownership

## Findings by area

### Performance

1. **The complete Font Awesome bundle is loaded on every page.**

   `_includes/head.html` loads `assets/libs/fontawesome/all.min.js`, while `_includes/footer.html` uses only six brand icons. This costs about 548 KB of compressed transfer and requires the browser to parse 1.53 MB of JavaScript on every page.

2. **All gallery and contact images load eagerly.**

   The generated site contains 22 `<img>` elements across English/Chinese output, with zero `loading="lazy"` and zero `decoding="async"` attributes. The English gallery alone eagerly downloads 1.76 MB of image data even when most images begin below the fold.

3. **The home portrait is oversized for its displayed slot.**

   `home.jpg` is 1536 × 2048 and 760 KB but is capped at approximately 432 × 576 CSS pixels on larger screens. It should retain an adequate high-density candidate, but most devices do not need the full current file.

4. **The active photographs have no responsive source selection.**

   Home, contact, and gallery templates use one JPEG URL per image. Mobile clients therefore receive the same file as large screens.

5. **The generated deployment contains substantial dead weight.**

   Jekyll copies unused assets and legacy pages into `_site`. This does not automatically increase a normal page request, but it increases repository cloning, Pages artifact generation/upload, storage, and the number of public URLs that must be maintained.

6. **CSS and first-party JavaScript are not meaningful bottlenecks.**

   The stylesheet compresses to 5.6 KB and `main.js` to 842 bytes. Splitting either by page would add template conditions and more cache/request bookkeeping for negligible savings.

### Build and dependencies

1. **The build is healthy but not reproducible.**

   `Gemfile.lock` is ignored. The gemspec allows Jekyll `~> 4.2`, while the audit machine resolved Jekyll 4.4.1. A future install can silently resolve a different dependency set.

2. **The repository behaves like a direct site but retains theme-gem scaffolding.**

   `academic.gemspec` and `_sass/main.scss` are remnants of the original theme structure. The live stylesheet is the standalone `assets/css/main.scss`; `_sass/main.scss` is not imported.

3. **Ruby emits a future compatibility warning.**

   Jekyll currently warns that `logger` will no longer be bundled with Ruby starting in Ruby 3.5. This should be handled through a tested dependency update or explicit dependency when the runtime is upgraded, not through an unverified one-off change.

4. **There is no continuous integration check.**

   No workflow currently proves that a clean checkout builds or that generated local links remain valid.

### Repository and content hygiene

Likely starter-theme or unused material includes:

- `assets/img/lab-technician.jpg` — 12.84 MB
- `assets/img/graduate-student.jpg` — 7.89 MB
- `assets/img/primary-investigator.jpg` — 7.84 MB
- Seven other unreferenced JPGs — about 2.29 MB combined
- `publications/1501.07274.pdf` — 7.09 MB and only named by unused starter publication data
- `assets/libs/bootstrap/` — about 583 KB and not loaded by any HTML page
- `screenshot.png` — about 515 KB and not referenced
- `assets/favicon-master.png` — about 507 KB and not needed in the published site
- Twelve sample PDFs under `courses/` — about 212 KB
- Three sample course pages and three sample people pages
- `_layouts/people.html`, which is not selected by any page
- `_data/publications.yml`, which contains unrelated starter research and is not rendered
- The `featured` and `index` sections in `_data/settings.yml`, which are not rendered
- `_sass/main.scss`, which is not imported
- `_posts/Abstract accepted by CIETAL 2025.md`, which lacks a post date prefix and is not generated
- `_posts/2024-12-10-Abstract Accepted by CIETAL 2025!`, which lacks a Markdown extension and is not generated
- `courses/XX Encuentro de Morfólogos`, which lacks an extension and is not generated

Git history shows several of the largest files originated in the early “Get started” theme commit. They should still be checked for intentional direct/public use before removal.

### Correctness and routing

1. **Seven generated language-switch links are broken.**

   The header derives a Chinese URL for every English page. The three legacy course pages, one course post, and three people pages have no Chinese counterpart, so their switcher links point to missing pages.

2. **Translation routing is based on path arithmetic, not explicit pairing.**

   This works for the current main pages and posts, but it is fragile when a page is renamed or exists in only one language.

3. **Post slugs are inconsistent and one contains a persistent typo.**

   Filenames vary in case and spacing, and `Doctoral-research-proposal-denfense` is misspelled in English and Chinese URLs. Changing public URLs without redirects would be worse than retaining them, so any normalization must include redirect preservation.

4. **The contact email uses a placeholder as a real `mailto:` target.**

   `[firstname].[surname]@upf.edu` may be intentional anti-spam text, but clicking it does not produce a usable address. This needs a content/privacy decision rather than an automatic code change.

### Accessibility and security hygiene

Positive findings:

- All rendered `<img>` elements have `alt` attributes.
- No generated page contains duplicate IDs.
- A skip link is present.
- The menu button exposes `aria-expanded` and `aria-controls`.
- Gallery buttons have accessible names.
- The native dialog restores focus to the opening image.
- Reduced-motion preferences are honored.

Improvements:

1. **Nine `target="_blank"` links lack an explicit `rel="noopener noreferrer"`.**

   Seven are on the English home page, and one appears in each language version of the 2024 poster post.

2. **Chinese pages retain English interface labels for assistive technology.**

   “Skip to content,” “Menu,” “Primary navigation,” “Language selector,” “Social profiles,” and the home-link label should be localized when `page.lang == "zh"`.

3. **The full-screen mobile menu does not manage background focus.**

   Scrolling is locked, but keyboard users can still tab into content behind the menu. Use a small, well-tested focus strategy—preferably `inert` on the main/footer while open plus focus restoration—without building a custom navigation framework.

4. **Contrast should receive a rendered verification pass.**

   The palette appears intentionally high-contrast in source, but final contrast should be measured in both color schemes, including small metadata text and interactive states.

### SEO and internationalization

Positive findings:

- `jekyll-seo-tag` emits titles, canonical URLs, Open Graph basics, and JSON-LD.
- The root `<html lang>` switches correctly between `en` and `zh`.
- The main English/Chinese page pairs currently resolve.

Improvements:

1. **Chinese pages emit the English site description.**

   `_config.yml` defines `description_zh`, but generated Chinese metadata still uses the English `description`.

2. **There are no `hreflang` alternate links.**

   Paired pages should emit `en`, `zh`, and optionally `x-default` alternates. Only emit an alternate when the counterpart exists.

3. **There is no social-preview image.**

   A deliberately selected, compressed `og:image` would improve link previews without affecting page visuals.

4. **There is no generated sitemap.**

   Add a sitemap only through a deployment-compatible Jekyll plugin or a simple static generation step.

5. **Many pages rely on the global description.**

   Add concise, language-specific front-matter descriptions to core pages and important posts. This is content work, not a templating workaround.

6. **There is no custom 404 page.**

   A bilingual or language-neutral 404 page would improve recovery from old URLs and typos.

### Maintainability

1. **English and Chinese layout pairs duplicate substantial structure.**

   `home`, `gallery`, `contact`, `post`, `publications`, and `conferences` each have parallel layouts/includes. A structural correction often has to be applied twice.

2. **Some content ownership is unclear.**

   Publications exist in page markup while an unrelated `_data/publications.yml` remains in the repository. Gallery prose is embedded inside two large layout files. Settings contain unused theme keys.

3. **The README is a wishlist, not an operating guide.**

   It does not document a clean install, build, validation, bilingual content workflow, image expectations, or deployment model.

4. **There is no automated regression boundary.**

   The current build can succeed while emitting broken language links or reintroducing eager images.

## Prioritized implementation plan

### Phase 0 — Establish visual and functional guardrails

Priority: immediate
User-visible change: none

1. Capture baseline screenshots for:

   - English and Chinese home pages
   - Gallery with dialog open
   - Services, conferences, CV, contact, and one post
   - Desktop around 1440 px, tablet around 900 px, and mobile around 390 px
   - Light and dark color schemes
   - Mobile navigation open and closed

2. Record a Lighthouse or equivalent cold-cache baseline for home, gallery, and contact once a browser is available.

3. Add a lightweight repository check that:

   - Runs `bundle exec jekyll build --trace`
   - Fails on missing internal `href`/`src` targets
   - Fails on duplicate IDs
   - Checks image `alt`, `width`, and `height`
   - Checks `target="_blank"` links for the required `rel`
   - Checks that language alternates exist before rendering them

4. Adopt the budgets in the “Acceptance criteria” section below.

Rationale: performance work that touches icons or images needs a stable proof that appearance and behavior did not drift.

### Phase 1 — Remove the global icon runtime

Priority: highest
Effort: low
Risk: low with screenshot comparison

1. Replace `assets/libs/fontawesome/all.min.js` with either:

   - One small local SVG symbol sprite referenced by `<svg><use>`, or
   - Six inline SVG brand icons in a shared include

2. Keep the current:

   - Six destinations
   - Accessible labels
   - 2.25 rem circular controls
   - `currentColor` behavior
   - Hover colors and vertical movement

3. Remove the Font Awesome script from `_includes/head.html`.

4. Delete the Font Awesome bundle after the rendered footer is verified.

Expected result: save about 548 KB of compressed transfer and eliminate parsing/execution of 1.53 MB of JavaScript on every page. This should be the largest single user-facing improvement.

### Phase 2 — Improve image loading without introducing a heavy pipeline

Priority: highest
Effort: low to medium
Risk: low for loading attributes; medium for recompression

1. Keep the home portrait eager and high-priority.

2. Add:

   - `loading="lazy"` and `decoding="async"` to gallery images that begin below the fold
   - `loading="lazy"` and `decoding="async"` to the contact portrait
   - Eager loading for the first gallery image only if a rendered check shows it is the page's likely LCP

3. Re-encode the ten active photographs with metadata stripped and a visually conservative quality setting.

4. Add responsive candidates where the current width mismatch is meaningful:

   - Home portrait: small/mobile and high-density/desktop candidates
   - Contact portrait: mobile and desktop candidates
   - Gallery: at most two practical widths per image

5. Prefer a simple committed-asset convention over a Jekyll image plugin unless the deployment is moved to a custom Actions build. If derivative generation is scripted, keep it to one documented command and do not require a runtime image service.

6. Preserve:

   - Existing aspect ratios and crop behavior
   - Existing `width`/`height` or equivalent aspect-ratio reservation
   - Original image URLs when they may have inbound links
   - A high-quality source outside the published asset path if originals need archival

Expected result: drastically reduce gallery initial transfer and reduce the 760 KB home LCP candidate while retaining photographic quality.

### Phase 3 — Remove starter-theme deployment weight

Priority: high for repository/deployment health; low for normal page transfer
Effort: low
Risk: medium because old files may have direct inbound URLs

1. Check GitHub Pages analytics/Search Console and repository intent for direct use of:

   - Legacy `/courses/` and `/people/` URLs
   - `publications/1501.07274.pdf`
   - Unreferenced personal images

2. In a dedicated cleanup commit:

   - Remove unused Bootstrap and its source map
   - Remove dead `_sass/main.scss`
   - Remove unused theme layouts/data/settings keys
   - Remove malformed duplicate/orphan post files
   - Remove sample course pages/PDFs and people pages/images when confirmed unused
   - Remove `screenshot.png` if it will not be used in documentation

3. Preserve useful source-only files, such as a favicon master, outside the published Jekyll source or list them under `_config.yml` `exclude`.

4. Rebuild and compare the generated URL inventory before/after.

Expected result: reduce the roughly 44.8 MB generated site to a small fraction of its current size. Do not count this as a page-speed win unless a removed asset was actually requested by that page.

### Phase 4 — Fix routing, accessibility, and metadata

Priority: high
Effort: low to medium
Risk: low

1. Replace path-derived language switching with explicit page pairing:

   - Add a stable `translation_key` or explicit counterpart URL in front matter
   - Build a small lookup include
   - Hide or disable the unavailable alternate rather than link to a 404

2. Remove the seven broken legacy language links, either by removing those pages or by making the switcher counterpart-aware.

3. Localize shared interface labels for Chinese pages.

4. Add `rel="noopener noreferrer"` to the nine identified external links.

5. Make the mobile menu contain focus and restore it to the toggle when closed.

6. Feed `description_zh` or page-level Chinese descriptions into SEO output.

7. Add valid `hreflang` links only for confirmed page pairs.

8. Add page-level descriptions, a social-preview image, a sitemap, and a custom 404 page.

9. Decide whether to expose a functional email link or deliberately keep non-clickable anti-spam text.

### Phase 5 — Simplify bilingual structure without over-abstracting it

Priority: medium
Effort: medium
Risk: medium because template refactors can cause visual drift

1. Merge only the near-identical structural pairs first:

   - `post.html` and `post_zh.html`
   - `contact.html` and `contact_zh.html`
   - `publications.html` and `publications_zh.html`
   - `conferences.html` and `conferences_zh.html`

2. Store short interface labels in one small `_data/i18n.yml` keyed by language.

3. Consolidate the home and gallery structures only after the smaller merges prove the pattern. Keep long-form prose readable; do not force paragraphs into a dense translation dictionary merely to remove lines.

4. Give gallery entries a single source of truth for image path, dimensions, date/place, and language-specific alt text. Keep long English/Chinese narratives in a format editors can comfortably update.

5. Remove unused data only after the live templates no longer reference it.

6. Retain a small number of clear includes instead of creating a generic component system.

### Phase 6 — Make builds reproducible and documented

Priority: medium
Effort: low to medium
Risk: low after confirming GitHub Pages deployment mode

1. Document whether Pages uses branch-based Jekyll or a custom GitHub Actions build.

2. Make dependencies explicit for that model:

   - Commit `Gemfile.lock` for a custom Actions build, or
   - Use the supported Pages dependency model and pin the CI environment accordingly

3. Decide whether this is still a distributable theme gem. If not, replace the gemspec indirection with direct site dependencies after verifying deployment.

4. Resolve the Ruby `logger` warning through the selected, tested runtime/dependency set.

5. Add a minimal CI workflow for clean install, Jekyll build, generated link checks, and size budgets.

6. Rewrite `README.md` to include:

   - Prerequisites and clean install
   - Local build and preview
   - Validation command
   - How to add an English/Chinese page or post pair
   - How to add and optimize gallery images
   - Public URL stability/redirect rules
   - Deployment ownership

### Phase 7 — Normalize content carefully

Priority: lower
Effort: medium
Risk: medium due to public URLs

1. Choose lowercase, hyphenated filenames for new content.

2. Do not rename existing public posts unless the old URL receives a permanent redirect.

3. Correct the `denfense` slug only as a redirect-backed migration.

4. Run a live external-link check and repair confirmed dead URLs.

5. Review the README carousel wishlist. An autoplay carousel would add image transfer, motion, and interaction complexity; it should not be added unless it serves a clear content goal and has an accessible, user-controlled design.

## Acceptance criteria

### Visual and interaction invariants

- No unintended difference in palette, typography, spacing, card geometry, image crop, or responsive layout
- Footer icons retain the same apparent size, color, shape, and hover treatment
- Home portrait remains sharp at normal and high-density display sizes
- Gallery thumbnails remain sharp and the dialog shows an adequate large image
- Mobile navigation remains directly accessible and becomes keyboard-contained
- Gallery Escape, previous/next arrows, backdrop close, and focus restoration continue to work
- Light, dark, and reduced-motion modes continue to work

### Correctness

- `bundle exec jekyll build --trace` succeeds from a clean dependency install
- `git diff --check` succeeds
- Zero missing local `href` or `src` targets
- Zero duplicate IDs
- Zero rendered images without useful `alt`, width, and height/aspect reservation
- Zero unavailable language-counterpart links
- Zero `target="_blank"` links without the selected safe `rel`
- English and Chinese canonical and alternate metadata point to existing pages

### Performance budgets

- Global local CSS + JavaScript: under 25 KB gzip after removing Font Awesome
- First-party JavaScript: under 10 KB gzip unless a measured feature justifies more
- Home local transfer, excluding web fonts/favicons: target under 500 KB
- Gallery initial local transfer, excluding web fonts/favicons: target under 400 KB before scrolling
- No below-the-fold gallery image fetched eagerly
- No responsive image candidate materially wider than needed for its rendered width and device pixel ratio
- Generated-site size: target under 8 MB after approved legacy cleanup
- Jekyll build: remain under 2 seconds on a typical development machine

The budgets should fail CI only on deterministic file/link checks. Lighthouse should be reviewed on representative local or production runs rather than used as a flaky per-commit gate.

## Recommended commit sequence

1. Add validation checks and record baselines
2. Replace Font Awesome with local SVG icons
3. Add lazy loading and responsive/optimized active images
4. Remove approved starter-theme assets and orphan pages
5. Fix counterpart-aware language routing, localized labels, and external-link attributes
6. Improve SEO metadata, sitemap, and 404 handling
7. Consolidate low-risk bilingual layout pairs
8. Pin/document dependencies and add CI

Each step should be independently buildable and reviewable. Asset deletion and public URL migration should remain separate commits so they can be reverted without undoing performance improvements.

## Changes not recommended

- Migrating from Jekyll to React, Astro, or another framework solely for performance
- Splitting the 5.6 KB compressed stylesheet into page bundles
- Splitting the 842-byte compressed first-party script by page
- Inlining and maintaining critical CSS
- Adding a service worker for this small, frequently cacheable static site
- Adding a runtime image CDN
- Adding a broad CSS framework
- Minifying generated HTML at the cost of harder debugging
- Loading social icons from another third-party runtime
- Adding an autoplay image carousel without a separate content/accessibility decision

These approaches would increase moving parts more than they improve the current site.
