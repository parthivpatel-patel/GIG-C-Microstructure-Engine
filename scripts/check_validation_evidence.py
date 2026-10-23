#!/usr/bin/env python3
"""Verify local validation evidence, not publisher authenticity or hosted success.

Historical source identities are checked against the recorded implementation commit;
--working-tree instead requires those exact source bytes in the supplied checkout.
Raw logs/artifacts are deliberately required: report assertions alone cannot pass.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

MAX_FILE = 128 * 1024 * 1024
MAX_DOCUMENT = 16 * 1024 * 1024
MAX_TOTAL = 512 * 1024 * 1024
MAX_ENTRIES = 4096
SHA = re.compile(r"[0-9a-f]{64}\Z")
COMMIT = re.compile(r"[0-9a-f]{40}\Z")
NAME = re.compile(r"[A-Za-z0-9_.-]{1,128}\Z")

CANDIDATE_CONFIGURATIONS = frozenset({
    "phase9-clean-debug", "phase9-clean-release", "phase9-clean-asan-ubsan",
    "phase9-clang-debug", "phase9-clang-release", "phase9-clang-asan-ubsan",
    "python-debug", "python-release", "python-asan-ubsan",
})
# Minimum reviewed P1E--P1H path coverage, shared by the historical H/I freezes.
# This is a protected subset, not a complete transitive build dependency inventory.
CANDIDATE_SOURCE_PATHS = frozenset({
    "CMakeLists.txt", "include/gig/itch/wire.hpp",
    "src/itch/binary_file.cpp", "src/itch/decoder.cpp", "src/itch/context.cpp",
    "src/itch/reconstruction.cpp", "src/itch/restart.cpp", "src/itch/sha256.cpp",
    "src/itch/gzip.cpp", "src/itch/streaming.cpp",
    "scripts/check_itch_reference.py", "scripts/check_itch_context_reference.py",
    "scripts/check_itch_l3_reference.py", "scripts/check_itch_streaming_reference.py",
    "tests/itch_reference_driver.cpp", "tests/itch_context_reference_driver.cpp",
    "tests/itch_l3_reference_driver.cpp", "tests/itch_streaming_reference_driver.cpp",
    "tests/test_itch_streaming.cpp", "tests/test_itch_gzip.cpp",
})
# Reviewed P1E--P1H contracts; adding a future oracle does not remove these gates.
CANDIDATE_CANONICAL = {
    "itch.independent_reference": "142217bb7c7a51dbcbc7d54108247d7bec62575cf036293425b40cd205061b3e",
    "itch.context_reference": "58d6a2f6fd574bc8041676964307ac606422dcebba780bc10166b3019b99476e",
    "itch.l3_reference": "bb16d4ba9e400ee8f2bc40707de5aa89d0b0955819b4f1f45ca2cdf82cac7991",
    "itch.streaming_reference": "be5d6f5a15fa1dc77560e0a815b8397a605eab369fa66f44df12e5ed9b04a4d5",
}


class EvidenceError(ValueError):
    """The requested verification cannot support the declared evidence claim."""


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise EvidenceError(reason)


def exact_json(value: object) -> str:
    """Compare JSON values without Python's bool/int/float equality coercions."""
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (ValueError, RecursionError) as exc:
        raise EvidenceError("invalid finite JSON value") from exc


def invalid_constant(value: str) -> None:
    raise EvidenceError("nonfinite JSON token: " + value)


def duplicate_free(pairs: list[tuple[str, object]]) -> dict:
    out: dict = {}
    for key, value in pairs:
        require(key not in out, "duplicate JSON field: " + key)
        out[key] = value
    return out


class Reader:
    def __init__(self) -> None:
        self.total = 0
        self.last_document_sha256 = ""

    def data(self, path: Path, limit: int = MAX_FILE) -> bytes:
        require(path.is_file(), "missing file: " + str(path))
        size = path.stat().st_size
        require(0 <= size <= limit, "file size limit: " + str(path))
        require(self.total + size <= MAX_TOTAL, "aggregate byte limit")
        with path.open("rb") as stream:
            data = stream.read(limit + 1)
        require(len(data) == size and len(data) <= limit, "file changed or size limit: " + str(path))
        self.total += len(data)
        return data

    def document(self, path: Path) -> dict:
        try:
            data = self.data(path, MAX_DOCUMENT)
            value = json.loads(data, object_pairs_hook=duplicate_free, parse_constant=invalid_constant)
            self.last_document_sha256 = hashlib.sha256(data).hexdigest()
        except (json.JSONDecodeError, UnicodeError, RecursionError) as exc:
            raise EvidenceError("invalid bounded JSON document") from exc
        require(type(value) is dict, "JSON document must be an object")
        return value

    def digest(self, path: Path, expected: str) -> bytes:
        digest(expected)
        data = self.data(path)
        require(hashlib.sha256(data).hexdigest() == expected, "SHA256 mismatch: " + str(path))
        return data


def digest(value: object) -> str:
    require(type(value) is str and SHA.fullmatch(value) is not None, "invalid SHA256")
    return value


def integer(value: object, name: str) -> int:
    require(type(value) is int and 0 <= value <= 1_000_000, "invalid integer: " + name)
    return value


def bounded_map(value: object, name: str) -> dict:
    require(type(value) is dict and 0 < len(value) <= MAX_ENTRIES, "invalid mapping: " + name)
    return value


def local_path(root: Path, name: object) -> Path:
    require(type(name) is str and 0 < len(name) <= 4096, "invalid relative path")
    part = PurePosixPath(name)
    require(not part.is_absolute() and all(p not in (".", "..") for p in part.parts)
            and "\\" not in name and ":" not in name and "\x00" not in name and bool(part.parts), "unsafe relative path: " + name)
    result = (root / name).resolve()
    require(result.is_relative_to(root.resolve()), "path escapes root: " + name)
    return result


def git_blob(root: Path, revision: str, path: str, reader: Reader) -> bytes:
    # Exact hexadecimal revision and validated relative path, never shell interpolation.
    require(COMMIT.fullmatch(revision) is not None, "invalid implementation commit")
    local_path(root, path)
    obj = revision + ":" + path
    try:
        size = int(subprocess.check_output(["git", "-C", str(root), "cat-file", "-s", obj],
                                           stderr=subprocess.PIPE, timeout=15))
        require(0 <= size <= MAX_DOCUMENT and reader.total + size <= MAX_TOTAL, "source blob byte limit")
        data = subprocess.check_output(["git", "-C", str(root), "cat-file", "blob", obj],
                                       stderr=subprocess.PIPE, timeout=15)
    except (subprocess.SubprocessError, ValueError) as exc:
        raise EvidenceError("unavailable implementation source: " + path) from exc
    require(len(data) == size, "source blob size mismatch")
    reader.total += size
    return data


def junit(data: bytes, row: dict) -> dict:
    require(len(data) <= MAX_DOCUMENT, "JUnit byte limit")
    # CTest writes UTF-8. Decode before inspecting declarations: searching raw
    # ASCII bytes lets UTF-16/32 DTDs bypass the no-entity input contract.
    try:
        text = data.decode("utf-8")
    except UnicodeError as exc:
        raise EvidenceError("JUnit must be UTF-8") from exc
    require("\x00" not in text, "NUL/UTF-16/32 JUnit not accepted")
    require("<!DOCTYPE" not in text.upper() and "<!ENTITY" not in text.upper(), "DTD/entities not accepted")
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        raise EvidenceError("invalid JUnit XML") from exc
    require(root.tag == "testsuite", "expected one CTest testsuite")
    cases = root.findall("testcase")
    require(0 < len(cases) <= 10000, "JUnit case count limit")
    names = [case.get("name") for case in cases]
    require(all(type(n) is str and n for n in names) and len(names) == len(set(names)),
            "duplicate or missing JUnit case identity")
    failures = sum(case.find("failure") is not None or case.find("error") is not None for case in cases)
    skipped = sum(case.find("skipped") is not None for case in cases)
    disabled = sum(case.get("status") in ("disabled", "notrun") for case in cases)
    for case in cases:
        require(case.get("status", "run") in ("run", "disabled", "notrun"), "unknown JUnit status")
    counts = {"tests": len(cases), "failures": failures, "skipped": skipped, "disabled": disabled}
    for key, actual in counts.items():
        require(integer(row.get(key), key) == actual, "reported/JUnit count mismatch: " + key)
        try:
            declared = int(root.get(key, "-1"))
        except ValueError as exc:
            raise EvidenceError("invalid JUnit count") from exc
        require(declared == actual, "JUnit summary/case count mismatch: " + key)
    require(failures == skipped == disabled == 0, "required outcomes failed/skipped/disabled")
    expected = bounded_map(row.get("canonical_sha256"), "canonical_sha256")
    by_name = {case.get("name"): case for case in cases}
    for name, wanted in expected.items():
        digest(wanted)
        require(name in by_name, "missing canonical testcase: " + name)
        output = "".join(by_name[name].itertext())
        found = re.findall(r"canonical_sha256=([0-9a-f]{64})(?![0-9a-f])", output)
        require(found == [wanted], "canonical output mismatch: " + name)
    return counts


def candidate_contract(report: dict) -> None:
    frozen = bounded_map(report.get("frozen_source_sha256"), "frozen_source_sha256")
    require(CANDIDATE_SOURCE_PATHS <= frozen.keys(), "candidate protected source coverage missing")
    rows = report.get("matrix")
    require(type(rows) is list and len(rows) == len(CANDIDATE_CONFIGURATIONS),
            "candidate requires all nine configurations")
    require(all(type(row) is dict for row in rows), "invalid candidate matrix row")
    names = [row.get("configuration") for row in rows]
    require(all(type(name) is str for name in names)
            and set(names) == CANDIDATE_CONFIGURATIONS, "candidate configuration coverage mismatch")
    enabled = report.get("enabled_configurations")
    require(type(enabled) is dict and set(enabled) == CANDIDATE_CONFIGURATIONS
            and all(value is True for value in enabled.values()), "candidate streaming must be ON in all configurations")
    for row in rows:
        canonical = row.get("canonical_sha256")
        require(type(canonical) is dict
                and all(canonical.get(name) == wanted for name, wanted in CANDIDATE_CANONICAL.items()),
                "candidate mandatory oracle family/hash mismatch")


def verify(evidence: Path, raw_root: Path, source_root: Path, *, working_tree: bool = False,
           candidate_profile: bool = False) -> dict:
    reader = Reader()
    report = reader.document(evidence)
    evidence_hash = reader.last_document_sha256
    if candidate_profile:
        candidate_contract(report)
    revision = report.get("implementation_commit")
    require(type(revision) is str and COMMIT.fullmatch(revision) is not None, "invalid implementation commit")
    frozen = bounded_map(report.get("frozen_source_sha256"), "frozen_source_sha256")
    aggregate = hashlib.sha256(json.dumps(frozen, sort_keys=True).encode()).hexdigest()
    require(aggregate == digest(report.get("source_manifest_sha256")), "source manifest digest mismatch")
    for name, expected in frozen.items():
        digest(expected)
        path = local_path(source_root, name)
        data = reader.data(path, MAX_DOCUMENT) if working_tree else git_blob(source_root, revision, name, reader)
        require(hashlib.sha256(data).hexdigest() == expected, "frozen source mismatch: " + name)
    raw_map = bounded_map(report.get("raw_evidence_sha256"), "raw_evidence_sha256")
    for name, expected in raw_map.items():
        reader.digest(local_path(raw_root, name), expected)
    # Bind duplicated report assertions to the already hash-verified raw documents.
    # H uses a historical object-shaped measurement record with separate raw files;
    # I's list-shaped record has one mandatory consolidated measurements.json.
    require(type(report.get("measurements")) is not list or "measurements.json" in raw_map,
            "list measurements require raw measurements.json")
    for raw_name, field in (("measurements.json", "measurements"),
                            ("measurement-environment.json", "measurement_environment"),
                            ("toolchains.json", "toolchains")):
        if raw_name in raw_map:
            raw_path = local_path(raw_root, raw_name)
            if field == "measurements":
                # Reader.document intentionally requires objects; measurements is a list.
                data = reader.data(raw_path, MAX_DOCUMENT)
                require(hashlib.sha256(data).hexdigest() == raw_map[raw_name],
                        "SHA256 mismatch: " + str(raw_path))
                try:
                    actual = json.loads(data, object_pairs_hook=duplicate_free,
                                        parse_constant=invalid_constant)
                except (json.JSONDecodeError, UnicodeError, RecursionError) as exc:
                    raise EvidenceError("invalid bounded measurements JSON") from exc
            else:
                actual = reader.document(raw_path)
            require(exact_json(actual) == exact_json(report.get(field)), "raw/report contradiction: " + field)
    rows = report.get("matrix")
    require(type(rows) is list and 0 < len(rows) <= 64, "invalid matrix")
    seen: set[str] = set()
    canonical: dict | None = None
    total = 0
    for row in rows:
        require(type(row) is dict, "invalid matrix row")
        config = row.get("configuration")
        require(type(config) is str and NAME.fullmatch(config) is not None and config not in seen,
                "duplicate or unsafe configuration")
        seen.add(config)
        require(integer(row.get("build_exit"), "build_exit") == 0
                and integer(row.get("test_exit"), "test_exit") == 0, "unsuccessful build/test command")
        xml = reader.digest(local_path(raw_root, config + ".xml"), row.get("junit_sha256"))
        reader.digest(local_path(raw_root, config + ".log"), row.get("log_sha256"))
        total += junit(xml, row)["tests"]
        if canonical is None:
            canonical = row["canonical_sha256"]
        require(canonical == row["canonical_sha256"], "cross-configuration canonical disagreement")
    require(integer(report.get("total_ctest_outcomes"), "total_ctest_outcomes") == total, "matrix total mismatch")
    enabled = report.get("enabled_configurations")
    if enabled is not None:
        require(type(enabled) is dict and set(enabled) == seen and all(v is True for v in enabled.values()),
                "streaming configuration coverage mismatch")
    package = report.get("package")
    require(type(package) is dict, "missing package evidence")
    artifacts = bounded_map(package.get("artifact_sha256"), "package artifacts")
    for name, expected in artifacts.items():
        reader.digest(local_path(raw_root.parent, name), expected)
    if "package.json" in raw_map:
        require(exact_json(reader.document(local_path(raw_root, "package.json"))) == exact_json(package),
                "package record contradiction")
    steps = package.get("steps")
    require(type(steps) is list and 0 < len(steps) <= 256, "invalid package steps")
    step_names: set[str] = set()
    for step in steps:
        require(type(step) is dict and type(step.get("name")) is str and step["name"] not in step_names,
                "duplicate/invalid package step")
        step_names.add(step["name"])
        require(integer(step.get("exit_code"), "package exit_code") == 0, "package command failed")
        digest(step.get("stdout_sha256"))
    return {"status": "PASS", "coverage_profile": "candidate-P1E-P1H-nine-configurations" if candidate_profile else "generic-consistency-only",
            "implementation_commit": revision,
            "source_mode": "working-tree" if working_tree else "historical-git-blobs",
            "frozen_files": len(frozen), "raw_files": len(raw_map), "package_artifacts": len(artifacts),
            "configurations": len(rows), "ctest_outcomes": total, "canonical_sha256": canonical,
            "evidence_sha256": evidence_hash,
            "bytes_checked": reader.total,
            "limitation": "Local byte/count consistency; not execution attestation, license, origin authentication or hosted CI proof."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--raw-root", type=Path, required=True, help="private phase evidence directory")
    parser.add_argument("--source-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--working-tree", action="store_true")
    parser.add_argument("--candidate-profile", action="store_true",
                        help="require all nine configurations, streaming ON and reviewed P1E--P1H oracle identities")
    args = parser.parse_args()
    try:
        print(json.dumps(verify(args.evidence, args.raw_root, args.source_root,
                                working_tree=args.working_tree, candidate_profile=args.candidate_profile), sort_keys=True))
        return 0
    except (EvidenceError, OSError, KeyError, TypeError, RecursionError) as exc:
        print("evidence verification failed: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
