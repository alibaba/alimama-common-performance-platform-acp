#ifndef PIEMON_RUNNER_H_
#define PIEMON_RUNNER_H_
//#define URI_LENGTH 2048

#include <pthread.h>
#include <unistd.h>
#include <stdio.h>
#include <execinfo.h>
#include <signal.h>
#include <stdint.h>
#include <stdlib.h>
#include <limits.h>

#include "PiemonCache.h"
#include "queryScanner.h"
//#include "IFileReader.h"
#include <assert.h>
#include "decoderManager.h"
#include "ThreadPool/threadpool.h"

//#include <sys/uio.h>

using namespace piemon;
namespace piemon {

class PiemonRunner 
{
public:
    PiemonRunner(queryScanner *fileReader, 
           PiemonCache *globalInfo, PacketType packetType);
    virtual ~PiemonRunner();
    
public:
    virtual void start(threadpool* pool) = 0;
    virtual void stop() = 0;
    virtual void join() = 0;

//    void doConnect();
//    void doRequest();
//    static void doStaticConnect();
private:
//    bool checkFinish();

protected:
    queryScanner *_fileReader;
    PiemonCache *_globalInfo;
    decoderManager *manager;
    PacketType _packetType;
    void *handle;
    char *error;
    create_t* create_fun;
    destroy_t* destroy_fun;
};
}

#endif
