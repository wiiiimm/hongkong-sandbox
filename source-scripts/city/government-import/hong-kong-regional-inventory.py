"""Report government-model coverage for Hong Kong outside Lantau Island."""

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from shapely.geometry import Point, Polygon
from shapely.strtree import STRtree

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "source-scripts/city/shared-modelling"))
from db import connect

RUN_ID = "e98f84fdaeb489b229af3910d80d765bb87dbbdc565ec1794836b04909f370ec"
LANTAU_SECTION_IDS = {
    "10.1", "10.2", "10.5", "10.6", "10.7", "10.8", "10.9", "10.10", "10.11",
    "11.6", "11.7",
}
SIZE_ORDER = ("xxl", "xl", "large", "medium", "small", "xs", "unmeasured")
SIZE_LABELS = {
    "xxl": "XXL", "xl": "XL", "large": "L", "medium": "M",
    "small": "S", "xs": "XS", "unmeasured": "Unmeasured",
}
MACRO_REGIONS = {
    "Hong Kong Island": {"01", "02", "03", "04"},
    "Kowloon": {"05", "06", "07", "08", "09"},
    "Airport and non-Lantau Islands": {"10"},
    "Western New Territories": {"11", "12"},
    "Eastern New Territories": {"13", "14", "15"},
    "Northwest and North New Territories": {"16", "17", "18"},
}


def read(path):
    return json.loads(path.read_bytes())


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def selected_sections(path):
    sections = {}
    polygons = []
    polygon_sections = []
    for section in read(path)["sections"]:
        if section["id"] in LANTAU_SECTION_IDS:
            continue
        sections[section["id"]] = {
            "name": section["name"],
            "district": section["district"],
            "districtName": section["districtName"],
        }
        for item in section["polygons"]:
            polygons.append(Polygon(item["rings"][0], item["rings"][1:]))
            polygon_sections.append(section["id"])
    return sections, polygons, polygon_sections


def collect_forms(manifest, sections, polygons, polygon_sections):
    tree = STRtree(polygons)
    forms = []
    embedded = set()
    seen = set()
    territory_total = 0
    for tile in manifest["tiles"]:
        payload = read(ROOT / "3d-viewer" / tile["url"])
        for building in payload["buildings"]:
            territory_total += 1
            uid = building["uid"]
            assert uid not in seen, uid
            seen.add(uid)
            if building.get("modelGeometry"):
                embedded.add(uid)
            centre = Polygon(building["rings"][0], building["rings"][1:]).centroid
            matches = sorted({
                polygon_sections[index]
                for index in tree.query(centre)
                if polygons[index].covers(centre)
            })
            if not matches:
                continue
            assert len(matches) == 1, (uid, matches)
            section_id = matches[0]
            assert section_id in sections
            forms.append((uid, section_id))
    assert territory_total == manifest["counts"]["buildings"] == len(seen)
    return forms, embedded, territory_total


def installed_models(manifest):
    result = {}
    for url in manifest["officialModelCatalogues"]:
        catalogue = read(ROOT / "3d-viewer" / url)
        for model in catalogue["models"]:
            previous = result.get(model["uid"])
            assert not previous or previous["sha256"] == model["sha256"], model["uid"]
            result[model["uid"]] = model
    return result


def size_group_for_triangles(triangles):
    if triangles is None:
        return "unmeasured"
    if triangles < 100:
        return "xs"
    if triangles < 500:
        return "small"
    if triangles < 2000:
        return "medium"
    if triangles < 10000:
        return "large"
    if triangles < 50000:
        return "xl"
    return "xxl"


def size_records(selected_uids):
    selected_uids = set(selected_uids)
    result = {}
    with connect() as connection:
        connection.execute("SET TRANSACTION READ ONLY")
        rows = connection.execute("""
            SELECT viewer_uid,size_group,triangles,model_id,building_csuid,
                   source_state,source_hold_reason,compressed_bytes,geometry_bytes
            FROM astra_modelling.native_model_sizes
            WHERE run_id=%s
            ORDER BY viewer_uid,triangles DESC NULLS LAST,model_id
        """, (RUN_ID,)).fetchall()
    for row in rows:
        uid = row[0]
        if uid not in selected_uids:
            continue
        item = result.setdefault(uid, {
            "componentTriangles": [], "modelIds": [], "buildingCSUIDs": set(),
            "sourceStates": set(), "sourceHoldReasons": set(),
            "componentCompressedBytes": [], "componentGeometryBytes": [],
        })
        item["componentTriangles"].append(row[2])
        item["modelIds"].append(row[3])
        if row[4]:
            item["buildingCSUIDs"].add(row[4])
        if row[5]:
            item["sourceStates"].add(row[5])
        if row[6]:
            item["sourceHoldReasons"].add(row[6])
        item["componentCompressedBytes"].append(row[7])
        item["componentGeometryBytes"].append(row[8])
    for item in result.values():
        triangles = (sum(item["componentTriangles"])
                     if all(value is not None for value in item["componentTriangles"]) else None)
        item.update({
            "componentCount": len(item["modelIds"]),
            "triangles": triangles,
            "sizeGroup": size_group_for_triangles(triangles),
            "compressedBytes": (sum(item["componentCompressedBytes"])
                                if all(value is not None for value in item["componentCompressedBytes"]) else None),
            "geometryBytes": (sum(item["componentGeometryBytes"])
                              if all(value is not None for value in item["componentGeometryBytes"]) else None),
            "buildingCSUIDs": sorted(item["buildingCSUIDs"]),
            "sourceStates": sorted(item["sourceStates"]),
            "sourceHoldReasons": sorted(item["sourceHoldReasons"]),
        })
        for key in ("componentTriangles", "componentCompressedBytes", "componentGeometryBytes"):
            del item[key]
    return result


def empty_counts():
    return {"allForms": 0, "available": Counter(), "installed": Counter()}


def add(counts, size_group, installed):
    counts["allForms"] += 1
    if size_group is None:
        return
    counts["available"][size_group] += 1
    if installed:
        counts["installed"][size_group] += 1


def finish_counts(counts):
    available = sum(counts["available"].values())
    installed = sum(counts["installed"].values())
    return {
        "allForms": counts["allForms"],
        "governmentAvailable": available,
        "installed": installed,
        "enhancementRequired": available - installed,
        "noMatchedGovernmentSource": counts["allForms"] - available,
        "installedPercentOfAvailable": installed / available * 100 if available else None,
        "tiers": [{
            "sizeGroup": group, "label": SIZE_LABELS[group],
            "available": counts["available"][group],
            "installed": counts["installed"][group],
            "enhancementRequired": counts["available"][group] - counts["installed"][group],
        } for group in SIZE_ORDER],
    }


def write_csv(path, rows):
    columns = (
        "id", "name", "allForms", "governmentAvailable", "installed",
        "enhancementRequired", "noMatchedGovernmentSource", "installedPercentOfAvailable",
    )
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def tier_text(tiers):
    return " / ".join(f"{tier['label']} {tier['installed']:,}/{tier['available']:,}" for tier in tiers[:-1])


def write_readme(path, summary):
    lines = [
        "# Hong Kong government-model inventory outside Lantau — current manifest", "",
        "This report excludes every project review section physically on Lantau Island: Tung Chung, "
        "Discovery Bay through Ngong Ping, Sunny Bay and Disneyland. Chek Lap Kok airport and the "
        "non-Lantau islands remain included and are reported separately.", "",
        "Counts are source building forms. Installed means the UID has embedded model geometry or is "
        "present in a manifest-listed official-model catalogue. Complexity is the matched unchanged "
        "government model's triangle bracket; the small number of multi-component matches use the "
        "assembly's summed triangle count.", "",
        "| Region | All forms | Gov available | Installed | Remaining | No gov match | Installed % |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in summary["macroRegions"]:
        lines.append(
            f"| {row['name']} | {row['allForms']:,} | {row['governmentAvailable']:,} | "
            f"{row['installed']:,} | {row['enhancementRequired']:,} | "
            f"{row['noMatchedGovernmentSource']:,} | {row['installedPercentOfAvailable']:.2f}% |"
        )
    total = summary["total"]
    lines.append(
        f"| **Total outside Lantau** | **{total['allForms']:,}** | **{total['governmentAvailable']:,}** | "
        f"**{total['installed']:,}** | **{total['enhancementRequired']:,}** | "
        f"**{total['noMatchedGovernmentSource']:,}** | **{total['installedPercentOfAvailable']:.2f}%** |"
    )
    lines += ["", "## Complexity by broad region", "",
              "Each cell is installed / available.", "",
              "| Region | XXL / XL / L / M / S / XS |", "| --- | --- |"]
    for row in summary["macroRegions"]:
        lines.append(f"| {row['name']} | {tier_text(row['tiers'])} |")
    lines += ["", "## District and special-area totals", "",
              "| District / area | All forms | Gov available | Installed | Remaining | No gov match | Installed % |",
              "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for row in summary["regions"]:
        percent = f"{row['installedPercentOfAvailable']:.2f}%" if row["installedPercentOfAvailable"] is not None else "N/A"
        lines.append(
            f"| {row['name']} | {row['allForms']:,} | {row['governmentAvailable']:,} | "
            f"{row['installed']:,} | {row['enhancementRequired']:,} | "
            f"{row['noMatchedGovernmentSource']:,} | {percent} |"
        )
    lines += ["", "`summary.json` contains tier totals for every broad region, district/special area, "
              "and all included review sections. `regions.csv` and `sections.csv` provide flat tables.", "",
              "This is a read-only inventory. It creates no queue, reservation or database write and "
              "does not edit or generate model geometry. No AI modelling call is involved.", ""]
    path.write_text("\n".join(lines))


def run(output):
    manifest_path = ROOT / "3d-viewer/city/data/manifest.json"
    sections_path = ROOT / "3d-viewer/city/data/review-sections.json"
    manifest = read(manifest_path)
    sections, polygons, polygon_sections = selected_sections(sections_path)
    forms, embedded, territory_total = collect_forms(manifest, sections, polygons, polygon_sections)
    official = installed_models(manifest)
    installed_uids = embedded | set(official)
    sizes = size_records(uid for uid, _ in forms)

    total_counts = empty_counts()
    section_counts = defaultdict(empty_counts)
    region_counts = defaultdict(empty_counts)
    macro_counts = defaultdict(empty_counts)
    for uid, section_id in forms:
        size_group = sizes.get(uid, {}).get("sizeGroup")
        installed = uid in installed_uids
        district = sections[section_id]["district"]
        region_id = "10-airport" if section_id in {"10.3", "10.4"} else "10-islands" if district == "10" else district
        macro = next(name for name, districts in MACRO_REGIONS.items() if district in districts)
        for counts in (total_counts, section_counts[section_id], region_counts[region_id], macro_counts[macro]):
            add(counts, size_group, installed)

    section_rows = []
    for section_id in sorted(sections, key=lambda value: tuple(map(int, value.split(".")))):
        section_rows.append({
            "id": section_id, "name": sections[section_id]["name"],
            "district": sections[section_id]["district"],
            "districtName": sections[section_id]["districtName"],
            **finish_counts(section_counts[section_id]),
        })
    region_rows = []
    region_ids = [f"{number:02d}" for number in range(1, 10)] + ["10-airport", "10-islands"] + [f"{number:02d}" for number in range(11, 19)]
    for region_id in region_ids:
        if region_id == "10-airport":
            name = "Chek Lap Kok airport and boundary-crossing facilities"
        elif region_id == "10-islands":
            name = "Non-Lantau Islands District islands"
        else:
            name = next(section["districtName"] for section in sections.values() if section["district"] == region_id)
        region_rows.append({"id": region_id, "name": name, **finish_counts(region_counts[region_id])})
    macro_rows = [{"id": str(index + 1), "name": name, **finish_counts(macro_counts[name])}
                  for index, name in enumerate(MACRO_REGIONS)]
    summary = {
        "schemaVersion": 1,
        "scope": {
            "includedSectionIds": sorted(sections, key=lambda value: tuple(map(int, value.split(".")))),
            "excludedLantauSectionIds": sorted(LANTAU_SECTION_IDS, key=lambda value: tuple(map(int, value.split(".")))),
            "airportIncluded": True,
            "nonLantauIslandsIncluded": True,
        },
        "territoryFormsVerified": territory_total,
        "total": finish_counts(total_counts),
        "macroRegions": macro_rows,
        "regions": region_rows,
        "sections": section_rows,
        "governmentSizeRun": RUN_ID,
        "multiComponentMatchedForms": sum(value["componentCount"] > 1 for value in sizes.values()),
        "inputs": {
            str(manifest_path.relative_to(ROOT)): sha256(manifest_path),
            str(sections_path.relative_to(ROOT)): sha256(sections_path),
        },
        "installedDefinition": "UID present in embedded modelGeometry or a manifest-listed official model catalogue",
        "enhancementRequiredDefinition": "Matched government source UID exists and is not installed",
        "aiCalls": 0, "databaseWrites": 0, "queuesCreated": 0, "geometryChanges": 0,
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    write_csv(output / "regions.csv", region_rows)
    write_csv(output / "sections.csv", section_rows)
    write_readme(output / "README.md", summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "docs/astra-city/hong-kong-regional-government-model-inventory-20260923")
    args = parser.parse_args()
    summary = run(args.output)
    print(json.dumps({"total": summary["total"], "macroRegions": summary["macroRegions"]}, indent=2))


if __name__ == "__main__":
    main()
