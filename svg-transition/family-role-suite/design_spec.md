# Family ↔ Work Role Suite Design Spec

## Goal

Represent six people as complete individuals across family life and professional life. Each role requires two static forms and two independently playable SVG transitions: family → work and work → family.

## Shared visual contract

- 512 × 512 SVG canvas with a transparent background.
- Monochrome `currentColor` silhouettes with geometric, low-complexity paths.
- The head, hair, age cues, and body position remain stable between states so identity survives the transition.
- Family identity is communicated through an independent home activity, never through holding or standing beside a child.
- Work identity is communicated through an occupation-specific prop and clothing cue.
- Every SVG is self-contained, accessible, dependency-free, and readable at 128 px.

## Role matrix

| Role | Family form | Work form |
| --- | --- | --- |
| Mother | Cooking: apron, saucepan, steam | Office professional: laptop |
| Father | Home repair: toolbox, wrench | Site engineer: hard hat, blueprint |
| Daughter | Reading: open book | Scientist: microscope, lab coat |
| Son | Leisure: skateboard, headphones | Photographer: camera, shoulder strap |
| Grandfather | Daily mobility: cane, cardigan | Teacher: lectern, open lesson book |
| Grandmother | Knitting: yarn, needles, shawl | Tailor: sewing machine, measuring tape |

## Motion contract

- Each direction is delivered as its own SVG file and plays once for 2400 ms, then holds on the destination.
- A brief anticipation phase compresses the source before a radial reveal introduces the destination.
- The transition focus originates at the changing activity prop while the face remains visually anchored.
- Source and destination silhouettes use the exact same markup as their corresponding static SVGs.
- `prefers-reduced-motion: reduce` immediately displays the destination state.

## Acceptance

- Six roles × four deliverables produce 24 valid SVG files.
- Every role has `family.svg`, `work.svg`, `family-to-work.svg`, and `work-to-family.svg`.
- Static endpoint markup exactly matches the source/destination groups embedded in both animation directions.
- No child appears in any composition.
- The preview has no horizontal overflow at a 390 px viewport.
- All artwork remains inside the 512 × 512 viewBox and readable in a 128 px contact sheet.
