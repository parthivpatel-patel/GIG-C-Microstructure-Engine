#include "gig/itch/streaming.hpp"
#include "gig/memory/tracked_resource.hpp"
#include "support/itch_gzip_fixture.hpp"

#include <iostream>
#include <string>

namespace {
using namespace gig::itch;
using namespace gig::itch::test;

StreamingConfig configuration(std::span<const std::byte> raw,
                              std::span<const std::byte> compressed) {
    auto reconstruction = config();
    reconstruction.source.provenance.sha256 = sha256(raw);
    const auto digest = hex_digest(sha256(raw));
    reconstruction.initialization.fixture_sha256 =
        *gig::Digest::make({digest.data(), digest.size()}).data;
    StreamingConfig result{reconstruction, {}, {}, sha256(compressed)};
    result.gzip.output_buffer_bytes = 65536;
    return result;
}

void run() {
    // Byte authoring and stored-block CRC framing are independent of production
    // decode/decompression. Fixtures and baseline strings use the test allocator,
    // not the deliberately faulted engine resource.
    const auto raw = framed_records(streaming_records());
    const auto compressed = stored_gzip(raw);
    const auto settings = configuration(raw, compressed);
    gig::TrackedResource resource(std::pmr::get_default_resource(), 128 * 1024 * 1024);
    std::size_t checkpoint_sites = 0;
    std::size_t depth_sites = 0;

    {
        auto created = StreamingReconstructor::create(settings, &resource);
        check(bool(created), "query-failure fixture creation");
        auto& stream = *created.data;
        check(!stream.pause_after(10), "declare accepted query boundary");
        std::size_t offset = 0;
        while (offset < compressed.size()) {
            const auto fed = stream.feed(
                std::span<const std::byte>(compressed).subspan(offset));
            offset += fed.consumed;
            check(!fed.error, "query-failure fixture feed");
            if (fed.paused) break;
            check(fed.consumed != 0, "query-failure fixture progress");
        }
        check(stream.summary().paused && stream.summary().accepted_records == 10,
              "exact logical prefix before export failures");
        const auto& source = stream.reconstruction();
        const auto source_before = source.summary();
        const auto context_before = source.context().summary();
        const auto native_before = state(source);
        const auto prefix_before = stream.summary().accepted_prefix_sha256;
        const auto receipt_count = source.receipts().size();
        const auto live_before = resource.stats().live_bytes;
        // This test code identity is a declared descriptor-control sentinel, not
        // a claim that the fixture owns authenticated implementation provenance.
        const auto code = *gig::Digest::make(std::string(64, '1')).data;
        const auto assert_unchanged = [&] {
            check(source.summary() == source_before, "query cannot advance source");
            check(source.context().summary() == context_before,
                  "query cannot advance context");
            check(state(source) == native_before, "query cannot mutate native state");
            check(stream.summary().accepted_prefix_sha256 == prefix_before,
                  "query cannot change accepted-frame identity");
            check(source.receipts().size() == receipt_count,
                  "query cannot append source receipts");
            check(resource.stats().live_bytes == live_before,
                  "failed query cannot retain resource storage");
        };

        const auto checkpoint_begin = resource.stats().attempts;
        const auto expected = stream.checkpoint(code);
        check(bool(expected), "checkpoint baseline success");
        checkpoint_sites = resource.stats().attempts - checkpoint_begin;
        check(checkpoint_sites > 0, "actual checkpoint allocation sites reached");
        for (std::size_t site = 0; site < checkpoint_sites; ++site) {
            resource.fail_after(site);
            const auto failed = stream.checkpoint(code);
            resource.disable_failure();
            check(!failed && failed.error.code == gig::ErrorCode::resource_exhausted,
                  "each reached checkpoint allocation failure is explicit");
            assert_unchanged();
            check(!stream.verify_checkpoint(*expected.data, code),
                  "exact checkpoint retry succeeds after disabling fault");
        }

        for (std::size_t index = 0; index < 2; ++index) {
            const auto* engine = source.engine(index);
            const auto depth_begin = resource.stats().attempts;
            {
                const auto depth = engine->depth(16);
                check(bool(depth), "depth-query baseline success");
            }
            const auto sites = resource.stats().attempts - depth_begin;
            check(sites > 0, "actual per-book depth allocation sites reached");
            depth_sites += sites;
            for (std::size_t site = 0; site < sites; ++site) {
                resource.fail_after(site);
                const auto failed = engine->depth(16);
                resource.disable_failure();
                check(!failed && failed.error.code == gig::ErrorCode::resource_exhausted,
                      "each reached depth allocation failure is explicit");
                assert_unchanged();
            }
        }
    }
    check(resource.stats().live_bytes == 0 && resource.stats().live_blocks == 0,
          "query-failure fixture releases all engine storage");
    std::cout << "checkpoint_allocation_sites=" << checkpoint_sites
              << " depth_allocation_sites=" << depth_sites
              << " pmr_peak_bytes=" << resource.stats().peak_bytes
              << " live_bytes_after_destroy=" << resource.stats().live_bytes << '\n';
}
} // namespace

int main() {
    try {
        run();
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
