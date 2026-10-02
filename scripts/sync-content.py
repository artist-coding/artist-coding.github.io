"""Synchronize the website with a local HarnessSafe checkout and paper figures."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

FAMILIES = {
    "F1_memory_runtime": "F1",
    "v2_skill_runtime": "F2",
    "v2_tool_mcp_runtime": "F3",
    "T2_memory_to_skill": "T2",
    "T3_subagent_poisoning": "T3-S",
    "T3_compaction_resume_poisoning": "T3-C",
    "T3_shared_artifact_supply_chain": "T3-A",
}
EXPECTED = {"F1": 72, "F2": 84, "F3": 70, "T2": 36, "T3-S": 30, "T3-C": 30, "T3-A": 6}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark-root", required=True, type=Path)
    parser.add_argument("--figures-dir", type=Path)
    args = parser.parse_args()
    site = Path(__file__).resolve().parents[1]
    root = args.benchmark_root.resolve()
    manifest_path = root / "runs/manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert set(manifest["suites"]) == set(FAMILIES), "Review new family mappings before publishing."
    cases = []
    metadata_hashes = {}
    for suite, family in FAMILIES.items():
        for record in manifest["suites"][suite]["cases"]:
            path = root / "runs" / record["case_dir"] / "case_meta.json"
            meta = json.loads(path.read_text(encoding="utf-8"))
            assert record.get("case_id", meta["case_id"]) == meta["case_id"]
            title = str(meta.get("variant") or record.get("variant") or meta["case_id"]).replace("_", " ")
            item = {"id": meta["case_id"], "title": title, "family": family, "path": record["case_dir"]}
            for field in ["entry", "carrier", "boundary", "trigger", "violation"]:
                value = meta.get(field)
                item[field] = value if isinstance(value, str) and value else json.dumps(value) if value else "Not specified"
            item["safe_behavior"] = str(meta.get("expected_safe_behavior") or "")
            cases.append(item)
            metadata_hashes[meta["case_id"]] = digest(path)
    assert collections.Counter(c["family"] for c in cases) == EXPECTED
    assert len({c["id"] for c in cases}) == 328
    commit = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    write_json(site / "assets/cases.json", {"manifest_sha256": digest(manifest_path), "cases": cases})
    write_json(site / "assets/content-source.json", {
        "repository": "https://github.com/artist-coding/harnesssafe",
        "source_commit": commit,
        "manifest_sha256": digest(manifest_path),
        "families": EXPECTED,
        "case_metadata_sha256": metadata_hashes,
    })
    if args.figures_dir:
        executable = shutil.which("pdftoppm")
        if not executable:
            raise SystemExit("Install Poppler and put pdftoppm on PATH to render the original paper figures.")
        folder = site / "assets/figures"
        folder.mkdir(parents=True, exist_ok=True)
        records = []
        for stem in ["background", "benchmark", "checkpoint_dist"]:
            source = args.figures_dir / (stem + ".pdf")
            pdf = folder / source.name
            shutil.copyfile(source, pdf)
            subprocess.run([executable, "-singlefile", "-scale-to", "2400", "-png", str(pdf), str(folder / stem)], check=True)
            png = folder / (stem + ".png")
            records.append({"pdf": pdf.name, "pdf_sha256": digest(pdf), "png": png.name, "png_sha256": digest(png)})
        write_json(folder / "sources.json", {
            "paper": "https://arxiv.org/abs/2608.06984",
            "doi": "10.48550/arXiv.2608.06984",
            "license": "CC-BY-4.0",
            "conversion": "Original author-provided PDF figures rendered with Poppler; longest edge 2400 px. No figure content changed.",
            "files": records,
        })
    print("Synced 328 cases across 7 families" + (" and 3 paper figures." if args.figures_dir else "."))

if __name__ == "__main__":
    main()
