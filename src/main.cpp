#include <iostream>
#include <string_view>
#include "fixtures/synthetic/replay_events.hpp"
int main(int argc,char** argv) {
    try {
        if (argc>2 || (argc==2 && std::string_view(argv[1])!="--canonical")) {
            std::cerr << "usage: gig_engine_demo [--canonical]\n";return 2;
        }
        auto replay=gig::fixtures::take(gig::ReplayEngine::create(gig::fixtures::rules(),gig::fixtures::replay_config()));
        gig::fixtures::canonical_workflow(replay);
        if (const auto e=replay.book().check_invariants()) {std::cerr << e.field << '\n';return 1;}
        if (argc==2) std::cout << gig::fixtures::take(replay.canonical()) << '\n';
        else std::cout << "GIG C++ Microstructure Engine: Phase 2 deterministic replay ready\n"
                       << "SYNTHETIC fixture: orders=" << replay.book().order_count()
                       << " remaining_lots=" << replay.book().remaining()
                       << " journal_records=" << replay.journal_size() << '\n';
        return 0;
    } catch (const std::exception& error) {std::cerr << error.what() << '\n';return 1;}
}
