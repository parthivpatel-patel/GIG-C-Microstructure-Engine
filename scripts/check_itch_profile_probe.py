#!/usr/bin/env python3
"""Independent arithmetic/fixture checks for the declared128-live/1024-journal profile.

The C++ probe checks state and reached query faults; this script independently
packs the bytes and derives totals rather than accepting native output as truth.
RSS must be measured by an external wait-accounted child wrapper, not inferred here.
"""
import copy
import hashlib
import json
import struct
import subprocess
import sys
import zlib


def fixture():
    records = []

    def event(kind, locate):
        lengths = {"S": 12, "R": 39, "A": 36, "X": 23}
        return bytearray(kind.encode() + struct.pack(">HH", locate, 0) + (1).to_bytes(6, "big") + bytes(lengths[kind] - 11))

    def system(code):
        p = event("S", 0)
        p[11] = ord(code)
        records.append(p)

    system("O")
    for book, symbol in [(1, b"TEST    "), (2, b"TWO     ")]:
        p = event("R", book)
        p[11:19] = symbol
        p[19:21] = b"QN"
        p[21:25] = struct.pack(">I", 100)
        p[25:34] = b"NC  P N1N"
        p[38] = ord("N")
        records.append(p)
    for index in range(128):
        for book, symbol in [(1, b"TEST    "), (2, b"TWO     ")]:
            p = event("A", book)
            p[11:19] = struct.pack(">Q", 2 * index + book)
            p[19] = ord("B" if book == 1 else "S")
            p[20:24] = struct.pack(">I", 1000)
            p[24:32] = symbol
            p[32:36] = struct.pack(">I", 100 if book == 1 else 200)
            records.append(p)
    for _ in range(7):
        for index in range(128):
            for book in [1, 2]:
                p = event("X", book)
                p[11:19] = struct.pack(">Q", 2 * index + book)
                p[19:23] = struct.pack(">I", 1)
                records.append(p)
    for code in "SQMEC":
        system(code)
    raw = b"".join(struct.pack(">H", len(p)) + p for p in records) + b"\0\0"
    # Independently construct this fixture's one stored DEFLATE block and wrapper.
    assert len(raw) < 65536
    compressed = b"\x1f\x8b\x08\0\0\0\0\0\0\xff\x01" + struct.pack("<HH", len(raw), len(raw) ^ 65535) + raw + struct.pack("<II", zlib.crc32(raw), len(raw))
    assert zlib.decompress(compressed, 31) == raw
    return records, raw, compressed


def verify(result):
    records, raw, compressed = fixture()
    exact = {
        "schema": "gig.synthetic_profile_probe.v1", "orders_per_symbol": 128,
        "books": 2, "records": len(records), "native_records": 2048,
        "journal_records_per_book": 1024, "remaining_per_book": 128 * (1000 - 7),
        "max_orders_per_book": 128, "journal_limit_per_book": 1024,
        "context_lifetime_limit": 4096, "source_limit": 4096,
        "receipt_budget_bytes": 2 * 1024**2, "pmr_budget_bytes": 128 * 1024**2,
        "compressed_bytes": len(compressed), "decompressed_bytes": len(raw),
        "compressed_sha256": hashlib.sha256(compressed).hexdigest(),
        "decompressed_sha256": hashlib.sha256(raw).hexdigest(),
        "restart_equivalent": True, "publication_eligible": True,
        "observed_market_validated": False, "post_destroy_live_bytes": 0,
    }
    for key, value in exact.items():
        assert type(result[key]) is type(value) and result[key] == value, key
    assert result["journal_entry_bytes"] > 0
    assert result["journal_element_bytes"] == 2048 * result["journal_entry_bytes"]
    assert result["journal_element_bytes"] <= result["first_pipeline_peak_pmr"] <= result["restart_coexistence_peak_pmr"] <= result["final_peak_pmr"] <= result["pmr_budget_bytes"]
    assert result["first_pipeline_live_pmr"] < result["coexisting_query_live_pmr"] <= result["coexisting_query_peak_pmr"] <= result["final_peak_pmr"]
    assert result["query_allocation_failures_reached"] >= 2
    assert result["allocations"] > result["query_allocation_failures_reached"]
    assert result["export_canonical_bytes"] > 0
    stop = result["reduced_pmr_stop"]
    assert stop["budget"] == 16 * 1024**2 and 0 < stop["peak"] <= stop["budget"]
    assert 3 < stop["accepted"] < len(records) and stop["framed"] == stop["accepted"] + 1
    assert stop["native"] == stop["accepted"] - 3
    assert result["journal_cap_stop"] == {"tested": True, "limit": 1023, "framed": 2050, "accepted": 2049, "native": 2046, "field": "journal.records"}


def main():
    assert len(sys.argv) in (2,3), "usage: check_itch_profile_probe.py EXECUTABLE [--sanitizer-allocation-profile]"
    if len(sys.argv)==3:
        assert sys.argv[2]=="--sanitizer-allocation-profile"
    process = subprocess.run(sys.argv[1:], capture_output=True, timeout=180, check=True)
    assert len(process.stdout) <= 65536 and not process.stderr
    result = json.loads(process.stdout)
    verify(result)
    bad_models = [("native_records", 2047), ("decompressed_sha256", "0" * 64), ("publication_eligible", False), ("journal_element_bytes", 1), ("post_destroy_live_bytes", 1)]
    for key, value in bad_models:
        wrong = copy.deepcopy(result)
        wrong[key] = value
        try:
            verify(wrong)
        except AssertionError:
            pass
        else:
            raise AssertionError("missed negative control: " + key)
    invalid = subprocess.run([sys.argv[1], "32"], capture_output=True, timeout=30)
    assert invalid.returncode != 0 and b"only declared128-order profile supported" in invalid.stderr
    print(json.dumps({"profile": "128_live_1024_journal_per_book", "independent_checks": "passed", "allocation_profile": "bounded_8_order_sweep_plus_full_128_boundaries" if len(sys.argv)==3 else "full_128_order_sweep", "negative_controls": len(bad_models), "fixture_sha256": result["decompressed_sha256"], "query_allocation_failures_reached": result["query_allocation_failures_reached"], "peak_pmr": result["final_peak_pmr"]}, sort_keys=True))


if __name__ == "__main__":
    main()
