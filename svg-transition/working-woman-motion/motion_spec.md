# Working Woman Motion Spec

## Brief

- Personality: focused, calm, professional.
- Context: a one-shot splash or in-page illustration reveal.
- Duration: 1600 ms. The deliberate pace keeps the detailed silhouette readable without feeling theatrical.
- Source: “Working Woman” by sentya irma, Noun Project icon 7641720. Confirm the Creative Commons attribution requirements before distribution.

## Part inventory

| Part | SVG id | Role |
| --- | --- | --- |
| Woman | `person` | Primary subject and first visual anchor |
| Laptop screen | `laptop-screen` | Secondary working-context cue |
| Laptop base | `laptop-base` | Tertiary settle and visual baseline |

## Choreography

| Time | Pose |
| --- | --- |
| 0–224 ms | Empty stage and quiet anticipation |
| 224–992 ms | Person rises into place with a restrained overshoot |
| 384–1088 ms | Laptop screen opens from its lower-left hinge |
| 608–1184 ms | Laptop base slides and expands into place |
| 1184–1600 ms | All parts settle exactly onto the verified static vector |

The staging uses overlapping action rather than simultaneous movement. The motion applies anticipation, staging, slow in/slow out, follow-through, timing, solid drawing, and appeal. Deformation is intentionally limited because the source reads as a professional workplace icon.

## Geometry QA

- Vector complexity: three semantic paths, derived from six source contours with 90 total points.
- Initial trace IoU: 0.981085.
- Source coverage: 0.994561.
- Vector precision: 0.986377.
- Smoothness verdict: pass for the source’s intentionally angular icon style; no 1 px staircase runs were retained.
- Final-frame contract: every animation reaches opacity 1 with no transform at 1600 ms.

## Tunable controls

- Change `--p2m-duration` in the SVG to scale the complete reveal.
- Keep the existing easing family to preserve the calm, professional motion voice.
- Reduced-motion users receive the complete static icon immediately.
