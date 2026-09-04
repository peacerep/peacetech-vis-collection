"""
Regenerates review/index.html from metadata/*.json.
Local-only dataset checker — no external upload, no embedded images
(index.html references ../mini-fig/*.png by relative path, so it must
stay inside the review/ folder and be opened from the local filesystem).

Every schema field is rendered as a table column, including empty ones
(shown as "—"), so gaps in the metadata are visible rather than hidden.

Run after any batch of edits to metadata/*.json:
    python3 review/build_review.py
"""
import json, html, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DASH = "—"

def load(name):
    with open(os.path.join(ROOT, "metadata", name), encoding="utf-8") as f:
        return json.load(f)

vis = load("visualisations.json")["visualisations"]
people = load("people.json")["people"]
orgs = load("organisations.json")["organisations"]
datasets = load("datasets.json")["datasets"]
tools = load("tools.json")["tools"]
vocab = load("vocabularies.json")

people_by_id = {p["id"]: p for p in people}
orgs_by_id = {o["id"]: o for o in orgs}
datasets_by_id = {d["id"]: d for d in datasets}
tools_by_id = {t["id"]: t for t in tools}
versions_by_id = {(d["id"], v["id"]): v for d in datasets for v in d["versions"]}
link_type_label = {l["id"]: l["label"] for l in vocab["link_types"]}
dim_label = {d["id"]: d["label"] for d in vocab["dimensions"]}
vt_label = {v["id"]: v["label"] for v in vocab["visualisation_types"]}
status_label = {s["id"]: s["label"] for s in vocab["status"]}
role_label = {r["id"]: r["label"] for r in vocab["contributor_roles"]}
STATUS_MUTED = {"excluded", "deprecated", "outdated"}

def status_pill(s):
    if not s:
        return f'<span class="dash">{DASH}</span>'
    cls = "status-muted" if s in STATUS_MUTED else ""
    return f'<span class="status-pill {cls}">{esc(status_label.get(s, s))}</span>'

def esc(s):
    return html.escape(str(s), quote=True)

def val(x):
    if x is None or x == "":
        return f'<span class="dash">{DASH}</span>'
    return esc(x)

def list_val(items):
    if not items:
        return f'<span class="dash">{DASH}</span>'
    return ", ".join(esc(i) for i in items)

def td(value_html):
    return f'<td>{value_html}</td>'

def table(headers, row_htmls):
    thead = "".join(f"<th>{esc(h)}</th>" for h in headers)
    body = "".join(row_htmls) or f'<tr><td colspan="{len(headers)}" class="empty">none</td></tr>'
    return f'<div class="table-wrap"><table><thead><tr>{thead}</tr></thead><tbody>{body}</tbody></table></div>'

def tool_names(v):
    names = []
    for t in v["tools"]:
        tid = t.get("tool_id", "")
        tool = tools_by_id.get(tid)
        names.append(tool["name"] if tool else f'missing tool: {tid}')
    return names

def org_name(oid):
    o = orgs_by_id.get(oid)
    if not o:
        return f'<span class="flag">missing org: {esc(oid)}</span>'
    return o.get("short_name") or o.get("name") or oid

def contributor_name(c):
    """Resolve a contributor's display name (escaped HTML), handling both people and organisations."""
    pool = people_by_id if c["entity_type"] == "person" else orgs_by_id
    entity = pool.get(c["entity_id"])
    if not entity:
        return f'<span class="flag">missing {esc(c["entity_type"])}: {esc(c["entity_id"])}</span>'
    name = entity["display_name"] if c["entity_type"] == "person" else (entity.get("name") or entity.get("short_name") or entity["id"])
    return esc(name)

def dataset_line(dref, show_note=True):
    d = datasets_by_id.get(dref["dataset_id"])
    if not d:
        return f'<li><span class="flag">missing dataset: {esc(dref["dataset_id"])}</span></li>'
    uncertain = "UNCERTAIN" in (d.get("notes") or "")
    name = d.get("short_name") or d["name"]
    version = ""
    if dref.get("version_id"):
        v = versions_by_id.get((dref["dataset_id"], dref["version_id"]))
        version = f' <code>{esc(v["label"])}</code>' if v else f' <span class="flag">unknown version {esc(dref["version_id"])}</span>'
    note = f' <span class="dim">— {esc(dref["usage_note"])}</span>' if show_note and dref.get("usage_note") else ""
    mark = ' <span class="flag">⚠</span>' if uncertain else ""
    return f'<li>{esc(name)}{version}{mark}{note}</li>'

def dimension_line(d):
    label = dim_label.get(d["id"], d["id"])
    covered = "covered" if d.get("is_covered") else "not covered"
    desc = f' <span class="dim">— {esc(d["description"])}</span>' if d.get("description") else ""
    return f'<li>{esc(label)} <span class="dim">({covered})</span>{desc}</li>'

def contributor_line(c):
    kind = "" if c["entity_type"] == "person" else ' <span class="tag-type">org</span>'
    return f'<li>{contributor_name(c)}{kind}</li>'

def link_line(l):
    kind = link_type_label.get(l["type"], l["type"])
    label = f' <span class="dim">({esc(l["label"])})</span>' if l.get("label") else ""
    return f'<li><span class="tag-type">{esc(kind)}</span> <a href="{esc(l["url"])}" target="_blank" rel="noopener">{esc(l["url"])}</a>{label}</li>'

def view_component_line(vc):
    types = list_val(vc.get("visualisation_types", []))
    desc = vc.get("description") or DASH
    return f'<li><strong>{esc(vc["name"])}</strong> <span class="dim">({esc(vc["kind"])}, types: {types})</span> — {esc(desc) if desc != DASH else DASH}</li>'

def view_component_name_line(vc):
    return f'<li>{esc(vc["name"])}</li>'

def ul(items_html):
    return f'<ul class="tight">{"".join(items_html)}</ul>' if items_html else f'<span class="dash">{DASH}</span>'

def is_flagged(v):
    return bool(v.get("notes")) or any(
        "UNCERTAIN" in (datasets_by_id.get(d["dataset_id"], {}).get("notes", "") or "")
        for d in v["data_coverage"]["datasets"]
    )

# Computed once and reused by the table + both grid views below, rather than
# re-running is_flagged() for every visualisation in each view.
flagged_by_id = {v["id"]: is_flagged(v) for v in vis}

# ---------------- Visualisations: filtering table ----------------
# Thumb/Title/Links/Notes always show; every other column starts hidden
# and can be switched on/off via the column-toggle checkboxes.
TABLE_COLUMNS = [
    ("thumb", "Thumb", True),
    ("title", "Title", True),
    ("status", "Status", False),
    ("datasets", "Datasets", False),
    ("dimensions", "Dimensions", False),
    ("contributors", "Contributors", False),
    ("tools", "Tools", False),
    ("links", "Links", True),
    ("vis_types", "Vis Types", False),
    ("views_components", "Views/Components", False),
    ("alt_text", "Alt Text", False),
    ("credit", "Credit", False),
    ("created", "Created", False),
    ("updated", "Updated", False),
    ("notes", "Notes", True),
]
TOGGLE_COLUMNS = [(k, l) for k, l, a in TABLE_COLUMNS if not a]

def col_cell(tag, key, content_html, always):
    """<th>/<td> for a filtering-table column: hidden by default unless `always`."""
    style = "" if always else ' style="display:none"'
    return f'<{tag} data-col="{key}"{style}>{content_html}</{tag}>'

table_thead_html = "".join(col_cell("th", k, esc(l), a) for k, l, a in TABLE_COLUMNS)

table_rows = []
flagged_n = sum(flagged_by_id.values())
for v in vis:
    flagged = flagged_by_id[v["id"]]
    thumb_src = f'../mini-fig/{v["thumbnail"]["url"]}' if v["thumbnail"].get("url") else None
    thumb_html = f'<img class="thumb thumb-sm" src="{esc(thumb_src)}" loading="lazy">' if thumb_src else f'<div class="thumb thumb-sm thumb-empty">{DASH}</div>'
    title_cell = f'<div class="cell-title">{esc(v["title"])}</div><div class="cell-id"><code>{esc(v["id"])}</code></div>'
    col_values = {
        "thumb": thumb_html,
        "title": title_cell,
        "status": status_pill(v.get("status")),
        "datasets": ul([dataset_line(d) for d in v["data_coverage"]["datasets"]]),
        "dimensions": ul([dimension_line(d) for d in v["data_coverage"]["dimensions"]]),
        "contributors": ul([contributor_line(c) for c in v["contributors"]]),
        "tools": list_val(tool_names(v)),
        "links": ul([link_line(l) for l in v["links"]]),
        "vis_types": list_val([vt_label.get(t, t) for t in v["content"]["visualisation_types"]]),
        "views_components": ul([view_component_line(c) for c in v["content"]["views_components"]]),
        "alt_text": val(v["thumbnail"].get("alt_text")),
        "credit": val(v["thumbnail"].get("credit")),
        "created": val(v["timestamps"]["created_at"]),
        "updated": val(v["timestamps"]["updated_at"]),
        "notes": val(v.get("notes")),
    }
    tds = "".join(col_cell("td", k, col_values[k], a) for k, _, a in TABLE_COLUMNS)
    table_rows.append(f'<tr class="vitem {"row-flagged" if flagged else ""}" data-flagged="{"1" if flagged else "0"}">{tds}</tr>')

table_body_html = "".join(table_rows) or f'<tr><td colspan="{len(TABLE_COLUMNS)}" class="empty">none</td></tr>'
col_toggles_html = "".join(
    f'<label class="col-toggle-label"><input type="checkbox" class="col-toggle" data-col="{k}"> {esc(l)}</label>'
    for k, l in TOGGLE_COLUMNS
)

# ---------------- Visualisations: grid views (cards) ----------------
# Two variants share this builder: the full grid, and a compact grid that
# drops Alt Text, drops dataset usage notes, and lists Views/Components by
# name only (see `compact` branches below).
def gfield(label, value_html):
    return f'<div class="gf"><div class="gfl">{esc(label)}</div><div class="gfv">{value_html}</div></div>'

def build_grid_cards(compact):
    cards = []
    for v in vis:
        flagged = flagged_by_id[v["id"]]
        thumb_src = f'../mini-fig/{v["thumbnail"]["url"]}' if v["thumbnail"].get("url") else None
        thumb_html = f'<img class="thumb" src="{esc(thumb_src)}" loading="lazy">' if thumb_src else f'<div class="thumb thumb-empty">{DASH}</div>'
        fields = [
            gfield("ID", f'<code>{esc(v["id"])}</code>'),
            gfield("Status", status_pill(v.get("status"))),
            gfield("Summary", val(v["description"]["summary"])),
            gfield("Keywords", list_val(v["description"]["keywords"])),
            gfield("Research Qs", list_val(v["description"]["research_questions"])),
            gfield("Audiences", list_val(v["description"]["audiences"])),
            gfield("Datasets", ul([dataset_line(d, show_note=not compact) for d in v["data_coverage"]["datasets"]])),
            gfield("Dimensions", ul([dimension_line(d) for d in v["data_coverage"]["dimensions"]])),
            gfield("Contributors", ul([contributor_line(c) for c in v["contributors"]])),
            gfield("Tools", list_val(tool_names(v))),
            gfield("Links", ul([link_line(l) for l in v["links"]])),
            gfield("Vis Types", list_val([vt_label.get(t, t) for t in v["content"]["visualisation_types"]])),
            gfield("Views/Components", ul([
                (view_component_name_line if compact else view_component_line)(c)
                for c in v["content"]["views_components"]
            ])),
        ]
        if not compact:
            fields.append(gfield("Alt Text", val(v["thumbnail"].get("alt_text"))))
        fields += [
            gfield("Credit", val(v["thumbnail"].get("credit"))),
            gfield("Created", val(v["timestamps"]["created_at"])),
            gfield("Updated", val(v["timestamps"]["updated_at"])),
            gfield("Notes", val(v.get("notes"))),
        ]
        cards.append(f'''
        <article class="gridcard vitem {"row-flagged" if flagged else ""}" data-flagged="{"1" if flagged else "0"}">
          {thumb_html}
          <div class="gridcard-body">
            <h3>{esc(v["title"])}</h3>
            {"".join(fields)}
          </div>
        </article>''')
    return cards

grid_cards = build_grid_cards(compact=False)
grid_compact_cards = build_grid_cards(compact=True)

vis_section = f'''
<div class="vis-toolbar">
  <p class="stats">{len(vis)} of 37 data.csv rows populated (row 33 intentionally excluded) &nbsp;·&nbsp; <span class="flag">{flagged_n} flagged</span></p>
  <div class="vis-controls">
    <div class="seg" id="view-toggle">
      <button type="button" class="active" data-view="table">Table</button>
      <button type="button" data-view="grid">Grid</button>
      <button type="button" data-view="grid-compact">Grid (compact)</button>
    </div>
    <button type="button" id="flagged-toggle" class="pill-toggle">Flagged only</button>
  </div>
</div>
<div id="vis-table">
  <div class="col-toggles">{col_toggles_html}</div>
  <div class="table-wrap"><table id="vis-table-el"><thead><tr>{table_thead_html}</tr></thead><tbody>{table_body_html}</tbody></table></div>
</div>
<div id="vis-grid" class="cardgrid-multi" style="display:none">{"".join(grid_cards)}</div>
<div id="vis-grid-compact" class="cardgrid-multi" style="display:none">{"".join(grid_compact_cards)}</div>'''

# ---------------- People ----------------
PEOPLE_HEADERS = ["Name", "ID", "Given", "Family", "Affiliation", "Roles", "Partner", "Notes"]
people_rows = []
for p in people:
    affs = ", ".join(org_name(a) for a in p.get("affiliation_ids", [])) or DASH
    roles = list_val([role_label.get(r, r) for r in p.get("roles", [])])
    cells = [
        f'<strong>{esc(p["display_name"])}</strong>',
        f'<code>{esc(p["id"])}</code>',
        val(p.get("given_name")),
        val(p.get("family_name")),
        esc(affs) if affs != DASH else f'<span class="dash">{DASH}</span>',
        roles,
        "yes" if p.get("is_collaboration_partner") else "no",
        val(p.get("notes")),
    ]
    people_rows.append(f'<tr>{"".join(td(c) for c in cells)}</tr>')
people_section = table(PEOPLE_HEADERS, people_rows)

# ---------------- Organisations ----------------
ORG_HEADERS = ["Name", "ID", "Short", "Type", "URL", "Country", "Partner", "Notes"]
org_rows = []
for o in orgs:
    name_html = val(o.get("name")) if o.get("name") else '<span class="flag">unconfirmed</span>'
    cells = [
        f'<strong>{name_html}</strong>',
        f'<code>{esc(o["id"])}</code>',
        val(o.get("short_name")),
        val(o.get("type")),
        val(o.get("url")),
        val(o.get("country")),
        "yes" if o.get("is_collaboration_partner") else "no",
        val(o.get("notes")),
    ]
    org_rows.append(f'<tr>{"".join(td(c) for c in cells)}</tr>')
orgs_section = table(ORG_HEADERS, org_rows)

# ---------------- Datasets ----------------
DATASET_HEADERS = ["Name", "ID", "Short", "Description", "Publisher", "Source URL", "Licence", "Citation", "Versions", "Fields", "Notes"]
ds_rows = []
for d in datasets:
    uncertain = "UNCERTAIN" in (d.get("notes") or "")
    version_items = [f'<li><code>{esc(v["label"])}</code> <span class="dim">release: {val(v.get("release_date"))} · accessed: {val(v.get("accessed_at"))} · {val(v.get("notes"))}</span></li>' for v in d["versions"]]
    field_items = [f'<li>{esc(fl["name"])} <span class="dim">({val(fl.get("data_type"))})</span></li>' for fl in d["fields"]]
    cells = [
        f'<strong>{esc(d["name"])}</strong>',
        f'<code>{esc(d["id"])}</code>',
        val(d.get("short_name")),
        val(d.get("description")),
        val(d.get("publisher_organisation_id")),
        val(d.get("source_url")),
        val(d.get("licence")),
        val(d.get("citation")),
        ul(version_items),
        ul(field_items),
        val(d.get("notes")),
    ]
    ds_rows.append(f'<tr class="{"row-flagged" if uncertain else ""}">{"".join(td(c) for c in cells)}</tr>')
datasets_section = table(DATASET_HEADERS, ds_rows)

# ---------------- Tools ----------------
TOOL_HEADERS = ["Name", "ID", "Type", "Description", "Website", "Notes"]
real_tools = [t for t in tools if t["id"] != "tool_example"]
if real_tools:
    tool_rows = []
    for t in real_tools:
        cells = [
            f'<strong>{esc(t["name"])}</strong>',
            f'<code>{esc(t["id"])}</code>',
            val(t.get("type")),
            val(t.get("description")),
            val(t.get("website")),
            val(t.get("notes")),
        ]
        tool_rows.append(f'<tr>{"".join(td(c) for c in cells)}</tr>')
    tools_section = table(TOOL_HEADERS, tool_rows)
else:
    tools_section = '<p class="empty">tools.json not yet populated (Phase 2 task 4).</p>'

# ---------------- Vocabularies ----------------
vocab_html = ""
for key in ["dimensions", "audiences", "contributor_roles", "visualisation_types", "link_types", "status"]:
    items = ", ".join(esc(i["label"]) for i in vocab.get(key, []))
    vocab_html += f'<p><strong>{esc(key.replace("_", " "))}:</strong> {items or DASH}</p>'

HTML = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>peacerep-collection — dataset checker</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  :root{{ --bg:#fff; --card:#fbfbfa; --text:#1a1a1a; --muted:#6b6b6b; --border:#e0e0dd; --accent:#b5401f; --accent-bg:#fbeee8; }}
  @media (prefers-color-scheme: dark){{
    :root{{ --bg:#17181a; --card:#1f2123; --text:#e8e8e6; --muted:#9a9a97; --border:#34363a; --accent:#e2895f; --accent-bg:#3a2620; }}
  }}
  *{{ box-sizing:border-box; }}
  body{{ font-family:-apple-system,Segoe UI,system-ui,sans-serif; background:var(--bg); color:var(--text); margin:0; padding:22px 30px 80px; font-size:14px; }}
  h1{{ font-size:19px; margin:0 0 4px; }}
  .sub{{ color:var(--muted); font-size:12.5px; margin:0 0 18px; }}
  nav{{ display:flex; gap:2px; border-bottom:1px solid var(--border); margin-bottom:18px; flex-wrap:wrap; }}
  nav button{{ background:none; border:none; padding:8px 13px; font-size:13.5px; color:var(--muted); cursor:pointer; border-bottom:2px solid transparent; }}
  nav button.active{{ color:var(--text); border-bottom-color:var(--accent); font-weight:600; }}
  section{{ display:none; }}
  section.active{{ display:block; }}
  .stats{{ color:var(--muted); font-size:13px; margin:0; }}
  .vis-toolbar{{ display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom:12px; flex-wrap:wrap; }}
  .vis-controls{{ display:flex; align-items:center; gap:8px; }}
  .seg{{ display:inline-flex; border:1px solid var(--border); border-radius:6px; overflow:hidden; }}
  .seg button{{ background:var(--card); border:none; padding:5px 12px; font-size:12.5px; color:var(--muted); cursor:pointer; }}
  .seg button + button{{ border-left:1px solid var(--border); }}
  .seg button.active{{ background:var(--accent-bg); color:var(--accent); font-weight:600; }}
  .pill-toggle{{ font-size:12.5px; color:var(--muted); background:var(--card); border:1px solid var(--border); border-radius:6px; padding:5px 12px; cursor:pointer; }}
  .pill-toggle.active{{ background:var(--accent-bg); color:var(--accent); border-color:var(--accent); font-weight:600; }}
  .table-wrap{{ overflow-x:auto; border:1px solid var(--border); border-radius:8px; }}
  table{{ border-collapse:collapse; width:100%; font-size:12.5px; }}
  th, td{{ text-align:left; padding:7px 10px; border-bottom:1px solid var(--border); vertical-align:top; white-space:normal; }}
  th{{ position:sticky; top:0; background:var(--card); color:var(--muted); font-size:10.5px; text-transform:uppercase; letter-spacing:.03em; white-space:nowrap; z-index:1; }}
  #vis-table-el{{ table-layout:fixed; }}
  #vis-table-el th{{ white-space:normal; }}
  #vis-table-el th, #vis-table-el td{{ overflow-wrap:anywhere; }}
  #vis-table-el th[data-col="thumb"], #vis-table-el td[data-col="thumb"]{{ width:70px; }}
  #vis-table-el th[data-col="title"], #vis-table-el td[data-col="title"]{{ width:220px; }}
  tbody tr:last-child td{{ border-bottom:none; }}
  tbody tr:hover{{ background:var(--accent-bg); }}
  tr.row-flagged td:first-child{{ box-shadow: inset 3px 0 0 var(--accent); }}
  .thumb{{ width:80px; height:52px; object-fit:cover; border-radius:4px; display:block; }}
  .thumb-sm{{ width:52px; height:34px; }}
  .thumb-empty{{ display:flex; align-items:center; justify-content:center; color:var(--muted); background:var(--border); font-size:11px; }}
  .dash{{ color:var(--muted); }}
  .dim{{ color:var(--muted); }}
  .cell-title{{ font-weight:600; }}
  .cell-id{{ font-size:11px; color:var(--muted); margin-top:2px; }}
  .cell-id code{{ background:none; padding:0; }}
  .desc-summary{{ margin-bottom:4px; }}
  .desc-sub{{ font-size:11.5px; color:var(--muted); margin-top:2px; }}
  ul.tight{{ margin:0; padding-left:14px; }}
  ul.tight li{{ margin-bottom:2px; }}
  .tag-type{{ font-size:10px; text-transform:uppercase; background:var(--accent-bg); color:var(--accent); padding:1px 5px; border-radius:3px; }}
  .status-pill{{ font-size:10.5px; text-transform:uppercase; letter-spacing:.02em; background:var(--border); color:var(--text); padding:2px 7px; border-radius:99px; white-space:nowrap; }}
  .status-pill.status-muted{{ background:var(--accent-bg); color:var(--accent); }}
  .flag{{ color:var(--accent); font-weight:600; }}
  .empty{{ color:var(--muted); font-style:italic; }}
  code{{ font-size:12px; background:var(--border); padding:0 4px; border-radius:3px; }}
  a{{ color:inherit; }}
  .vitem[data-hidden-by-filter="1"]{{ display:none; }}
  .col-toggles{{ display:flex; flex-wrap:wrap; gap:5px 14px; margin-bottom:10px; font-size:12px; color:var(--muted); }}
  .col-toggle-label{{ display:inline-flex; align-items:center; gap:5px; cursor:pointer; user-select:none; }}
  .col-toggle-label input{{ cursor:pointer; }}
  .cardgrid-multi{{ display:grid; grid-template-columns:repeat(4, 1fr); gap:14px; align-items:start; }}
  @media (max-width:1400px){{ .cardgrid-multi{{ grid-template-columns:repeat(3, 1fr); }} }}
  @media (max-width:1000px){{ .cardgrid-multi{{ grid-template-columns:repeat(2, 1fr); }} }}
  @media (max-width:640px){{ .cardgrid-multi{{ grid-template-columns:1fr; }} }}
  .gridcard{{ background:var(--card); border:1px solid var(--border); border-radius:8px; overflow:hidden; }}
  .gridcard.row-flagged{{ border-color:var(--accent); }}
  .gridcard .thumb{{ width:100%; height:140px; border-radius:0; }}
  .gridcard-body{{ padding:12px 14px 14px; }}
  .gridcard-body h3{{ font-size:14px; margin:0 0 8px; }}
  .gf{{ display:grid; grid-template-columns:104px 1fr; gap:6px; padding:3px 0; border-top:1px solid var(--border); font-size:12px; }}
  .gf:first-of-type{{ border-top:none; }}
  .gfl{{ color:var(--muted); text-transform:uppercase; font-size:10px; letter-spacing:.03em; padding-top:1px; }}
  .gfv{{ line-height:1.45; word-break:break-word; }}
</style>
</head>
<body>
<h1>peacerep-collection — dataset checker</h1>
<p class="sub">Local-only, every field shown (blank = {DASH}). Regenerate with <code>python3 review/build_review.py</code> after editing metadata/*.json.</p>
<nav>
  <button class="active" data-t="vis">Visualisations</button>
  <button data-t="people">People</button>
  <button data-t="orgs">Organisations</button>
  <button data-t="datasets">Datasets</button>
  <button data-t="tools">Tools</button>
  <button data-t="vocab">Vocabularies</button>
</nav>
<section id="vis" class="active">{vis_section}</section>
<section id="people">{people_section}</section>
<section id="orgs">{orgs_section}</section>
<section id="datasets">{datasets_section}</section>
<section id="tools">{tools_section}</section>
<section id="vocab">{vocab_html}</section>
<script>
document.querySelectorAll('nav button').forEach(b=>{{
  b.addEventListener('click', ()=>{{
    document.querySelectorAll('nav button').forEach(x=>x.classList.remove('active'));
    document.querySelectorAll('section').forEach(x=>x.classList.remove('active'));
    b.classList.add('active');
    document.getElementById(b.dataset.t).classList.add('active');
  }});
}});

(function(){{
  var viewEls = {{ table: document.getElementById('vis-table'), grid: document.getElementById('vis-grid'), 'grid-compact': document.getElementById('vis-grid-compact') }};
  var viewButtons = document.querySelectorAll('#view-toggle button');
  var flaggedBtn = document.getElementById('flagged-toggle');
  var flaggedOnly = false;

  viewButtons.forEach(function(b){{
    b.addEventListener('click', function(){{
      viewButtons.forEach(function(x){{ x.classList.remove('active'); }});
      b.classList.add('active');
      Object.keys(viewEls).forEach(function(key){{
        viewEls[key].style.display = (key === b.dataset.view) ? '' : 'none';
      }});
    }});
  }});

  flaggedBtn.addEventListener('click', function(){{
    flaggedOnly = !flaggedOnly;
    flaggedBtn.classList.toggle('active', flaggedOnly);
    document.querySelectorAll('.vitem').forEach(function(el){{
      var hide = flaggedOnly && el.dataset.flagged !== '1';
      el.setAttribute('data-hidden-by-filter', hide ? '1' : '0');
    }});
  }});

  document.querySelectorAll('.col-toggle').forEach(function(cb){{
    cb.addEventListener('change', function(){{
      var key = cb.dataset.col;
      var show = cb.checked;
      document.querySelectorAll('#vis-table-el [data-col="' + key + '"]').forEach(function(el){{
        el.style.display = show ? '' : 'none';
      }});
    }});
  }});
}})();
</script>
</body>
</html>'''

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(HTML)
print("written", out_path)
