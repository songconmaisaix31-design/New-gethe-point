# Working Woman ↔ Mother Motion Spec

## Goal

Show one recognizable woman moving between professional work and everyday home life without implying that either role replaces her identity.

## Visual contract

- Preserve the working-woman bun, head silhouette, facial negative space, monochrome fill, angular edge language, and 512 × 512 canvas.
- Replace the laptop with a saucepan, lid, and steam. Add a negative-space apron to the same woman; no child appears in the composition.
- Keep the head in the same position across both roles so the character remains visibly continuous.

## Motion contract

- Personality: caring, focused, assured.
- Duration: 2000 ms in each direction.
- Work → Home: the laptop folds down toward the future saucepan, then a radial reveal grows from the cooking area.
- Home → Work: the cooking silhouette settles away while the laptop opens from the saucepan area.
- Both directions use anticipation, staging, slow in/slow out, overlapping action, follow-through, timing, solid drawing, and appeal.
- The first and final states are exact static role shapes. Reduced-motion mode immediately shows the destination.

## Acceptance

- Cooking mother role remains recognizable at 128 px through the apron, saucepan, lid, and steam.
- No mid-animation clipping or overlapping edge artifacts.
- Each SVG opens independently and holds on its destination.
- Desktop and narrow-screen preview layouts remain usable.
- The final browser-rendered frame matches the corresponding static SVG.

## QA results

- Static mother: recognizable after a browser-rendered 512 px frame is downsampled to 128 px.
- Work → Home final frame: exact same-pipeline match with `mother.svg`.
- Home → Work final frame: exact same-pipeline match with the verified working-woman `logo.svg`.
- Motion frames inspected at 100, 650, 1250, and 2300 ms in both directions; no clipping or edge artifacts found.
- Mobile preview: Playwright viewport width 390 px and document scroll width 390 px; no horizontal overflow.
