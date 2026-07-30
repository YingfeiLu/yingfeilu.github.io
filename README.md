# Yingfei Lu’s academic website

This repository contains the source for [yingfeilu.github.io](https://yingfeilu.github.io), a bilingual English–Chinese academic website built with Jekyll. The site intentionally uses static HTML, one small stylesheet, and one small first-party script.

## Local setup

Prerequisites:

- Ruby 3.4
- Bundler
- Python 3 for repository validation
- ImageMagick only when regenerating responsive image assets

Install the pinned Ruby dependencies:

```sh
bundle install
```

Build the site:

```sh
bundle exec jekyll build --trace
```

Run a local preview:

```sh
bundle exec jekyll serve
```

Run the complete deterministic validation:

```sh
script/validate
```

That command builds the site, checks generated internal links and fragments, duplicate IDs, image attributes, language alternates, external-link safety attributes, metadata, and performance budgets, then runs `git diff --check`.

## Content structure

- Root Markdown pages are the English site.
- `zh/` contains the Chinese pages and translated updates.
- English news posts live in `_posts/`.
- Shared labels live in `_data/i18n.yml`.
- Navigation, social profiles, and contact details live in `_data/settings.yml`.
- Layouts and reusable markup live in `_layouts/` and `_includes/`.
- `assets/css/main.scss` and `assets/js/main.js` are the site’s first-party front end.

## Add a bilingual page or update

Every translated page must declare an explicit reciprocal `translation_url`. A Chinese page must also declare `lang: zh`.

For an English page:

```yaml
translation_url: "/zh/example.html"
```

For its Chinese counterpart:

```yaml
lang: zh
translation_url: "/example.html"
```

English posts belong in `_posts/YYYY-MM-DD-lowercase-hyphenated-title.md`. Chinese translations use the matching public date path under `zh/YYYY/MM/DD/`, plus `date` and `translation_type: update` in front matter. New filenames should be lowercase and hyphenated. Do not rename an existing public page or post unless the old URL receives a real permanent redirect.

Add a concise page-level `description` in the page’s own language. The build emits language alternates only when `translation_url` is present, so an unpaired page must omit that field.

## Images

Keep original public image URLs stable. Add or replace source photographs first, then regenerate committed responsive derivatives with:

```sh
script/build_images
```

The script requires ImageMagick and strips metadata from derivatives. Templates must retain useful `alt`, `width`, and `height` attributes. The home portrait stays eager with `fetchpriority="high"`; contact and gallery images stay lazy-loaded with asynchronous decoding.

`source-assets/` is for archival design sources that should remain out of the generated site.

## Deployment

The expected deployment is GitHub Pages from the `main` branch. `.github/workflows/ci.yml` validates pushes and pull requests but does not publish the site. `Gemfile.lock` is committed so local and CI builds use the same dependency set.

The generated `_site/` directory is intentionally ignored and must not be committed.
