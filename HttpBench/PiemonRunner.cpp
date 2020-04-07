//#define _ENABLE_DEFAULT_POST_METHOD_
#include "PiemonRunner.h"
#include <iostream>
#include <dlfcn.h>
#define LIB_CACULATE_PATH "./libdecoder.so"
using namespace std;
using namespace piemon;


PiemonRunner::PiemonRunner(queryScanner *fileReader, 
               PiemonCache *globalInfo, 
               PacketType packetType) 
{
/*    handle = dlopen(LIB_CACULATE_PATH, RTLD_LAZY);
    dlerror();
    create_fun = (create_t*)dlsym(handle, "create");
    destroy_fun = (destroy_t*)dlsym(handle,"destroy");
    manager = create_fun();
  */
    assert(fileReader);
    assert(globalInfo); 
    _fileReader = fileReader;
    _globalInfo = globalInfo; 
}
PiemonRunner::~PiemonRunner() {}
