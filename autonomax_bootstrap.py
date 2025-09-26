#!/usr/bin/env python3
import csv, json, argparse, os, pathlib, shutil
from typing import List

def read_csv(csv_path: str):
    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            row = { (k or "").lower().strip(): (v or "") for k, v in r.items() }
            rows.append(row)
    return rows

def parse_paths(cell: str) -> List[str]:
    if not cell:
        return []
    parts = [p.strip() for p in cell.split("|")]
    return [p for p in parts if p]

def ensure_symlink(target: str, link_path: str):
    try:
        if os.path.islink(link_path) or os.path.exists(link_path):
            try:
                os.remove(link_path)
            except IsADirectoryError:
                shutil.rmtree(link_path)
        os.symlink(target, link_path)
        return True, ""
    except Exception as e:
        return False, str(e)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, help="Path to Master Index CSV (found or original)")
    ap.add_argument("--project-root", required=True, help="Repo root (current project)")
    ap.add_argument("--no-symlinks", action="store_true", help="Do not create _staging symlinks")
    args = ap.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()
    work_dir = project_root / "_autonomax"
    staging_dir = project_root / "_staging"
    work_dir.mkdir(parents=True, exist_ok=True)
    staging_dir.mkdir(parents=True, exist_ok=True)

    rows = read_csv(args.csv)

    manifest = {"project_root": str(project_root), "entries": []}

    for raw in rows:
        filename = (
            raw.get("filename")
            or raw.get("file")
            or raw.get("name")
            or raw.get("filename / folder")
            or raw.get("filename/folder")
            or ""
        ).strip()

        found = (raw.get("found") or "").strip().lower()
        paths_cell = (raw.get("paths") or raw.get("path") or "").strip()
        probable = (raw.get("probable local path") or raw.get("probable_path") or "").strip()

        candidate_paths = parse_paths(paths_cell)

        entry = {
            "filename": filename,
            "found": found if found in ("yes", "no") else ("yes" if candidate_paths else "unknown"),
            "candidate_paths": candidate_paths,
            "probable_path_hint": probable,
            "chosen_path": None,
            "in_repo": False,
            "symlink": None,
        }

        rel_candidate = (project_root / filename)
        if filename and rel_candidate.exists():
            entry["chosen_path"] = str(rel_candidate)
        else:
            for p in candidate_paths:
                if os.path.exists(p):
                    entry["chosen_path"] = p
                    break
            if not entry["chosen_path"] and probable and os.path.isabs(probable) and os.path.exists(probable):
                entry["chosen_path"] = probable

        if entry["chosen_path"] and not args.no_symlinks:
            safe_name = filename.replace("/", "__").replace("*", "_star_") or os.path.basename(entry["chosen_path"])
            dest = staging_dir / safe_name
            ok, err = ensure_symlink(entry["chosen_path"], str(dest))
            entry["symlink"] = str(dest) if ok else f"ERROR: {err}"
            entry["in_repo"] = str(project_root) in entry["chosen_path"]

        manifest["entries"].append(entry)

    manifest_path = work_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    ok = sum(1 for e in manifest["entries"] if e["chosen_path"])
    missing = [e["filename"] for e in manifest["entries"] if not e["chosen_path"]]

    report_lines = ["# AutonomaX Bootstrap Report", "", f"**Found:** {ok} / {len(manifest['entries'])}", ""]
    if missing:
        report_lines.append("## Missing")
        for m in missing:
            report_lines.append(f"- {m}")

    report_path = work_dir / "report.md"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    print(f"Manifest: {manifest_path}")
    print(f"Report:   {report_path}")

if __name__ == "__main__":
    main()
