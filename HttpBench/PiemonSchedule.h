#ifndef PIEMON_SCHEDULE_H_
#define PIEMON_SCHEDULE_H_

#include "PiemonCache.h"
#include "PiemonRunner.h"
#include <pthread.h>
#include "MessageReader.h"
#include "LogManager.h"
#include "ThreadPool/threadpool.h"
using namespace NewLog;
using namespace piemon;
namespace piemon {
class PiemonSchedule 
{
public:
    PiemonSchedule(queryScanner *fileReader, PiemonCache *globalInfo);
    ~PiemonSchedule();
public:
    void run();
    void stop();
    void stop_pool();
    void InertOneWorker(PiemonRunner* _worker,int _offset);
    void DumpAllWorkers();
    void StopSomeWorkers(int num);
    void TurboSomeWorkers(int &total_thread_num,int times);
    void ModifyParallel(string message_val,int  &total_thread_num);
    void ModifyRateWorkers(int targetQps);
    int calParallelByRate(int rate,int rtt);
    int DumpWorkerNum();
    static void stopRun();
    static void checkFetchFinish();
    static void* counting_loop_thread(void* args);
    static void*  DumpQpsPerSec(void* args);
    static void*  AccEngineRunner(void* args);
    int insert_record(const int qps,const int thread);
    int Init_Monitor();

private:
    void runParallel(threadpool* pool);
    void runRate();
    void showResult();

private:
    PiemonCache *_globalInfo;
    MessageReader *_MessageReader;
    PiemonRunner **_workers;
    int _workerNum;
    bool _stop;
    string message_val;
    long _interval;
    queryScanner  *_fileReader;

    struct Record
    {
    int _qps_to_write;
    int _thread_to_write;
    struct Record* next;
    };

    struct parallelWorkerLink
    {
    int _offset;
    time_t _createtime;
    PiemonRunner* SingleWorker;
    struct parallelWorkerLink* next;
    };    
    struct parallelWorkerLink* Worker_head;
    struct parallelWorkerLink* Worker_tail;
    static struct Record* output_head;
    static struct Record* output_tail;
	struct threadpool* apool;
    static int current_qps;
    static int current_parallel;
    static int TargetQps;
    static pthread_mutex_t output_mutex;
    static pthread_t output_task;
    static pthread_t qps_task;
    static pthread_t acc_task;
    LogManager* Newlog;
    LogManager* Newlog2;
};
}

#endif
