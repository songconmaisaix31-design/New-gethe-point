# SVG motion studies

This bundle contains standalone and bidirectional SVG motion studies:

- `woman-to-family.svg`
- `family-to-woman.svg`
- `working-woman-motion/working-woman-motion.svg`
- `working-woman-mother/mother.svg`
- `working-woman-mother/working-woman-to-mother.svg`
- `working-woman-mother/mother-to-working-woman.svg`
- `family-role-suite/father.svg`
- `family-role-suite/daughter.svg`
- `family-role-suite/son.svg`
- `family-role-suite/grandfather.svg`
- `family-role-suite/grandmother.svg`
- `family-work-suite/` — six family/work pairs with both transition directions

Open `preview.html` to view and replay both directions. Each SVG embeds its working-woman source layer and can be moved or used independently. The separate `working-woman.png` is retained as a source asset.

The standalone working-woman motion is a true three-part vector reconstruction. Open `working-woman-motion/logo_motion.html` for the replayable QA showcase, or use `working-woman-motion/working-woman-motion.svg` directly as a self-contained animated asset.

The mother-role set keeps the same character silhouette and replaces the work setup with an apron, saucepan, and steam; it deliberately contains no child figure. Open `working-woman-mother/preview.html` to inspect the static mother and replay both role transitions.

The family-role suite adds five pure-vector static roles and reuses the mother asset as its sixth card. Open `family-role-suite/preview.html` for the complete responsive set; `family-role-suite/design_spec.md` records the shared geometry and identity cues.

The family/work suite expands every person into two exact static endpoints plus `family-to-work.svg` and `work-to-family.svg`. Open `family-work-suite/preview.html` to inspect all 24 self-contained SVG assets. Family forms use independent home activities rather than a child as an identity cue.

Transition duration is controlled by `--duration` in each animated SVG. Every animation respects `prefers-reduced-motion` and holds on its destination state after playback.

## Source notes

- Working Woman icon 7641720 by sentya irma, via [Noun Project](https://thenounproject.com/icon/working-woman-7641720/). The source page identifies the icon license as Creative Commons; confirm attribution requirements for the intended distribution.
- Family artwork was supplied by the user as `family.svg` and identifies SVG Repo as its source.

The Noun Project shortcut supplied by the user resolves to a page that exposes a PNG preview but not a direct original SVG asset. For that reason, the output files are SVG animation containers with the PNG preview as the working-woman layer; the family layer remains vector.
