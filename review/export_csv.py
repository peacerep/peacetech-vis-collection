"""
Exports metadata/visualisations.json to a flat CSV for sharing outside this repo.

One row per visualisation: Title, Summary, Datasets, Contributors, Link
(Link = public_link if the record has one, else embed_link).

Run:
    python3 review/export_csv.py
"""
import json, csv, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load(name):
    with open(os.path.join(ROOT, "metadata", name), encoding="utf-8") as f:
        return json.load(f)

vis = load("visualisations.json")["visualisations"]
people_by_id = {p["id"]: p for p in load("people.json")["people"]}
orgs_by_id = {o["id"]: o for o in load("organisations.json")["organisations"]}
datasets_by_id = {d["id"]: d for d in load("datasets.json")["datasets"]}

def dataset_names(v):
    names = []
    for d in v["data_coverage"]["datasets"]:
        ds = datasets_by_id.get(d["dataset_id"])
        names.append(ds.get("short_name") or ds["name"] if ds else d["dataset_id"])
    return "; ".join(names)

def contributor_names(v):
    names = []
    for c in v["contributors"]:
        pool = people_by_id if c["entity_type"] == "person" else orgs_by_id
        entity = pool.get(c["entity_id"])
        if not entity:
            names.append(c["entity_id"])
        elif c["entity_type"] == "person":
            names.append(entity["display_name"])
        else:
            names.append(entity.get("name") or entity.get("short_name") or entity["id"])
    return "; ".join(names)

def link(v):
    by_type = {l["type"]: l["url"] for l in v["links"]}
    return by_type.get("public_link") or by_type.get("embed_link") or ""

rows = [
    [
        v["title"],
        v["description"].get("summary", ""),
        dataset_names(v),
        contributor_names(v),
        link(v),
    ]
    for v in vis
]

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "visualisations_export.csv")
with open(out_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Title", "Summary", "Datasets", "Contributors", "Link"])
    writer.writerows(rows)

print(f"written {out_path} ({len(rows)} rows)")
