#ifndef SYNC_PIEMON_RUNNER_H_
#define SYNC_PIEMON_RUNNER_H_

#include "PiemonRunner.h"
using namespace piemon;
namespace piemon {
class SyncPiemonRunner : public PiemonRunner
{
public:
    SyncPiemonRunner(queryScanner *fileReader, PiemonCache *globalInfo, 
                   uint32_t parallelNum, PacketType packetType);
    ~SyncPiemonRunner();

    void start(threadpool* pool);
    void stop();
    void join();
    static void* work(void* arg);
    static void*  AccEngineRunner(void* args);
private:
    uint32_t _parallelNum;
    static pthread_t acc_task;
};
}
#endif
