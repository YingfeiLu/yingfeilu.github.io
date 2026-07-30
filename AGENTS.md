# Repository instructions

## Scope and intent

This is Yingfei Lu’s bilingual English–Chinese Jekyll site. Preserve the current visual identity: typography, palette, spacing, responsive layout, dark mode, gallery crops, and editorial content. Prefer static, reversible changes; do not add a JavaScript framework, CSS framework, runtime image service, service worker, or autoplay carousel without an explicit request.

## Source ownership

- Edit source files, never `_site/`.
- English pages are at the repository root; Chinese pages are under `zh/`.
- English updates are Jekyll posts in `_posts/`; Chinese update translations are dated pages under `zh/YYYY/MM/DD/`.
- Shared interface labels belong in `_data/i18n.yml`.
- Navigation, social links, and contact details belong in `_data/settings.yml`.
- Styles and behavior belong in `assets/css/main.scss` and `assets/js/main.js`.
- Keep long-form English and Chinese copy readable in Markdown or focused templates; do not hide it in a generic component abstraction.

## Bilingual routing and metadata

- Every translated page or post pair must have reciprocal `translation_url` front matter.
- Chinese content must declare `lang: zh`.
- Add a concise, language-appropriate `description` to new core pages.
- Never derive a translation link by adding or removing `/zh`.
- Never emit a language alternate unless its target exists.
- Use lowercase, hyphenated filenames for new content.
- Do not rename an existing public URL without a real permanent redirect.

## Images and accessibility

- Preserve original public image URLs.
- Run `script/build_images` after changing any active home, contact, gallery, or social-preview source image.
- Keep useful `alt`, intrinsic `width`, and intrinsic `height` attributes.
- Keep the home portrait eager and high-priority.
- Keep contact and gallery images lazy-loaded with `decoding="async"`.
- External links using `target="_blank"` must include `rel="noopener noreferrer"`.
- Preserve keyboard access, reduced-motion behavior, dialog focus restoration, and mobile-menu focus containment.

## Validation

Install dependencies with `bundle install`, then run:

```sh
script/validate
```

The validation must pass before handoff. It covers the Jekyll build, generated links and fragments, duplicate IDs, image contracts, language metadata, safe external-link attributes, size budgets, and whitespace errors.

If visual changes are intentional, also inspect English and Chinese home, gallery, contact, services, conferences, CV, and a post at desktop and mobile widths in light and dark mode. Do not claim rendered browser or device verification unless it was actually completed.

## Generated and archival files

- Do not commit `_site/`, `.jekyll-cache/`, or `.DS_Store`.
- `source-assets/` is excluded from publication and may contain archival masters.
- Keep global local CSS and JavaScript under 25 KB gzip, first-party JavaScript under 10 KB gzip, and the generated site under 8 MB unless a measured requirement justifies changing the budgets.
