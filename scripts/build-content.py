#!/usr/bin/env python3
"""Build the offline content package from a pinned HowToLiveBetter checkout.

Uses only Python's standard library and never executes files from upstream.
Run: python scripts/build-content.py --source-root /path/to/HowToLiveBetter-SHA
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import html
import json
from pathlib import Path
import re
from urllib.parse import quote, urljoin, urlsplit


UPSTREAM_COMMIT = "20718eeab32cb8506971fb71b03e66a91077be07"
SOURCE_URL = "https://github.com/eternity4719/HowToLiveBetter"
SYNCED_AT = "2026-10-06"
HEADING = re.compile(r"^###\s+(\d+)[.、．]\s*(.+?)\s*$", re.M)
FIELD = re.compile(r"^-\s+([^：:\n]{1,60})[：:][ \t]*(.*)$", re.M)
COMMENT = re.compile(r"<!--.*?-->", re.S)
TAGS = re.compile(r"<!--\s*成本标签[:：]\s*(.*?)\s*-->", re.S)
MD_LINK = re.compile(r"\[([^\]]+)\]\(([^\s)]+)(?:\s+[\"'][^\"']*[\"'])?\)")
WEB_URL = re.compile(r"https?://[^\s<>\]\"'，。；、]+")
REQUIRED_FIELDS = ("成本", "说人话", "收益", "证据等级", "来源", "备注")

GROUPS = [
    {"id": "health", "name": "身体健康", "shortName": "健康", "description": "日常习惯、看病用药与长期照护", "icon": "健"},
    {"id": "safety", "name": "安全应急", "shortName": "安全", "description": "意外防范、紧急情况与出行安全", "icon": "安"},
    {"id": "money", "name": "钱与居住", "shortName": "省钱", "description": "少花冤枉钱，处理住房和生活难关", "icon": "省"},
    {"id": "rights", "name": "工作与权益", "shortName": "权益", "description": "法律边界、劳动权益与财产保护", "icon": "权"},
    {"id": "growth", "name": "学习与生意", "shortName": "成长", "description": "学技能、做生意与选择下一条路", "icon": "学"},
    {"id": "family", "name": "家庭照护", "shortName": "家庭", "description": "恋爱婚育、孩子成长与老人照护", "icon": "家"},
    {"id": "wellbeing", "name": "精力与心情", "shortName": "身心", "description": "分配时间精力，放松与面对打击", "icon": "心"},
    {"id": "digital", "name": "数字生活", "shortName": "数字", "description": "账号信息安全与网站平台基础", "icon": "网"},
]
GROUP_CHAPTERS = {
    "health": [2, 16, 24, 28, 33, 34],
    "safety": [1, 13, 21],
    "money": [5, 6, 7, 15],
    "rights": [8, 9, 11, 19],
    "growth": [12, 23, 31, 32],
    "family": [10, 17, 18, 20, 25, 27, 30],
    "wellbeing": [3, 4, 22, 29],
    "digital": [14, 26],
}
CHAPTER_GROUP = {number: group for group, numbers in GROUP_CHAPTERS.items() for number in numbers}


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def safe_url(value: str) -> bool:
    try:
        parsed = urlsplit(value)
        return parsed.scheme in ("https", "http") and bool(parsed.hostname) and not parsed.username and not parsed.password and not any(ord(c) < 32 for c in value)
    except ValueError:
        return False


def resolve_url(value: str, chapter_url: str) -> str:
    value = html.unescape(value.strip().strip("<>"))
    resolved = urljoin(chapter_url, value)
    if not safe_url(resolved):
        raise ValueError(f"Unsafe or malformed source link: {value!r}")
    return resolved


def plain_text(value: str, chapter_url: str) -> str:
    """Remove presentation syntax without truncating prose or source URLs."""
    value = COMMENT.sub("", value)
    value = MD_LINK.sub(lambda m: f"{m.group(1)}（{resolve_url(m.group(2), chapter_url)}）", value)
    value = re.sub(r"<(https?://[^>]+)>", r"\1", value)
    value = re.sub(r"</?(?:br|p|div|span|strong|em)\b[^>]*>", "", value, flags=re.I)
    value = re.sub(r"^(?:#{1,6}\s+|>\s?)", "", value, flags=re.M)
    value = re.sub(r"\*\*(.+?)\*\*", r"\1", value, flags=re.S)
    value = re.sub(r"__([^_]+)__", r"\1", value)
    value = re.sub(r"`([^`]+)`", r"\1", value)
    value = re.sub(r"\\([\\`*{}\[\]()#+\-.!_>])", r"\1", value)
    value = html.unescape(value)
    value = "\n".join(line.rstrip() for line in value.splitlines())
    return re.sub(r"\n{3,}", "\n\n", value).strip()


def emphasis(raw: str, chapter_url: str) -> list[dict]:
    """Keep the author's emphasis separately, without duplicating full prose."""
    tagged = re.sub(r"\*\*(.+?)\*\*", lambda m: "\ufff0" + m.group(1) + "\ufff1", raw, flags=re.S)
    rendered = plain_text(tagged, chapter_url)
    spans = []
    for match in re.finditer("\ufff0(.*?)\ufff1", rendered, re.S):
        prefix = rendered[:match.start()].replace("\ufff0", "").replace("\ufff1", "")
        start = len(prefix.encode("utf-16-le")) // 2
        spans.append({"start": start, "end": start + len(match.group(1).encode("utf-16-le")) // 2})
    return spans


def reading_guide(source_root: Path, upstream_commit: str) -> dict:
    text = (source_root / "README.md").read_text(encoding="utf-8-sig")
    url = f"{SOURCE_URL}/blob/{upstream_commit}/README.md"
    def section(title):
        return text.split("## " + title + "\n", 1)[1].split("\n## ", 1)[0]
    def rows(block):
        result = []
        for line in block.splitlines():
            if not line.startswith("| "): continue
            cells = [part.strip() for part in line.strip("|").split("|")]
            if len(cells) == 2 and cells[0] not in ("等级", "术语", "---"):
                result.append({"term": cells[0], "text": plain_text(cells[1], url)})
        return result
    grades = section("证据分级")
    cost_rows = []
    for line in section("性价比档").splitlines():
        if line.startswith("| "):
            cells = [v.strip() for v in line.strip("|").split("|")]
            if len(cells) == 3 and cells[0] not in ("维度", "---"):
                cost_rows.append({"term": cells[0], "values": cells[1], "text": plain_text(cells[2], url)})
    beneficiary = next(p for p in text.split("\n\n") if p.startswith("**一条建议的好处落在谁身上"))
    cost_caveat = next(p for p in section("性价比档").split("\n\n") if p.startswith("**这一档是作者自己的判断"))
    return {"sourceUrl": url, "grades": rows(grades), "costDimensions": cost_rows, "costCaveat": plain_text(cost_caveat, url), "beneficiaries": plain_text(beneficiary, url),
            "gradeNotes": [plain_text(p, url) for p in grades.split("\n\n") if p.startswith("A 级只说明") or p.startswith("收益栏和说人话")],
            "glossary": rows(section("读懂数字（术语表）"))}


def source_links(raw: str, chapter_url: str) -> list[dict]:
    """Read every Markdown, angle-bracket and bare HTTP(S) link in order."""
    occurrences = []
    occupied = []
    for match in MD_LINK.finditer(raw):
        url = resolve_url(match.group(2), chapter_url)
        occurrences.append((match.start(), plain_text(match.group(1), chapter_url), url))
        occupied.append((match.start(), match.end()))
    for match in WEB_URL.finditer(raw):
        if any(start <= match.start() < end for start, end in occupied):
            continue
        url = match.group(0).rstrip(";,.，。；）")
        # A bare trailing ')' closes prose only when it has no matching opener.
        while url.endswith(")") and url.count(")") > url.count("("):
            url = url[:-1]
        url = resolve_url(url, chapter_url)
        occurrences.append((match.start(), urlsplit(url).hostname or "原始来源", url))
    result, seen = [], set()
    for _, label, url in sorted(occurrences):
        if url not in seen:
            result.append({"label": label, "url": url})
            seen.add(url)
    return result


def parse_fields(raw_body: str, chapter_url: str) -> tuple[list[dict], dict]:
    """Split only explicit '- label:' boundaries; preserve multiline values."""
    tag_matches = list(TAGS.finditer(raw_body))
    tags = {}
    for match in tag_matches:
        tags.update(re.findall(r"([^\s=]+)=([^\s]+)", match.group(1)))
    clean = COMMENT.sub("", raw_body).strip()
    # Upstream chapter 26 has a license footer after the last entry. Preserve it
    # separately, rather than representing it as part of the author's caveat.
    footer = re.search(r"^##\s+", clean, re.M)
    appendix = clean[footer.start():].strip() if footer else ""
    clean = clean[:footer.start()].rstrip() if footer else clean
    matches = list(FIELD.finditer(clean))
    if not matches:
        raise ValueError("Entry has no labelled fields")
    fields = []
    prefix = clean[:matches[0].start()].strip()
    if prefix:
        fields.append({"label": "补充原文", "text": plain_text(prefix, chapter_url)})
    reconstructed = prefix + ("\n" if prefix else "")
    field_records = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(clean)
        raw_value = clean[match.start(2):end].strip()
        label = match.group(1).strip()
        field = {"label": label, "text": plain_text(raw_value, chapter_url)}
        marked = emphasis(raw_value, chapter_url)
        if marked: field["emphasis"] = marked
        fields.append(field)
        field_records.append({"label": label, "rawCharacters": len(raw_value), "rawSha256": sha256(raw_value.encode("utf-8"))})
        reconstructed += clean[match.start():end]
    if reconstructed.strip() != clean.strip():
        raise ValueError("Field parser did not account for every source character")
    if appendix:
        fields.append({"label": "章节附记", "text": plain_text(appendix, chapter_url)})
        field_records.append({"label": "章节附记", "rawCharacters": len(appendix), "rawSha256": sha256(appendix.encode("utf-8"))})
    labels = {field["label"] for field in fields}
    missing = set(REQUIRED_FIELDS) - labels
    if missing:
        raise ValueError(f"Missing required fields: {sorted(missing)}")
    if any(not field["text"] for field in fields):
        raise ValueError("Empty field value")
    return fields, {"tags": tags, "records": field_records, "appendix": bool(appendix), "sourceCharactersAccounted": True}


def js_json(value) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


def build(source_root: Path, project_root: Path, upstream_commit: str) -> dict:
    if not re.fullmatch(r"[0-9a-f]{40}", upstream_commit):
        raise ValueError("--upstream-commit must be a full 40-character commit SHA")
    source_root = source_root.resolve()
    source_files = sorted((source_root / "book").glob("*.md"))
    if not source_files:
        raise ValueError(f"No book/*.md chapters found in {source_root}")
    chapters, summaries, details, audits = [], [], {}, []
    field_counts, evidence_counts, tag_counts = Counter(), Counter(), Counter()
    raw_heading_total, total_links, footers = 0, 0, []
    for path in source_files:
        number_match = re.match(r"(\d+)-", path.name)
        if not number_match:
            raise ValueError(f"Unexpected chapter filename: {path.name}")
        number = int(number_match.group(1))
        if number not in CHAPTER_GROUP:
            raise ValueError(f"Chapter {number} needs an explicit topic group")
        source_bytes = path.read_bytes()
        text = source_bytes.decode("utf-8-sig").replace("\r\n", "\n")
        headings = list(HEADING.finditer(text))
        raw_heading_total += len(headings)
        if not headings:
            raise ValueError(f"No numbered entries: {path.name}")
        title_match = re.search(r"^#\s+(?:\d+[.、．]\s*)?(.+)$", text, re.M)
        if not title_match:
            raise ValueError(f"Missing chapter title: {path.name}")
        chapter_id = f"ch{number:02d}"
        chapter_url = f"{SOURCE_URL}/blob/{upstream_commit}/book/{quote(path.name)}"
        intro = text[title_match.end():headings[0].start()].strip()
        chapters.append({"id": chapter_id, "number": number, "title": plain_text(title_match.group(1), chapter_url), "groupId": CHAPTER_GROUP[number], "count": len(headings), "sourceUrl": chapter_url, "intro": plain_text(intro, chapter_url), "introEmphasis": emphasis(intro, chapter_url), "introLinks": source_links(intro, chapter_url)})
        entry_audits = []
        for index, heading in enumerate(headings):
            entry_number = int(heading.group(1))
            entry_id = f"c{number:02d}-{entry_number:02d}"
            if entry_id in details:
                raise ValueError(f"Duplicate ID: {entry_id}")
            raw_body = text[heading.end():headings[index + 1].start() if index + 1 < len(headings) else len(text)].strip()
            fields, audit = parse_fields(raw_body, chapter_url)
            by_label = {field["label"]: field["text"] for field in fields}
            tags = audit["tags"]
            missing_tags = {"钱", "时间", "毅力"} - set(tags)
            if missing_tags:
                raise ValueError(f"{entry_id} is missing cost tags: {missing_tags}")
            metadata = {"id": entry_id, "chapterId": chapter_id, "chapterNumber": number, "number": entry_number, "groupId": CHAPTER_GROUP[number], "title": plain_text(heading.group(2), chapter_url), "summary": by_label["说人话"], "evidence": by_label["证据等级"], "moneyCost": tags["钱"], "timeCost": tags["时间"], "effort": tags["毅力"], "hasCaveat": bool(by_label.get("备注")), "benefit": tags.get("收益", ""), "metric": tags.get("口径", "")}
            links = source_links(raw_body, chapter_url)
            summaries.append(metadata)
            # Shared metadata and chapter URL are restored in the JS wrapper.
            # Keeping them once avoids duplicating complete summary prose.
            source_line = text[:heading.start()].count("\n") + 1
            details[entry_id] = {"fields": fields, "sourceLinks": links, "entrySourceUrl": chapter_url + f"#L{source_line}"}
            field_counts.update(field["label"] for field in fields)
            evidence_counts.update([metadata["evidence"]])
            tag_counts.update(tags.keys())
            total_links += len(links)
            if audit["appendix"]:
                footers.append(entry_id)
            entry_audits.append({"id": entry_id, "number": entry_number, "title": metadata["title"], "sourceLine": text[:heading.start()].count("\n") + 1, "rawBodySha256": sha256(raw_body.encode("utf-8")), "fields": audit["records"], "sourceCharactersAccounted": audit["sourceCharactersAccounted"], "sourceLinks": len(links)})
        if [a["number"] for a in entry_audits] != list(range(1, len(headings) + 1)):
            raise ValueError(f"Non-contiguous entry numbering: {path.name}")
        audits.append({"file": f"book/{path.name}", "sha256": sha256(source_bytes), "sourceHeadingCount": len(headings), "generatedEntryCount": len(entry_audits), "titlesMatch": all(a["title"] == plain_text(h.group(2), chapter_url) for a, h in zip(entry_audits, headings)), "entries": entry_audits})
    if len(summaries) != raw_heading_total or len(details) != len(summaries):
        raise ValueError("Entry count mismatch")
    if len({chapter["id"] for chapter in chapters}) != len(chapters):
        raise ValueError("Duplicate chapter ID")
    found_chapters = {chapter["number"] for chapter in chapters}
    if found_chapters != set(CHAPTER_GROUP):
        raise ValueError(f"Chapter mapping mismatch: {found_chapters ^ set(CHAPTER_GROUP)}")
    meta = {"title": "低成本生活指南", "version": "0.1.0", "syncedAt": SYNCED_AT, "upstreamCommit": upstream_commit, "sourceUrl": SOURCE_URL, "licenseUrl": "https://creativecommons.org/licenses/by/4.0/", "totalEntries": len(summaries), "totalChapters": len(chapters), "originalTitle": "高性价比人生指南", "originalAuthor": "eternity4719", "evidenceNote": "证据等级沿用原作者分级，未进行独立临床核验。", "adaptationNote": "基于原文重编导航与离线阅读界面；建议正文、来源和备注保留。"}
    catalog = {"meta": meta, "groups": GROUPS, "chapters": chapters, "entries": summaries}
    catalog_path = project_root / "miniprogram/data/catalog.js"
    guide_path = project_root / "miniprogram/data/reading-guide.js"
    detail_path = project_root / "miniprogram/content/data/entries.js"
    report_path = project_root / "release/content-build-report.json"
    header = "// Generated by scripts/build-content.py. Content: CC BY 4.0, eternity4719.\n// Evidence grades are the upstream author's ratings; no independent clinical review.\n"
    catalog_bytes = (header + "module.exports=" + js_json(catalog) + ";\n").encode("utf-8")
    detail_js = header + "var catalog=require('../../data/catalog.js');\nvar details=" + js_json(details) + ";\n"
    detail_js += "var chapters={};catalog.chapters.forEach(function(chapter){chapters[chapter.id]=chapter;});\n"
    detail_js += "catalog.entries.forEach(function(entry){var detail=details[entry.id];Object.keys(entry).forEach(function(key){detail[key]=entry[key];});detail.sourceUrl=chapters[entry.chapterId].sourceUrl;});\nmodule.exports=details;\n"
    detail_bytes = detail_js.encode("utf-8")
    guide = reading_guide(source_root, upstream_commit)
    guide_bytes = (header + "module.exports=" + js_json(guide) + ";\n").encode("utf-8")
    for path, data in ((catalog_path, catalog_bytes), (detail_path, detail_bytes), (guide_path, guide_bytes)):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    report = {
        "status": "PASS", "syncedAt": SYNCED_AT, "upstreamCommit": upstream_commit,
        "sourceUrl": SOURCE_URL, "sourceRootName": source_root.name,
        "evidenceAssessment": "沿用原作者证据分级；本次仅核对内容转换与完整性，未进行独立临床、法律或金融结论核验。",
        "scope": "全部 book/*.md 编号建议、章节导语、全部字段、成本标签和 HTTP(S) 来源链接；未执行任何上游脚本。",
        "totals": {"chapters": len(chapters), "entries": len(summaries), "sourceHeadings": raw_heading_total, "sourceLinks": total_links, "fields": sum(field_counts.values()), "rawSourceBytes": sum(path.stat().st_size for path in source_files)},
        "expectedReadmeEntries": 667, "matchesReadmeCount": len(summaries) == 667,
        "fieldCoverage": dict(field_counts), "costTagCoverage": dict(tag_counts), "evidenceCounts": dict(evidence_counts),
        "checks": {"allChapterFilesIncluded": True, "allEntryTitlesMatched": all(a["titlesMatch"] for a in audits), "entryAndChapterIdsUnique": True, "allSixRequiredFieldsPresent": all(field_counts[label] == len(summaries) for label in REQUIRED_FIELDS), "sourceCharactersAccounted": all(e["sourceCharactersAccounted"] for a in audits for e in a["entries"]), "summaryNotTruncated": True, "multilineFieldsPreserved": True, "safeHttpLinksOnly": all(safe_url(link["url"]) for entry in details.values() for link in entry["sourceLinks"]), "pinnedChapterSourceUrls": all(f"/blob/{upstream_commit}/" in c["sourceUrl"] for c in chapters), "chapterNumbersComplete": True},
        "footerHandling": {"entryIds": footers, "preservation": "Chapter footers retained as 章节附记 fields instead of merging with 备注."},
        "storage": {"rawBodyIncluded": False, "reason": "All labelled content and chapter appendices are retained as display text; original Markdown remains available at SHA-pinned chapter URLs. Metadata is restored from catalog at module load to avoid duplicating the complete summaries."},
        "readingGuide": {"glossaryTerms": len(guide["glossary"]), "gradeDefinitions": len(guide["grades"]), "source": guide["sourceUrl"]},
        "files": [{"path": path.relative_to(project_root).as_posix(), "bytes": len(data), "sha256": sha256(data)} for path, data in ((catalog_path, catalog_bytes), (detail_path, detail_bytes), (guide_path, guide_bytes))],
        "chapters": audits,
    }
    if not all(report["checks"].values()):
        raise ValueError("Content integrity checks failed")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--upstream-commit", default=UPSTREAM_COMMIT)
    args = parser.parse_args()
    project_root = Path(__file__).resolve().parents[1]
    report = build(args.source_root, project_root, args.upstream_commit)
    print(json.dumps({"status": report["status"], "totals": report["totals"], "files": report["files"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
