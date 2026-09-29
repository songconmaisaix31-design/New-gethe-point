# Family ↔ Work SVG Suite Technical Specification

## Delivery structure

Generated assets live under `svg-transition/family-work-suite/`. Each role owns a directory with four SVG files. A root `preview.html` presents all roles and both transition directions.

## Generation

`generate_family_work_suite.py` is the single source of truth for shared animation CSS, accessibility markup, file naming, and package layout. Role-specific vector groups remain explicit data so visual differences are reviewable without introducing a rendering dependency.

The generator uses only the Python standard library. Generated SVG files contain no script, remote reference, raster image, font, or external stylesheet.

## Animation model

Each transition embeds exact copies of its static family and work groups. CSS keyframes animate opacity and transforms, while an SVG mask expands from the role's activity-prop focus point. The destination holds through `animation-fill-mode: forwards`.

## Verification

1. Generate all assets twice and compare hashes to prove deterministic output.
2. Parse every SVG as XML and verify accessibility metadata.
3. Verify file count, naming, absence of external resources/scripts, and static-to-animation endpoint equality.
4. Render the responsive gallery at desktop and 390 px widths when a local browser runtime is available.
5. Render a 128 px contact sheet and inspect role/occupation legibility.
6. Package the generated directory without changing source assets.

## Risks

- CSS animation support varies in embedded SVG contexts. Opening the SVG directly or loading it through `<object>` is the supported path.
- Creative Commons attribution for the Working Woman source must be retained and confirmed before external distribution.
