#ifndef PIEMON_PERF_COLLECTOR_H_
#define PIEMON_PERF_COLLECTOR_H_

#include <sys/types.h>
#include <stdint.h>

namespace piemon{
class PiemonPerfCollector
{
public:
    PiemonPerfCollector(uint32_t bytesCount = 0, uint32_t docsFound = 0,
           uint32_t docsCount = 0, uint32_t docsReturn = 0);
    ~PiemonPerfCollector();
public:
    uint32_t _bytesCount;
    uint32_t _docsFound;
    uint32_t _docsCount;
    uint32_t _docsReturn;

    bool operator==(const PiemonPerfCollector& res) const;
    bool operator!=(const PiemonPerfCollector& res) const;
    void show();
};
}

#endif
