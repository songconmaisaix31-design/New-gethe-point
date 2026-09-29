from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path


SUITE_DIR = Path(__file__).resolve().parent.parent / "family-work-suite"
ROLES = ("mother", "father", "daughter", "son", "grandfather", "grandmother")
SVG_FILES = ("family.svg", "work.svg", "family-to-work.svg", "work-to-family.svg")
FORBIDDEN_ELEMENTS = {"script", "image", "foreignObject"}


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def find_by_attribute(root: ET.Element, attribute: str, value: str) -> ET.Element:
    for element in root.iter():
        if element.get(attribute) == value:
            return element
    raise AssertionError(f"Missing element with {attribute}={value!r}")


def inner_xml(element: ET.Element) -> tuple[bytes, ...]:
    return tuple(ET.tostring(child, encoding="utf-8") for child in element)


def parse_svg(path: Path) -> ET.Element:
    root = ET.parse(path).getroot()
    assert local_name(root.tag) == "svg", path
    assert root.get("viewBox") == "0 0 512 512", path
    child_names = {local_name(child.tag) for child in root}
    assert {"title", "desc", "metadata"} <= child_names, path

    for element in root.iter():
        assert local_name(element.tag) not in FORBIDDEN_ELEMENTS, path
        for attribute, value in element.attrib.items():
            if local_name(attribute) == "href":
                assert value.startswith("#"), (path, value)
    return root


def verify_role(role: str) -> dict[str, object]:
    role_dir = SUITE_DIR / role
    roots = {name: parse_svg(role_dir / name) for name in SVG_FILES}

    family_art = inner_xml(find_by_attribute(roots["family.svg"], "id", "state-art"))
    work_art = inner_xml(find_by_attribute(roots["work.svg"], "id", "state-art"))

    forward_source = inner_xml(find_by_attribute(roots["family-to-work.svg"], "class", "source"))
    forward_destination = inner_xml(find_by_attribute(roots["family-to-work.svg"], "class", "destination"))
    reverse_source = inner_xml(find_by_attribute(roots["work-to-family.svg"], "class", "source"))
    reverse_destination = inner_xml(find_by_attribute(roots["work-to-family.svg"], "class", "destination"))

    assert family_art == forward_source == reverse_destination, role
    assert work_art == forward_destination == reverse_source, role

    for name in ("family-to-work.svg", "work-to-family.svg"):
        text = (role_dir / name).read_text(encoding="utf-8")
        assert "prefers-reduced-motion: reduce" in text, (role, name)
        assert "animation-fill-mode" not in text
        assert "forwards" in text, (role, name)
        assert "@keyframes reveal" in text, (role, name)

    return {
        "role": role,
        "files": len(SVG_FILES),
        "endpoint_markup_exact": True,
        "reduced_motion": True,
        "external_resources": False,
    }


def main() -> None:
    expected = {SUITE_DIR / role / name for role in ROLES for name in SVG_FILES}
    actual = set(SUITE_DIR.glob("*/*.svg"))
    assert actual == expected, sorted(str(path) for path in actual ^ expected)

    results = [verify_role(role) for role in ROLES]
    layout_path = SUITE_DIR / "outputs" / "layout-metrics.json"
    layout = json.loads(layout_path.read_text(encoding="utf-8-sig")) if layout_path.exists() else None
    if layout is not None:
        assert layout["viewportWidth"] == 390, layout
        assert layout["scrollWidth"] == 390, layout
        assert layout["horizontalOverflow"] is False, layout

    visual_files = (
        "contact-sheet-128.png",
        "motion-midpoint.png",
        "preview-desktop.png",
        "preview-mobile-390.png",
    )
    visual_evidence = all((SUITE_DIR / "outputs" / name).is_file() for name in visual_files)
    report = {
        "status": "passed",
        "svg_count": len(actual),
        "role_count": len(ROLES),
        "checks": {
            "xml_and_accessibility": "passed",
            "self_contained_vector_only": "passed",
            "bidirectional_endpoints": "passed",
            "reduced_motion": "passed",
            "responsive_390px": "passed" if layout is not None else "not_run",
            "visual_evidence": "passed" if visual_evidence else "not_run",
        },
        "roles": results,
    }
    output = SUITE_DIR / "outputs" / "qa-report.json"
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
