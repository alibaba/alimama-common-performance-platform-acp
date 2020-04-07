#include "PiemonSchedule.h"
#include "SyncPiemonRunner.h"
#include <iostream>
#include <sys/time.h>
  #include <cstdlib>
using namespace std;
using namespace piemon;
piemon::PiemonSchedule::Record* piemon::PiemonSchedule::output_head = NULL;
piemon::PiemonSchedule::Record* piemon::PiemonSchedule::output_tail = NULL;
int piemon::PiemonSchedule::current_qps=0;
int piemon::PiemonSchedule::TargetQps=0;
int piemon::PiemonSchedule::current_parallel=0;
pthread_mutex_t piemon::PiemonSchedule::output_mutex;
pthread_t piemon::PiemonSchedule::output_task;
pthread_t piemon::PiemonSchedule::qps_task;
pthread_t piemon::PiemonSchedule::acc_task;
PiemonSchedule::PiemonSchedule(queryScanner *fileReader, PiemonCache *globalInfo) {
    _fileReader = fileReader;
    _globalInfo = globalInfo;
    _MessageReader = new MessageReader();
    _MessageReader->Init(globalInfo->_proj_id);
    _workers = NULL;
    _stop = true;
    _interval = 1000;
    Worker_head = NULL;
    message_val = "";
    Worker_tail = NULL;
	apool = threadpool_init(10, 20); 
    Newlog = new LogManager();
    int aa1 = Newlog->Init("/tmp/PIEMON_RET");
    Newlog2 = new LogManager();
    int aa2 = Newlog2->Init("/tmp/PIEMON_RET_1");
    printf("CREATE FILE:%d\t%d\n",aa1,aa2);
}

PiemonSchedule::~PiemonSchedule() {
    delete Newlog;
    if (_workers) {
        for (int i = 0; i < _globalInfo->_threadNum; i++) {
            if (_workers[i]) {
                delete _workers[i];
                _workers[i] = NULL;
            }
        }
        delete[] _workers;
        _workers = NULL;
    }
}
int PiemonSchedule::Init_Monitor(){
     pthread_mutex_init(&output_mutex,NULL);
//   pthread_create(&output_task,NULL,counting_loop_thread,this);
     pthread_create(&qps_task,NULL,DumpQpsPerSec,this); 
     pthread_create(&acc_task,NULL,AccEngineRunner,this); 
     return 0;
}
void* PiemonSchedule::counting_loop_thread(void * args){
     struct Record* One_Record = NULL;
     while(1){
         pthread_mutex_lock(&output_mutex);
         if(output_head == NULL){
             pthread_mutex_unlock(&output_mutex);
             sleep(2);
         }
         else{
             One_Record = output_head;
//           printf("Current Qps is:%d\n",One_Record->_qps_to_write);
//           printf("Current Parallel is%d\n",One_Record->_thread_to_write);
             current_qps = One_Record->_qps_to_write;
             current_parallel = One_Record->_thread_to_write;
             output_head = output_head->next;
             pthread_mutex_unlock(&output_mutex);
             sleep(2);
             }
     }
}
int PiemonSchedule::insert_record(const int qps,const int thread){
    pthread_mutex_lock(&output_mutex);
    struct Record* new_record = (struct Record*)malloc(sizeof(struct Record));
    new_record->_qps_to_write = qps;
    new_record->_thread_to_write = thread;

    if(output_head == NULL){
        output_head = new_record; 
        output_tail = new_record;
        new_record->next = NULL; 
    }
    else{
        output_tail->next = new_record;
        new_record->next = NULL;
        output_tail = new_record;
    }
    pthread_mutex_unlock(&output_mutex);
}
void PiemonSchedule::run() {
	struct threadpool *pool = threadpool_init(10, 20);
    _stop = false;
    if (_globalInfo->_fetches > 0) {
        struct timeval *tmpTime = 
            (struct timeval *)malloc(sizeof(struct timeval));
        gettimeofday(tmpTime, NULL);
    } else if (_globalInfo->_seconds > 0) {
        struct timeval *tmpTime = 
            (struct timeval *)malloc(sizeof(struct timeval));
        gettimeofday(tmpTime, NULL);
        tmpTime->tv_sec += _globalInfo->_seconds;
    } else if (_globalInfo->_seconds == 0) {
        cerr<<"Wrong parameter, you must specify -s or -f!"<<endl;
    }
    int retCode =Init_Monitor();
    if (_globalInfo->_is_async_ == 1) { //async
//        runRate();
		runParallel(pool);
    } else if (_globalInfo->_is_async_ == 0){ //sync
      //  int paa = calParallelByRate(_globalInfo->_rate);
        _globalInfo->_parallelNum = 1;
        runParallel(pool);
        //runRate();
    } else {
        cerr<<"Wrong parameter, you must specify -p or -f!"<<endl;
    }
    struct timeval oldtime; 
    gettimeofday(&oldtime, NULL);
    int oldqps = 0;
    int currentqps = 0;
    int fflag = 0;
    int testflag=0;
    int gcounter = 0;
    int only_flag= 0;
    int first_flag = 0;
    int fff_flag = 0;
    int parallel = 0;
    int timess = 1;
    int total_thread_num =1;
    int maxqps =0;
    int last_qps = 0;
    int sss = 0;
    int paramm =0;
    int* press_map = new int[5];
    memset(press_map,0,5*sizeof(int));
    if(_globalInfo->_is_async_ == 1){
        while(!_stop){
            struct timeval exeTime;
            gettimeofday(&exeTime, NULL);
            message_val.clear();
            int sn= _MessageReader->AsyncPoll(message_val);
            if(sn == 0){
                 cout<<"detect message"<<endl;
                 cout<<message_val<<endl;
                 TargetQps = std::atoi(message_val.c_str());
                 _globalInfo->_rate = TargetQps;
                 stop_pool();
                 gettimeofday(&oldtime, NULL);
                 char val[50];
                 memset(val,0,50*sizeof(char));
                 snprintf(val,50,"%s\t%s\t%d\n",message_val.c_str(),"test",oldtime.tv_sec);
                 Newlog2->WriteOneLog(val);
            }
        }
    } //sync
    else{
        while (!_stop) {
            struct timeval exeTime;
            gettimeofday(&exeTime, NULL);
            if(first_flag ==0 && exeTime.tv_sec-oldtime.tv_sec<3){
                continue;
            }    // preheat for 3 seconds 
            else if(first_flag ==0){
                first_flag = 1;
                sss = atomic_read(&_globalInfo->_successQuery);
                paramm = calParallelByRate(_globalInfo->_rate,sss);
                for(int x=0;x<paramm;x++){
                    TurboSomeWorkers(total_thread_num,1);
                }
                gettimeofday(&oldtime, NULL);
                continue;
            } // start 80% threads
            else{
                int s = atomic_read(&_globalInfo->_successQuery);
                if(exeTime.tv_sec-oldtime.tv_sec == 2){
                    int micro_sec = exeTime.tv_usec-oldtime.tv_usec; 
                    float during_time = 2+(float((int(micro_sec*100/1000000))/100)); 
                    int reload_qps = s-last_qps;
                    last_qps = s;
                    if(only_flag == 0){
                        int qqq = (s-sss)/2;
                        parallel = qqq/(_globalInfo->_parallelNum+paramm);
                        if(parallel == 0)
                            parallel=1;
                        int total_parallel = _globalInfo->_rate/parallel-_globalInfo->_parallelNum-paramm;
                        if(total_parallel<3){
                            press_map[0] = 1; 
                            press_map[1] = 1;
                            press_map[2] = 1;
                        }
                        press_map[0] = int(total_parallel*0.7);
                        press_map[1] = int(total_parallel*0.15);
                        press_map[2] = int(total_parallel*0.05);
                        only_flag=1;
                    }
                    if(!fff_flag){
                        currentqps = int((s-oldqps)/5);
                        fff_flag =1;
                    }
                    else{
                        currentqps = int((s-oldqps)/during_time); 
                    }
                    oldqps = s;
                    gettimeofday(&oldtime, NULL);
                    maxqps = maxqps > currentqps ? maxqps : currentqps;
                    if(currentqps - _globalInfo->_rate < -20){
                        if(maxqps > _globalInfo->_rate){
                            continue;
                    }
                    if(press_map[timess]>1){
                        for(int x=0;x<press_map[timess];x++){
                            TurboSomeWorkers(total_thread_num,1);
    
                        }
                        timess++;
                    }
                    else{
                        int qps_perPar = current_qps/total_thread_num;
                        if(qps_perPar == 0){
                            continue;
                        }
                    int nnTinc = (_globalInfo->_rate- current_qps)/qps_perPar;
                    TurboSomeWorkers(total_thread_num,nnTinc);
                    }
                } 
            }
            message_val.clear();
            int sn= _MessageReader->AsyncPoll(message_val);
            if(sn == 0){
                cout<<"detect message"<<endl;
                cout<<message_val<<endl;
                TargetQps = std::atoi(message_val.c_str());
                ModifyParallel(message_val,total_thread_num);
                gettimeofday(&oldtime, NULL);
                char val[50];
                memset(val,0,50*sizeof(char));
                snprintf(val,50,"%s\t%s\t%d\n",message_val.c_str(),"test",oldtime.tv_sec);
                Newlog2->WriteOneLog(val);
            }
        }
    }
    }
}

void* PiemonSchedule::AccEngineRunner(void * args){
    PiemonSchedule* ld = (PiemonSchedule*)args;
    //new code for rt calculate
    while(true){
        sleep(1);
        float processTime = ld->_globalInfo->getProcessTime();
        int sucQ = atomic_read(&ld->_globalInfo->_successQuery);
        if(sucQ == 0){
            std::cout<<"NO RETURN"<<std::endl;
        }
    else{
        std::cout<<"RT: "<<(float)(processTime/sucQ/10.0)<<std::endl;
    }
    std::cout<<"PAR:"<<ld->DumpWorkerNum()<<std::endl;
    }
}



void* PiemonSchedule::DumpQpsPerSec(void * args){
    PiemonSchedule* ld = (PiemonSchedule*)args;
    struct timeval begintime;
    struct timeval endtime;
    struct timeval tmptime;
    while(1){
        int beg = atomic_read(&ld->_globalInfo->_successQuery);
        gettimeofday(&begintime, NULL);
        sleep(1);
        int end = atomic_read(&ld->_globalInfo->_successQuery);
        gettimeofday(&endtime, NULL);
        int micro_sec = endtime.tv_usec-begintime.tv_usec; 
        float during_time = 1+(float((int(micro_sec*100/1000000))/100));
        pthread_mutex_lock(&output_mutex);
        int qps = int((end-beg)/during_time);
        int paral = ld->DumpWorkerNum();
        current_qps = qps;
        current_parallel = paral;

        printf("CURRENT-QPS:%d\n",qps);
        gettimeofday(&tmptime, NULL);
        char val[50];
        memset(val,0,50*sizeof(char));
        snprintf(val,50,"%d\t%d\t%d\n",qps,paral,tmptime.tv_sec);
        ld->Newlog->WriteOneLog(val);
        pthread_mutex_unlock(&output_mutex);
    }
}


void PiemonSchedule::ModifyParallel(string message_val,int &total_thread_num){
    int TargetQps = std::atoi(message_val.c_str());
    int sQps = 0;
    int eQps = 0;
    pthread_mutex_lock(&output_mutex);
    if(current_parallel ==0)
        return;
    int qps  = current_qps/current_parallel;
    if(qps == 0)
        return; 
    int cur_qps = current_qps;
    pthread_mutex_unlock(&output_mutex);
    if(TargetQps> cur_qps){    //turbo
        int NeedToBoost = int((TargetQps - cur_qps)/qps);
        printf("BOOST:--%d---%d\n",NeedToBoost,current_qps);
        TurboSomeWorkers(total_thread_num,NeedToBoost);
        sleep(2);
        bool Level_boost = false;
        while(!Level_boost){
        pthread_mutex_lock(&output_mutex);
        if(abs(TargetQps - current_qps)>50 && current_qps<TargetQps){
            pthread_mutex_unlock(&output_mutex);
            sQps = atomic_read(&_globalInfo->_successQuery);
            sleep(1);
            eQps = atomic_read(&_globalInfo->_successQuery);
            int nn2Turbo = (eQps-sQps)/total_thread_num;
            if(total_thread_num ==0 | nn2Turbo==0){
                 return;
            }
            int nn3Turbo = (TargetQps-current_qps)/nn2Turbo;
            TurboSomeWorkers(total_thread_num,nn3Turbo);
            sleep(1);
        }
        else{
            pthread_mutex_unlock(&output_mutex);
            Level_boost =true;
            }
        } 
    }
    else{     //stop
        int NeedToDecline = int((cur_qps-TargetQps)/qps);
        printf("DECLINE--%d\n",NeedToDecline);
        for(int v =0;v<NeedToDecline;v++){StopSomeWorkers(1);total_thread_num--;}
        bool Level_dec = false;
        while(!Level_dec){
            if(abs(TargetQps - current_qps)>50 && current_qps>TargetQps){
            // new code for fast decline qps
            total_thread_num = total_thread_num==0?1:total_thread_num;
            int everyParQps = current_qps/total_thread_num;
            int needtodeclien = int(abs(TargetQps - current_qps)/everyParQps);
            // new code for fast decline qps end
            for(int v=0;v<int(needtodeclien*0.8);v++){
                StopSomeWorkers(1);
                total_thread_num--;}
        sleep(1);
        }
            else{
                Level_dec = true;
                }
        }
    }
}

void PiemonSchedule::runParallel(threadpool* pool) {
    int parallelNum = _globalInfo->_parallelNum;
    int threadNum = _globalInfo->_threadNum;
    int averageParallelNum = parallelNum / threadNum;
    int extraParallelNum = parallelNum % threadNum;
    _workers = new PiemonRunner*[threadNum];
    memset(_workers, 0, sizeof(PiemonRunner*) * threadNum);
    for (int i = 0; i < threadNum; i++, extraParallelNum--) {
        int tiny = extraParallelNum > 0 ? 1 : 0;
        if (averageParallelNum + tiny <= 0) {
            break;
        }
        _workers[i] = new SyncPiemonRunner(_fileReader, _globalInfo, 
                averageParallelNum + tiny, _globalInfo->_packetType);
        _workers[i]->start(pool);
        InertOneWorker(_workers[i],i+1);
        //InertOneWorker(_workers[i],i+2);
    }
}

void PiemonSchedule::InertOneWorker(PiemonRunner* _worker,int _offset){

        struct parallelWorkerLink* one_link = (struct parallelWorkerLink*)malloc(sizeof(struct parallelWorkerLink));
        one_link->_offset = _offset;
        one_link->SingleWorker = _worker;
        struct timeval thistime;
        gettimeofday(&thistime, NULL); 
        one_link->_createtime = thistime.tv_sec;
        one_link->next = NULL;

        if(Worker_head == NULL)
            Worker_head = one_link;
        if(Worker_tail == NULL)
            Worker_tail = one_link;
        if(Worker_tail !=NULL){
            Worker_tail->next = one_link;
            Worker_tail = one_link;       
        }
}

void PiemonSchedule::DumpAllWorkers(){
    while(Worker_head!=NULL){
        printf("This is the %dth Worker!\n",Worker_head->_offset);
        printf("Create Time is: %d\n\n\n\n",Worker_head->_createtime);
        Worker_head = Worker_head->next;
    }
}

int PiemonSchedule::DumpWorkerNum(){
    int fen=0;
    struct parallelWorkerLink* only_point = (struct parallelWorkerLink*)malloc(sizeof(struct parallelWorkerLink));
    only_point = Worker_head;
    if(Worker_tail !=NULL && Worker_head !=NULL){
        while(only_point !=NULL){
            if(Worker_tail == Worker_head){
                fen++;
                return fen;
            }
        fen++;
        only_point = only_point->next;
        }
    return fen;
    }
    else
    return 0;
}

void PiemonSchedule::StopSomeWorkers(int num){
    while(Worker_head !=NULL && num >0){
        Worker_head->SingleWorker->stop();
        Worker_head->SingleWorker->join();
        Worker_head = Worker_head->next;
        num--;
    }
}

void PiemonSchedule::TurboSomeWorkers(int &total_thread_num,int times){
      for(int j=0;j<times;j++){
          total_thread_num++;
          PiemonRunner* _workerss = new SyncPiemonRunner(_fileReader, _globalInfo,1, _globalInfo->_packetType);
          _workerss->start(apool);
          InertOneWorker(_workerss,total_thread_num);
      }
}

void PiemonSchedule::ModifyRateWorkers(int targetQps){
	/*
    _globalInfo->_rate = _globalInfo->_rate+targetQps; 
         Worker* tmpWorker;
        tmpWorker = new RateWorker(_fileReader, _globalInfo, 
                targetQps, _globalInfo->_packetType);
    tmpWorker->start();

*/
}


//stop for -s
void PiemonSchedule::stopRun() {
}

//stop for -f
void PiemonSchedule::checkFetchFinish() {
}

void PiemonSchedule::stop() {
    _globalInfo->_stop = true;
    _globalInfo->recordStoptime();
    usleep(100000);
    for (int i = 0; i < _globalInfo->_threadNum; i++) {
        if (_workers[i]) {
            _workers[i]->stop();
            _workers[i]->join();
        }
    }
    _stop = true;
    //DumpAllWorkers();
    showResult();
}
void PiemonSchedule::stop_pool() {
    usleep(100000);
    for (int i = 0; i < _globalInfo->_threadNum; i++) {
        if (_workers[i]) {
            _workers[i]->stop();
            _workers[i]->join();
        }
    }
    usleep(500000);
    for (int i = 0; i < _globalInfo->_threadNum; i++) {
        if (_workers[i]) {
            delete _workers[i];
            _workers[i] = NULL;
        }
    }
    delete[] _workers;
    _workers = NULL;
    usleep(100000);
    struct timeval *tmpTime =
        (struct timeval *)malloc(sizeof(struct timeval));
    gettimeofday(tmpTime, NULL);
    tmpTime->tv_sec += _globalInfo->_seconds;
}

int PiemonSchedule::calParallelByRate(int rate,int rtt){
    if(rtt == 0)
        return 0;
    int rt = int(3000/rtt);
    if (rt == 0)
        return 0;
    int per_para = int(1000/rt);
    if(per_para == 0)
        return 0; 
    return int((rate/per_para)*0.8);
    }
void PiemonSchedule::showResult() {
    _globalInfo->showResult();
}
