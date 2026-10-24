#include <charconv>
#include <iostream>
#include <string_view>
#include "fixtures/synthetic/phase2_workload.hpp"

int main(int argc,char** argv) {
    try {
        if(argc!=3)throw std::invalid_argument("usage: count seed");
        const auto argument=[](const char* text){
            const std::string_view input(text);std::uint64_t value{};
            const auto result=std::from_chars(input.data(),input.data()+input.size(),value);
            if(result.ec!=std::errc{} || result.ptr!=input.data()+input.size())throw std::invalid_argument("invalid argument");
            return value;
        };
        const auto count=argument(argv[1]);if(count>2048)throw std::invalid_argument("count range");
        const auto workload=gig::fixtures::phase2_workload(static_cast<std::size_t>(count),argument(argv[2]));
        const auto& generator=*workload.adds.front().metadata.provenance.lineage.items[0];
        std::cout<<generator.operation.view()<<' '<<generator.version.view()<<' '<<workload.adds.front().metadata.provenance.dataset.data->version.data->view()<<' '<<workload.config.streams.items[0]->dataset_version.view()<<'\n';
        for(std::size_t i=0;i<workload.adds.size();++i){
            const auto& order=std::get<gig::AddOrder>(workload.adds[i].payload);
            if(workload.replay[i].payload!=workload.adds[i].payload ||
               std::get<gig::CancelOrder>(workload.cancels[i].payload).order_id!=order.order_id ||
               std::get<gig::BookExecution>(std::get<gig::Trade>(workload.executions[i].payload).details).resting_order_id!=order.order_id)
                throw std::runtime_error("inconsistent fixture payloads");
            std::cout<<order.order_id.value()<<' '<<static_cast<unsigned>(order.side)<<' '
                     <<order.price_ticks.value()<<' '<<order.quantity.value()<<'\n';
        }
    } catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
