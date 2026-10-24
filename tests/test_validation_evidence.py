#!/usr/bin/env python3
"""Independent adversarial fixtures for the offline evidence verifier."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/check_validation_evidence.py"
spec = importlib.util.spec_from_file_location("evidence", SCRIPT)
assert spec and spec.loader
evidence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evidence)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class EvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.raw = self.root / "build/evidence"
        self.raw.mkdir(parents=True)
        self.report = self.root / "report.json"
        self.source = b"// independent immutable fixture\n"
        (self.root / "source.cpp").write_bytes(self.source)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(self.root), "add", "source.cpp"], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(self.root), "-c", "user.name=Evidence Test", "-c",
                        "user.email=evidence@example.invalid", "commit", "-qm", "fixture"], check=True,
                       capture_output=True)
        self.commit = subprocess.check_output(["git", "-C", str(self.root), "rev-parse", "HEAD"], text=True).strip()
        self.canonical = "a" * 64
        self.xml = (f'<testsuite tests="1" failures="0" skipped="0" disabled="0">'
                    f'<testcase name="oracle" status="run"><system-out>'
                    f'canonical_sha256={self.canonical}</system-out></testcase></testsuite>').encode()
        (self.raw / "debug.xml").write_bytes(self.xml)
        (self.raw / "debug.log").write_bytes(b"actual command output\n")
        (self.root / "build/artifact.whl").write_bytes(b"independent fixture artifact")
        frozen = {"source.cpp": sha(self.source)}
        self.value = {
            "implementation_commit": self.commit,
            "source_manifest_sha256": sha(json.dumps(frozen, sort_keys=True).encode()),
            "frozen_source_sha256": frozen,
            "raw_evidence_sha256": {"debug.xml": sha(self.xml), "debug.log": sha(b"actual command output\n")},
            "matrix": [{"configuration": "debug", "build_exit": 0, "test_exit": 0,
                        "tests": 1, "failures": 0, "skipped": 0, "disabled": 0,
                        "junit_sha256": sha(self.xml), "log_sha256": sha(b"actual command output\n"),
                        "canonical_sha256": {"oracle": self.canonical}}],
            "total_ctest_outcomes": 1,
            "enabled_configurations": {"debug": True},
            "package": {"steps": [{"name": "consumer", "exit_code": 0, "stdout_sha256": sha(b"")}],
                        "artifact_sha256": {"artifact.whl": sha(b"independent fixture artifact")}},
        }

    def check(self, *, working_tree: bool = False, candidate_profile: bool = False) -> dict:
        self.report.write_text(json.dumps(self.value))
        return evidence.verify(self.report, self.raw, self.root, working_tree=working_tree,
                               candidate_profile=candidate_profile)

    def rejected(self) -> None:
        with self.assertRaises(evidence.EvidenceError):
            self.check()

    def replace_xml(self, value: bytes) -> None:
        (self.raw / "debug.xml").write_bytes(value)
        self.value["raw_evidence_sha256"]["debug.xml"] = sha(value)
        self.value["matrix"][0]["junit_sha256"] = sha(value)

    def make_candidate(self) -> None:
        # Literal independent coverage expectation; not imported from verifier constants.
        names = ["phase9-clean-debug", "phase9-clean-release", "phase9-clean-asan-ubsan",
                 "phase9-clang-debug", "phase9-clang-release", "phase9-clang-asan-ubsan",
                 "python-debug", "python-release", "python-asan-ubsan"]
        canon = {
            "itch.independent_reference": "142217bb7c7a51dbcbc7d54108247d7bec62575cf036293425b40cd205061b3e",
            "itch.context_reference": "58d6a2f6fd574bc8041676964307ac606422dcebba780bc10166b3019b99476e",
            "itch.l3_reference": "bb16d4ba9e400ee8f2bc40707de5aa89d0b0955819b4f1f45ca2cdf82cac7991",
            "itch.streaming_reference": "be5d6f5a15fa1dc77560e0a815b8397a605eab369fa66f44df12e5ed9b04a4d5",
        }
        xml = ('<testsuite tests="4" failures="0" skipped="0" disabled="0">' + ''.join(
            f'<testcase name="{name}" status="run"><system-out>canonical_sha256={value}'
            '</system-out></testcase>' for name, value in canon.items()) + '</testsuite>').encode()
        template = copy.deepcopy(self.value["matrix"][0])
        self.value["matrix"] = []
        self.value["raw_evidence_sha256"] = {}
        for name in names:
            row = copy.deepcopy(template)
            row.update(configuration=name, tests=4, canonical_sha256=canon, junit_sha256=sha(xml))
            self.value["matrix"].append(row)
            (self.raw / (name + ".xml")).write_bytes(xml)
            (self.raw / (name + ".log")).write_bytes(b"actual command output\n")
            self.value["raw_evidence_sha256"][name + ".xml"] = sha(xml)
            self.value["raw_evidence_sha256"][name + ".log"] = sha(b"actual command output\n")
        # Independent literal protected path fixture; all are immutable Git blobs.
        protected = ["CMakeLists.txt", "include/gig/itch/wire.hpp",
                     "src/itch/binary_file.cpp", "src/itch/decoder.cpp", "src/itch/context.cpp",
                     "src/itch/reconstruction.cpp", "src/itch/restart.cpp", "src/itch/sha256.cpp",
                     "src/itch/gzip.cpp", "src/itch/streaming.cpp",
                     "scripts/check_itch_reference.py", "scripts/check_itch_context_reference.py",
                     "scripts/check_itch_l3_reference.py", "scripts/check_itch_streaming_reference.py",
                     "tests/itch_reference_driver.cpp", "tests/itch_context_reference_driver.cpp",
                     "tests/itch_l3_reference_driver.cpp", "tests/itch_streaming_reference_driver.cpp",
                     "tests/test_itch_streaming.cpp", "tests/test_itch_gzip.cpp"]
        for name in protected:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(self.source)
            self.value["frozen_source_sha256"][name] = sha(self.source)
        subprocess.run(["git", "-C", str(self.root), "add", "."], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(self.root), "-c", "user.name=Evidence Test", "-c",
                        "user.email=evidence@example.invalid", "commit", "-qm", "candidate fixture"],
                       check=True, capture_output=True)
        self.value["implementation_commit"] = subprocess.check_output(
            ["git", "-C", str(self.root), "rev-parse", "HEAD"], text=True).strip()
        self.value["source_manifest_sha256"] = sha(json.dumps(
            self.value["frozen_source_sha256"], sort_keys=True).encode())
        self.value["total_ctest_outcomes"] = 36
        self.value["enabled_configurations"] = dict.fromkeys(names, True)

    def test_candidate_missing_protected_source_rehashed(self) -> None:
        self.make_candidate()
        self.value["frozen_source_sha256"] = {"source.cpp": sha(self.source)}
        self.value["source_manifest_sha256"] = sha(json.dumps(
            self.value["frozen_source_sha256"], sort_keys=True).encode())
        with self.assertRaises(evidence.EvidenceError):
            self.check(candidate_profile=True)

    def test_measurements_raw_contradiction(self) -> None:
        raw = [{"raw": {"peak_pmr_bytes": 100}}]
        data = json.dumps(raw).encode()
        (self.raw / "measurements.json").write_bytes(data)
        self.value["raw_evidence_sha256"]["measurements.json"] = sha(data)
        self.value["measurements"] = [{"raw": {"peak_pmr_bytes": 1}}]
        self.rejected()

    def test_list_measurements_require_raw_record(self) -> None:
        self.value["measurements"] = [{"raw": {"peak_pmr_bytes": 1}}]
        self.rejected()

    def test_measurements_numeric_type_contradictions(self) -> None:
        for actual, declared in ((0, False), (1, 1.0)):
            with self.subTest(actual=actual, declared=declared):
                data = json.dumps([{"raw": {"value": actual}}]).encode()
                (self.raw / "measurements.json").write_bytes(data)
                self.value["raw_evidence_sha256"]["measurements.json"] = sha(data)
                self.value["measurements"] = [{"raw": {"value": declared}}]
                self.rejected()

    def test_measurements_raw_consistent(self) -> None:
        value = [{"raw": {"peak_pmr_bytes": 100}}]
        data = json.dumps(value).encode()
        (self.raw / "measurements.json").write_bytes(data)
        self.value["raw_evidence_sha256"]["measurements.json"] = sha(data)
        self.value["measurements"] = value
        self.assertEqual(self.check()["status"], "PASS")

    def test_toolchains_raw_contradiction(self) -> None:
        data = b'{"compiler": "actual"}'
        (self.raw / "toolchains.json").write_bytes(data)
        self.value["raw_evidence_sha256"]["toolchains.json"] = sha(data)
        self.value["toolchains"] = {"compiler": "changed"}
        self.rejected()

    def test_environment_raw_missing_report_field(self) -> None:
        data = b'{"cpu": "actual"}'
        (self.raw / "measurement-environment.json").write_bytes(data)
        self.value["raw_evidence_sha256"]["measurement-environment.json"] = sha(data)
        self.rejected()

    def test_environment_raw_contradiction(self) -> None:
        data = b'{"cpu": "actual"}'
        (self.raw / "measurement-environment.json").write_bytes(data)
        self.value["raw_evidence_sha256"]["measurement-environment.json"] = sha(data)
        self.value["measurement_environment"] = {"cpu": "changed"}
        self.rejected()

    def test_candidate_profile_complete(self) -> None:
        self.make_candidate()
        self.assertEqual(self.check(candidate_profile=True)["coverage_profile"],
                         "candidate-P1E-P1H-nine-configurations")

    def test_candidate_dropped_config_despite_adjusted_total(self) -> None:
        self.make_candidate()
        removed = self.value["matrix"].pop()
        self.value["enabled_configurations"].pop(removed["configuration"])
        self.value["total_ctest_outcomes"] -= 4
        # Generic consistency is intentionally weaker than mandatory candidate coverage.
        self.assertEqual(self.check()["ctest_outcomes"], 32)
        with self.assertRaises(evidence.EvidenceError):
            self.check(candidate_profile=True)

    def test_candidate_reduced_canonical_family(self) -> None:
        self.make_candidate()
        for row in self.value["matrix"]:
            row["canonical_sha256"] = {"itch.independent_reference":
                "142217bb7c7a51dbcbc7d54108247d7bec62575cf036293425b40cd205061b3e"}
        self.assertEqual(self.check()["ctest_outcomes"], 36)
        with self.assertRaises(evidence.EvidenceError):
            self.check(candidate_profile=True)

    def test_candidate_changed_reviewed_oracle_hash(self) -> None:
        self.make_candidate()
        self.value["matrix"][0]["canonical_sha256"]["itch.streaming_reference"] = "0" * 64
        with self.assertRaises(evidence.EvidenceError):
            self.check(candidate_profile=True)

    def test_candidate_streaming_disabled(self) -> None:
        self.make_candidate()
        self.value["enabled_configurations"]["python-debug"] = False
        with self.assertRaises(evidence.EvidenceError):
            self.check(candidate_profile=True)

    def test_candidate_streaming_enablement_omitted(self) -> None:
        self.make_candidate()
        self.value.pop("enabled_configurations")
        self.assertEqual(self.check()["ctest_outcomes"], 36)
        with self.assertRaises(evidence.EvidenceError):
            self.check(candidate_profile=True)

    def test_valid_fixture(self) -> None:
        self.assertEqual(self.check()["ctest_outcomes"], 1)
        self.assertEqual(self.check(working_tree=True)["source_mode"], "working-tree")

    def test_historical_source_is_not_current_source(self) -> None:
        (self.root / "source.cpp").write_bytes(b"changed later\n")
        self.assertEqual(self.check()["source_mode"], "historical-git-blobs")
        with self.assertRaises(evidence.EvidenceError):
            self.check(working_tree=True)

    def test_wrong_source_digest_with_consistent_manifest(self) -> None:
        self.value["frozen_source_sha256"]["source.cpp"] = "0" * 64
        self.value["source_manifest_sha256"] = sha(json.dumps(self.value["frozen_source_sha256"], sort_keys=True).encode())
        self.rejected()

    def test_wrong_source_commit(self) -> None:
        self.value["implementation_commit"] = "0" * 40
        self.rejected()

    def test_wrong_source_manifest(self) -> None:
        self.value["source_manifest_sha256"] = "0" * 64
        self.rejected()

    def test_wrong_artifact(self) -> None:
        (self.root / "build/artifact.whl").write_bytes(b"tampered")
        self.rejected()

    def test_missing_artifact(self) -> None:
        (self.root / "build/artifact.whl").unlink()
        self.rejected()

    def test_wrong_raw_log(self) -> None:
        (self.raw / "debug.log").write_bytes(b"tampered")
        self.rejected()

    def test_wrong_junit_digest(self) -> None:
        self.value["matrix"][0]["junit_sha256"] = "0" * 64
        self.rejected()

    def test_count_contradiction(self) -> None:
        self.value["matrix"][0]["tests"] = 2
        self.rejected()

    def test_junit_summary_cannot_hide_missing_case(self) -> None:
        self.replace_xml(self.xml.replace(b'tests="1"', b'tests="2"'))
        self.value["matrix"][0]["tests"] = 2
        self.value["total_ctest_outcomes"] = 2
        self.rejected()

    def test_junit_failed_case_cannot_hide_behind_summary(self) -> None:
        self.replace_xml(self.xml.replace(b"<system-out>", b'<failure message="broken"/><system-out>'))
        self.rejected()

    def test_skipped_case(self) -> None:
        self.replace_xml(self.xml.replace(b"<system-out>", b"<skipped/><system-out>"))
        self.rejected()

    def test_wrong_canonical(self) -> None:
        self.value["matrix"][0]["canonical_sha256"]["oracle"] = "b" * 64
        self.rejected()

    def test_duplicate_case_name(self) -> None:
        case = self.xml.split(b"<testcase", 1)[1].split(b"</testcase>")[0]
        self.replace_xml(self.xml.replace(b"</testsuite>", b"<testcase" + case + b"</testcase></testsuite>"))
        self.rejected()

    def test_duplicate_configuration(self) -> None:
        self.value["matrix"].append(copy.deepcopy(self.value["matrix"][0]))
        self.rejected()

    def test_total_contradiction(self) -> None:
        self.value["total_ctest_outcomes"] = 2
        self.rejected()

    def test_bool_not_a_count(self) -> None:
        self.value["matrix"][0]["tests"] = True
        self.rejected()

    def test_failed_command(self) -> None:
        self.value["matrix"][0]["build_exit"] = 1
        self.rejected()

    def test_package_failure(self) -> None:
        self.value["package"]["steps"][0]["exit_code"] = 1
        self.rejected()

    def test_package_record_contradiction(self) -> None:
        raw = json.dumps({"different": "record"}).encode()
        (self.raw / "package.json").write_bytes(raw)
        self.value["raw_evidence_sha256"]["package.json"] = sha(raw)
        self.rejected()

    def test_missing_enabled_configuration(self) -> None:
        self.value["enabled_configurations"] = {}
        self.rejected()

    def test_path_traversal(self) -> None:
        self.value["raw_evidence_sha256"] = {"../artifact.whl": sha(b"independent fixture artifact")}
        self.rejected()

    def test_absolute_artifact_path(self) -> None:
        self.value["package"]["artifact_sha256"] = {str(self.root / "build/artifact.whl"): sha(b"independent fixture artifact")}
        self.rejected()

    def test_symlink_escape(self) -> None:
        (self.raw / "outside").symlink_to(self.root / "source.cpp")
        self.value["raw_evidence_sha256"]["outside"] = sha(self.source)
        self.rejected()

    def test_duplicate_json_key(self) -> None:
        self.report.write_text('{"matrix":[],"matrix":[]}')
        with self.assertRaises(evidence.EvidenceError):
            evidence.verify(self.report, self.raw, self.root)

    def test_nonfinite_json(self) -> None:
        for token in ("NaN", "Infinity", "-Infinity"):
            self.report.write_text('{"x":' + token + '}')
            with self.assertRaises(evidence.EvidenceError):
                evidence.verify(self.report, self.raw, self.root)

    def test_dtd_and_entities_rejected(self) -> None:
        self.replace_xml(b'<!DOCTYPE x [<!ENTITY a "abc">]>' + self.xml)
        self.rejected()

    def test_utf16_dtd_cannot_bypass_declaration_check(self) -> None:
        text = '<!DOCTYPE testsuite [<!ENTITY a "unused">]>' + self.xml.decode()
        for encoding in ("utf-16", "utf-16-le", "utf-16-be"):
            with self.subTest(encoding=encoding):
                self.replace_xml(text.encode(encoding))
                self.rejected()

    def test_utf32_dtd_cannot_bypass_declaration_check(self) -> None:
        text = '<!DOCTYPE testsuite [<!ENTITY a "unused">]>' + self.xml.decode()
        for encoding in ("utf-32", "utf-32-le", "utf-32-be"):
            with self.subTest(encoding=encoding):
                self.replace_xml(text.encode(encoding))
                self.rejected()

    def test_malformed_xml(self) -> None:
        self.replace_xml(self.xml[:-2])
        self.rejected()

    def test_size_limits(self) -> None:
        original = evidence.MAX_TOTAL
        try:
            evidence.MAX_TOTAL = 2
            self.rejected()
        finally:
            evidence.MAX_TOTAL = original
        with self.assertRaises(evidence.EvidenceError):
            evidence.Reader().data(self.root / "source.cpp", limit=1)

    def test_cli_failure_is_nonzero(self) -> None:
        self.report.write_text("not JSON")
        run = subprocess.run(["python3", str(SCRIPT), str(self.report), "--raw-root", str(self.raw),
                              "--source-root", str(self.root)], capture_output=True, text=True)
        self.assertEqual(run.returncode, 1)
        self.assertIn("verification failed", run.stderr)


if __name__ == "__main__":
    unittest.main()
