from __future__ import annotations

import html
import json
import xml.etree.ElementTree as ET
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path


SOURCE_DIR = Path(__file__).resolve().parent
SVG_TRANSITION_DIR = SOURCE_DIR.parent
OUTPUT_DIR = SVG_TRANSITION_DIR / "family-work-suite"
SVG_NS = "{http://www.w3.org/2000/svg}"


@dataclass(frozen=True)
class Role:
    slug: str
    label: str
    family_label: str
    work_label: str
    family_source: Path
    identity_ids: tuple[str, ...]
    work_prop: str
    focus: tuple[int, int]
    attribution: str = "Original vector artwork authored for the Family ↔ Work Role Suite."


ROLES = (
    Role(
        slug="mother",
        label="Mother",
        family_label="Cooking at home",
        work_label="Office professional",
        family_source=SVG_TRANSITION_DIR / "working-woman-mother" / "mother.svg",
        identity_ids=(),
        work_prop="",
        focus=(126, 356),
        attribution=(
            "Working Woman by sentya irma from Noun Project, icon 7641720, Creative Commons. "
            "Mother-role artwork and animation are original derivatives."
        ),
    ),
    Role(
        slug="father",
        label="Father",
        family_label="Home repair",
        work_label="Site engineer",
        family_source=SOURCE_DIR / "father.svg",
        identity_ids=("father-head", "father-mustache", "father-body"),
        work_prop="""
<g id="engineer-cues" fill="currentColor" fill-rule="evenodd" stroke-linecap="round" stroke-linejoin="round">
  <path id="hard-hat" d="M298 124 C302 94 321 73 351 66 L355 91 L371 91 L375 66 C403 74 422 96 426 124 L443 124 L443 143 L285 143 L285 124 Z" />
  <path id="blueprint" d="M38 315 L213 315 L225 432 L50 432 Z M65 342 L111 342 L111 359 L65 359 Z M127 342 L197 342 L197 359 L127 359 Z M66 377 L195 377 L195 394 L66 394 Z M66 409 L147 409 L147 421 L66 421 Z" />
  <path id="pencil" d="M216 286 L229 299 L183 345 L164 351 L170 332 Z" />
</g>""",
        focus=(126, 374),
    ),
    Role(
        slug="daughter",
        label="Daughter",
        family_label="Reading at home",
        work_label="Laboratory scientist",
        family_source=SOURCE_DIR / "daughter.svg",
        identity_ids=("daughter-head", "daughter-body"),
        work_prop="""
<g id="scientist-cues" fill="currentColor" fill-rule="evenodd" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round">
  <path id="microscope" stroke="none" d="M86 254 L129 254 L129 275 L118 275 L138 317 C156 356 143 392 109 408 L170 408 L170 432 L43 432 L43 408 L76 408 C107 398 123 377 120 352 C117 329 101 302 90 281 L78 281 L78 265 Z M145 287 L177 287 L188 307 L174 316 L161 302 L145 302 Z" />
  <path id="microscope-stage" stroke="none" d="M79 337 L179 337 L179 356 L79 356 Z" />
  <path id="lab-coat-lines" d="M319 274 L346 302 L374 274 M346 302 L346 412 M315 350 L338 350 M355 350 L380 350" fill="none" stroke-width="8" />
  <circle id="sample" cx="166" cy="326" r="10" stroke="none" />
</g>""",
        focus=(125, 350),
    ),
    Role(
        slug="son",
        label="Son",
        family_label="Skateboarding",
        work_label="Photographer",
        family_source=SOURCE_DIR / "son.svg",
        identity_ids=("son-head", "headphones", "son-body"),
        work_prop="""
<g id="photographer-cues" fill="currentColor" fill-rule="evenodd" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round">
  <path id="camera" stroke="none" d="M48 324 L83 324 L96 303 L153 303 L166 324 L206 324 L206 402 L48 402 Z M87 363 C87 392 111 414 140 414 C169 414 193 392 193 363 C193 334 169 312 140 312 C111 312 87 334 87 363 Z M107 363 C107 345 122 331 140 331 C158 331 173 345 173 363 C173 381 158 395 140 395 C122 395 107 381 107 363 Z" />
  <path id="flash" stroke="none" d="M66 302 L105 302 L111 324 L60 324 Z" />
  <path id="camera-strap" d="M81 320 C93 264 135 243 184 270 C203 281 218 302 224 326" fill="none" stroke-width="10" />
</g>""",
        focus=(133, 360),
    ),
    Role(
        slug="grandfather",
        label="Grandfather",
        family_label="Daily home life",
        work_label="Teacher and mentor",
        family_source=SOURCE_DIR / "grandfather.svg",
        identity_ids=("grandfather-head", "glasses", "grandfather-body"),
        work_prop="""
<g id="teacher-cues" fill="currentColor" fill-rule="evenodd" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round">
  <path id="lectern" stroke="none" d="M40 324 L216 324 L201 371 L151 371 L167 449 L88 449 L104 371 L55 371 Z M63 339 L193 339 L187 356 L69 356 Z" />
  <path id="lesson-book" stroke="none" d="M52 282 C83 272 111 279 130 294 L130 326 C108 312 83 307 52 315 Z M136 294 C158 277 183 272 212 282 L212 315 C184 307 159 312 136 326 Z" />
  <path id="pointer" d="M219 262 L172 332" fill="none" stroke-width="9" />
</g>""",
        focus=(130, 337),
    ),
    Role(
        slug="grandmother",
        label="Grandmother",
        family_label="Knitting at home",
        work_label="Professional tailor",
        family_source=SOURCE_DIR / "grandmother.svg",
        identity_ids=("grandmother-head", "low-bun", "glasses", "grandmother-body"),
        work_prop="""
<g id="tailor-cues" fill="currentColor" fill-rule="evenodd" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round">
  <path id="sewing-table" stroke="none" d="M31 393 L235 393 L235 417 L31 417 Z M52 417 L76 417 L70 457 L46 457 Z M195 417 L219 417 L225 457 L201 457 Z" />
  <path id="sewing-machine" stroke="none" d="M55 299 L164 299 C195 299 215 320 215 351 L215 393 L188 393 L188 351 C188 336 179 326 164 326 L139 326 L139 366 L168 366 L168 386 L61 386 L61 366 L104 366 L104 326 L55 326 Z M70 276 L125 276 L133 299 L62 299 Z" />
  <path id="needle" d="M139 326 L139 378" fill="none" stroke-width="6" />
  <path id="measuring-tape" d="M307 274 C322 297 340 307 359 303 C376 300 389 286 398 269" fill="none" stroke-width="8" stroke-dasharray="12 8" />
</g>""",
        focus=(133, 350),
    ),
)


def without_namespace(element: ET.Element) -> ET.Element:
    clone = deepcopy(element)
    for node in clone.iter():
        if isinstance(node.tag, str) and "}" in node.tag:
            node.tag = node.tag.split("}", 1)[1]
    return clone


def serialize(element: ET.Element) -> str:
    return ET.tostring(without_namespace(element), encoding="unicode", short_empty_elements=True)


def parse_source(path: Path) -> ET.Element:
    return ET.parse(path).getroot()


def find_by_id(root: ET.Element, element_id: str) -> ET.Element:
    for element in root.iter():
        if element.get("id") == element_id:
            return element
    raise ValueError(f"Missing element #{element_id} in source SVG")


def source_defs(root: ET.Element) -> str:
    defs = root.find(f"{SVG_NS}defs")
    if defs is None:
        return ""
    return "\n".join(serialize(child) for child in defs)


def source_art(root: ET.Element) -> str:
    excluded = {"title", "desc", "metadata", "defs"}
    return "\n".join(
        serialize(child)
        for child in root
        if child.tag.removeprefix(SVG_NS) not in excluded
    )


def work_art(role: Role, family_root: ET.Element) -> str:
    if role.slug == "mother":
        worker_root = parse_source(SVG_TRANSITION_DIR / "working-woman-motion" / "logo.svg")
        return source_art(worker_root).replace('fill="#000"', 'fill="currentColor"')

    identity = "\n".join(serialize(find_by_id(family_root, element_id)) for element_id in role.identity_ids)
    return (
        '<g id="work-art" fill="currentColor" fill-rule="evenodd" '
        'shape-rendering="geometricPrecision">\n'
        f"{identity}\n{role.work_prop.strip()}\n"
        "</g>"
    )


def metadata(role: Role) -> str:
    return f"  <metadata>{html.escape(role.attribution)}</metadata>"


def static_svg(role: Role, state: str, defs: str, art: str) -> str:
    state_label = role.family_label if state == "family" else role.work_label
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512" role="img" aria-labelledby="title description">
  <title id="title">{html.escape(role.label)} — {html.escape(state_label)}</title>
  <desc id="description">{html.escape(role.label)} shown in the {state} form: {html.escape(state_label.lower())}.</desc>
{metadata(role)}
  <defs>
{defs}
  </defs>
  <g id="state-art" data-state="{state}">
{art}
  </g>
</svg>
'''


def transition_css() -> str:
    return """
      :root { --duration: 2.4s; --enter: cubic-bezier(.16, 1, .3, 1); --settle: cubic-bezier(.22, 1, .36, 1); }
      .source, .destination, .reveal-disc, .focus-ring { transform-box: fill-box; transform-origin: center; }
      .source { animation: source-out var(--duration) var(--enter) .12s forwards; }
      .destination { opacity: 0; mask: url(#destination-reveal); animation: destination-in var(--duration) var(--settle) .12s forwards; }
      .reveal-disc { animation: reveal var(--duration) var(--enter) .12s forwards; }
      .focus-ring { fill: none; stroke: currentColor; stroke-width: 5; opacity: 0; animation: ring var(--duration) var(--settle) .12s forwards; }
      @keyframes source-out {
        0%, 20% { opacity: 1; transform: none; }
        38% { opacity: 1; transform: translateY(3px) scale(.975); }
        68% { opacity: .28; transform: translateY(-2px) scale(1.012); }
        100% { opacity: 0; transform: translateY(4px) scale(.96); }
      }
      @keyframes destination-in {
        0%, 16% { opacity: 0; transform: translateY(8px) scale(.92); }
        68% { opacity: 1; transform: translateY(-2px) scale(1.012); }
        86% { opacity: 1; transform: translateY(1px) scale(.997); }
        100% { opacity: 1; transform: none; }
      }
      @keyframes reveal { 0%, 16% { r: 0; } 100% { r: 650px; } }
      @keyframes ring { 0%, 16% { opacity: 0; r: 0; } 44% { opacity: .22; } 100% { opacity: 0; r: 650px; stroke-width: 1; } }
      @media (prefers-reduced-motion: reduce) {
        .source { animation: none; opacity: 0; }
        .destination { animation: none; opacity: 1; transform: none; }
        .reveal-disc { animation: none; r: 650px; }
        .focus-ring { animation: none; opacity: 0; }
      }
""".strip()


def transition_svg(
    role: Role,
    source_state: str,
    destination_state: str,
    defs: str,
    source: str,
    destination: str,
) -> str:
    source_label = role.family_label if source_state == "family" else role.work_label
    destination_label = role.family_label if destination_state == "family" else role.work_label
    focus_x, focus_y = role.focus
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512" role="img" aria-labelledby="title description">
  <title id="title">{html.escape(role.label)}: {source_state} to {destination_state}</title>
  <desc id="description">{html.escape(role.label)} transitions from {html.escape(source_label.lower())} to {html.escape(destination_label.lower())}.</desc>
{metadata(role)}
  <defs>
{defs}
    <mask id="destination-reveal" maskUnits="userSpaceOnUse">
      <rect width="512" height="512" fill="#000" />
      <circle class="reveal-disc" cx="{focus_x}" cy="{focus_y}" r="0" fill="#fff" />
    </mask>
    <style>
{transition_css()}
    </style>
  </defs>
  <g class="source" data-state="{source_state}">
{source}
  </g>
  <g class="destination" data-state="{destination_state}">
{destination}
  </g>
  <circle class="focus-ring" cx="{focus_x}" cy="{focus_y}" r="0" />
</svg>
'''


def preview_html() -> str:
    sections = []
    for role in ROLES:
        cards = (
            ("Family form", f"{role.slug}/family.svg", role.family_label),
            ("Work form", f"{role.slug}/work.svg", role.work_label),
            ("Family → Work", f"{role.slug}/family-to-work.svg", "Forward transition"),
            ("Work → Family", f"{role.slug}/work-to-family.svg", "Reverse transition"),
        )
        card_markup = "\n".join(
            f'''<article class="card"><div class="stage"><object data="{path}" type="image/svg+xml" aria-label="{html.escape(role.label)} — {html.escape(title)}"></object></div><h3>{html.escape(title)}</h3><p>{html.escape(cue)}</p></article>'''
            for title, path, cue in cards
        )
        sections.append(
            f'''<section class="role" aria-labelledby="{role.slug}-title"><div class="role-heading"><div><span>Family member</span><h2 id="{role.slug}-title">{html.escape(role.label)}</h2></div><button type="button" data-replay="{role.slug}">Replay transitions</button></div><div class="grid" data-role="{role.slug}">{card_markup}</div></section>'''
        )

    return f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Family ↔ Work SVG Suite</title>
    <style>
      :root {{ color-scheme: light; font-family: Inter, ui-sans-serif, system-ui, sans-serif; color: #181714; background: #f3efe7; }}
      * {{ box-sizing: border-box; }}
      body {{ margin: 0; min-width: 0; padding: 32px; }}
      main {{ width: min(1280px, 100%); min-width: 0; margin: 0 auto; }}
      header {{ display: flex; gap: 24px; align-items: end; justify-content: space-between; margin-bottom: 30px; }}
      h1 {{ margin: 0 0 8px; font-size: clamp(32px, 5vw, 64px); letter-spacing: -.055em; line-height: .98; }}
      .intro {{ max-width: 680px; margin: 0; color: #696158; font-size: 16px; line-height: 1.55; }}
      .role {{ min-width: 0; margin: 0 0 24px; padding: 20px; border: 1px solid #ddd5c9; border-radius: 28px; background: rgba(255,255,255,.72); box-shadow: 0 18px 50px rgba(57,44,29,.07); }}
      .role-heading {{ display: flex; align-items: end; justify-content: space-between; gap: 16px; margin-bottom: 14px; }}
      .role-heading span {{ color: #8b5e3c; font-size: 12px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }}
      h2 {{ margin: 2px 0 0; font-size: 26px; letter-spacing: -.035em; }}
      button {{ min-height: 40px; padding: 0 16px; border: 1px solid #ccc1b3; border-radius: 999px; color: #28231e; background: #fff; font: inherit; font-size: 13px; font-weight: 650; cursor: pointer; }}
      button:hover {{ background: #f6efe7; }}
      .grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; min-width: 0; }}
      .card {{ min-width: 0; padding: 12px; border: 1px solid #e4ddd3; border-radius: 18px; background: #fff; }}
      .stage {{ display: grid; place-items: center; width: 100%; min-width: 0; aspect-ratio: 1; overflow: hidden; border-radius: 12px; background: linear-gradient(145deg, #fbfaf7, #eee8dd); }}
      object {{ display: block; width: 96%; max-width: 100%; height: 96%; color: #171614; }}
      h3 {{ margin: 11px 0 2px; font-size: 15px; letter-spacing: -.01em; }}
      .card p {{ margin: 0; color: #777067; font-size: 12px; }}
      @media (max-width: 900px) {{ .grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
      @media (max-width: 540px) {{ body {{ padding: 16px; }} header {{ align-items: start; flex-direction: column; }} .role {{ padding: 14px; border-radius: 22px; }} .role-heading {{ align-items: start; flex-direction: column; }} .grid {{ grid-template-columns: minmax(0, 1fr); }} button {{ width: 100%; }} }}
    </style>
  </head>
  <body>
    <main>
      <header><div><h1>Family ↔ Work</h1><p class="intro">Six people, two complete forms each, and both transition directions. Family identity is shown through independent home life—not through holding a child.</p></div></header>
      {''.join(sections)}
    </main>
    <script>
      document.querySelectorAll('[data-replay]').forEach((button) => {{
        button.addEventListener('click', () => {{
          const role = button.dataset.replay;
          document.querySelectorAll(`[data-role="${{role}}"] object`).forEach((object) => {{
            if (!object.data.includes('-to-')) return;
            const source = object.data.split('?')[0];
            object.data = `${{source}}?replay=${{Date.now()}}`;
          }});
        }});
      }});
      if (new URLSearchParams(location.search).has('qa')) {{
        document.documentElement.dataset.viewportWidth = String(window.innerWidth);
        document.documentElement.dataset.scrollWidth = String(document.documentElement.scrollWidth);
      }}
    </script>
  </body>
</html>
'''


def contact_sheet_html() -> str:
    cards = []
    for role in ROLES:
        for state in ("family", "work"):
            cards.append(
                f'<figure><object data="../{role.slug}/{state}.svg" type="image/svg+xml"></object>'
                f'<figcaption>{html.escape(role.label)} — {state.title()}</figcaption></figure>'
            )
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>128 px contact sheet</title><style>
html,body{{margin:0;background:#eee8dd;font-family:Arial,sans-serif}}body{{width:960px;padding:24px}}main{{display:grid;grid-template-columns:repeat(6,128px);gap:24px}}figure{{margin:0}}object{{display:block;width:128px;height:128px;color:#171614;background:#fff}}figcaption{{padding-top:6px;font-size:11px;color:#2b2723}}
</style></head><body><main>{''.join(cards)}</main></body></html>'''


def motion_sheet_html() -> str:
    cards = []
    for role in ROLES:
        for direction in ("family-to-work", "work-to-family"):
            cards.append(
                f'<figure><object data="../{role.slug}/{direction}.svg" type="image/svg+xml"></object>'
                f'<figcaption>{html.escape(role.label)} — {html.escape(direction)}</figcaption></figure>'
            )
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Motion midpoint contact sheet</title><style>
html,body{{margin:0;background:#eee8dd;font-family:Arial,sans-serif}}body{{width:1200px;padding:24px}}main{{display:grid;grid-template-columns:repeat(6,176px);gap:20px}}figure{{margin:0}}object{{display:block;width:176px;height:176px;color:#171614;background:#fff}}figcaption{{padding-top:6px;font-size:11px;color:#2b2723}}
</style></head><body><main>{''.join(cards)}</main></body></html>'''


def readme() -> str:
    return """# Family ↔ Work SVG Suite

This package contains six people in two static forms and both animation directions.

## Structure

Each role directory contains:

- `family.svg` — static family-life form
- `work.svg` — static professional form
- `family-to-work.svg` — one-shot forward transition
- `work-to-family.svg` — one-shot reverse transition

Open `preview.html` in a modern browser to inspect all 24 SVG files and replay either direction. The SVG files are self-contained and use `currentColor`, so their monochrome color can be controlled by the embedding context.

## Roles

- Mother: cooking ↔ office professional
- Father: home repair ↔ site engineer
- Daughter: reading ↔ laboratory scientist
- Son: skateboarding ↔ photographer
- Grandfather: home life ↔ teacher and mentor
- Grandmother: knitting ↔ professional tailor

No family form uses a child as an identity prop.

## Accessibility and motion

Every SVG includes a title, description, and metadata. Animations play for 2400 ms, hold on the destination, and immediately show the destination when `prefers-reduced-motion: reduce` is enabled.

## Attribution

The Working Woman source is Noun Project icon 7641720 by sentya irma and is identified as Creative Commons. The mother artwork is a derivative. Confirm the applicable attribution and license requirements before external distribution.
"""


def generate() -> None:
    (OUTPUT_DIR / "outputs").mkdir(parents=True, exist_ok=True)

    manifest: dict[str, object] = {"suite": "Family ↔ Work", "roles": []}
    for role in ROLES:
        role_dir = OUTPUT_DIR / role.slug
        role_dir.mkdir(exist_ok=True)
        family_root = parse_source(role.family_source)
        defs = source_defs(family_root)
        family = source_art(family_root)
        work = work_art(role, family_root)

        files = {
            "family.svg": static_svg(role, "family", defs, family),
            "work.svg": static_svg(role, "work", defs, work),
            "family-to-work.svg": transition_svg(role, "family", "work", defs, family, work),
            "work-to-family.svg": transition_svg(role, "work", "family", defs, work, family),
        }
        for name, content in files.items():
            (role_dir / name).write_text(content, encoding="utf-8", newline="\n")

        manifest["roles"].append(
            {
                "role": role.slug,
                "family_form": role.family_label,
                "work_form": role.work_label,
                "files": list(files),
            }
        )

    (OUTPUT_DIR / "preview.html").write_text(preview_html(), encoding="utf-8", newline="\n")
    (OUTPUT_DIR / "README.md").write_text(readme(), encoding="utf-8", newline="\n")
    (OUTPUT_DIR / "design_spec.md").write_text(
        (SOURCE_DIR / "design_spec.md").read_text(encoding="utf-8"), encoding="utf-8", newline="\n"
    )
    (OUTPUT_DIR / "Tech-Spec.md").write_text(
        (SOURCE_DIR / "Tech-Spec.md").read_text(encoding="utf-8"), encoding="utf-8", newline="\n"
    )
    (OUTPUT_DIR / "outputs" / "contact-sheet.html").write_text(contact_sheet_html(), encoding="utf-8", newline="\n")
    (OUTPUT_DIR / "outputs" / "motion-sheet.html").write_text(motion_sheet_html(), encoding="utf-8", newline="\n")
    (OUTPUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


if __name__ == "__main__":
    generate()
