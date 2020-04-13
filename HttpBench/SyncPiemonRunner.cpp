#include "SyncPiemonRunner.h"
#include "httpinterface.h"
using namespace piemon;
pthread_t SyncPiemonRunner::acc_task;
SyncPiemonRunner::
SyncPiemonRunner(queryScanner *fileReader, PiemonCache *globalInfo, 
               uint32_t parallelNum, PacketType packetType) 
    : PiemonRunner(fileReader, globalInfo, packetType) 
{
    _parallelNum = parallelNum;
}

SyncPiemonRunner::~SyncPiemonRunner() {
}

void* SyncPiemonRunner::work(void* arg)
{
    char *p = (char*) arg;
    printf("threadpool callback fuction : %s.\n", p);
    sleep(1);
}


void* SyncPiemonRunner::AccEngineRunner(void * args){
    SyncPiemonRunner* thisWorker = (SyncPiemonRunner*)args;
    int32_t queryIndex = 0;
	while(1){
    char *uri = (char *)malloc(thisWorker->_globalInfo->_maxUriLength);
    if (!thisWorker->_fileReader->ScanOneQuery((char *)uri, thisWorker->_globalInfo->_maxUriLength, queryIndex))
    {
        free(uri);
        cerr<<"Read query failed!"<<endl;
        exit(-1);
    }
	string wholeUrl = string(thisWorker->_globalInfo->_spec)+string(uri);
	
	struct timeval startTime;
    gettimeofday(&startTime, NULL);
	int retcode = queryF(wholeUrl.c_str());
	struct timeval endTime;
    gettimeofday(&endTime, NULL);
	thisWorker->_globalInfo->addResponseTime(startTime,endTime);
	if(retcode == 0){
        atomic_inc(&thisWorker->_globalInfo->_successQuery);
		  }
	}
}


void SyncPiemonRunner::start(threadpool* pool) {

pthread_create(&acc_task,NULL,AccEngineRunner,this);

//threadpool_add_job(pool, work, const_cast<char*>("1"));
	
}

void SyncPiemonRunner::stop() {
}
void SyncPiemonRunner::join() {
}



