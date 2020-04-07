#include "PiemonCache.h"
#include <string.h>
#include <stdlib.h>
#include <iostream>
#include <stdio.h>
using namespace piemon;
using namespace std;

PiemonCache::PiemonCache() {
    atomic_set(&_totalQuery, 0);
    atomic_set(&_successQuery, 0);
    atomic_set(&_connectFailed, 0);
    atomic_set(&_queryFailed, 0);
    atomic_set(&_queryTimeout, 0);

    _matchFailed = 0;

    _spec = NULL;
    _parallelNum = 0;
    _maxRT = -1;
    _maxQPS = -1;
    _maxTIMEOUT = -1;
    _threadNum = 1;
    _fetches = 0;
    _keepAlive = false;
    _limits = -1;

    _rate = 0;
    _seconds = 0;
    _logPath = strdup("piemon_log");
    _help = false;
    _fakehost = NULL;
    _isfakehost = false;
    _is_async_ = 0;  // sync Default
    _host = NULL;
    _port = 0;
    _proj_id = 36;
    _urlDirectory = NULL;
    _maxUriLength = 102400;
	
    time(&_startTime);
    time(&_endTime);
    cmd[0] = 0;
    _stop = false;

    _minResponseTime = 10000;
    _maxResponseTime = 0;
    _totalResponseTime = 0;
    _timeout = 5;
    _microtimeout = 1000;
    _responseTime = NULL;
    _FAKEresponseTime = NULL;

    _noDocsReturn = 0;
    _noDocsFound = 0;
    _totalDocsReturn = 0;
    _totalDocsFound = 0;
    _totalBytesReturn = 0;
    _packetType = HTTP_PACKET;
    _httpPost = false;
}

PiemonCache::~PiemonCache() {
    if (_spec) {
        ::free(_spec);
        _spec = NULL;
    }
    if (_host) {
        ::free(_host);
        _host = NULL;
    }
    if (_FAKEresponseTime) {
        delete[] _FAKEresponseTime;
        _FAKEresponseTime = NULL;
    }
    if (_FAKEresponseTime) {
        delete[] _FAKEresponseTime;
        _FAKEresponseTime = NULL;
    }
}

void PiemonCache::init() {
     //   alog::FileAppender* fileAppender =
     //     dynamic_cast<FileAppender*>(alog::FileAppender::getAppender(_logPath));
     //    _log->setAppender(fileAppender);
 //   if (_logPath) {
//        FILE *fppp;
  //      fppp = fopen(_logPath,"w+");
      //  alog::FileAppender* fileAppender =
      //    dynamic_cast<FileAppender*>(alog::FileAppender::getAppender(_logPath));
     //    _log->setAppender(fileAppender);
//  _log->setAppender(FileAppender::getAppender(_logPath));
//    }
    _FAKEresponseTime = new int[_microtimeout * 10];
    memset(_FAKEresponseTime, 0, sizeof(int) * _timeout * 10);
    for(int v=0;v<_microtimeout * 10;v++){
        _FAKEresponseTime[v]=0;
        }
    _responseTime = new int[_timeout * 10000];
    memset(_responseTime, 0, sizeof(int) * _timeout * 10000);
    for(int v=0;v<_timeout * 10000;v++){
        _responseTime[v]=0;
        }
}
/*
void PiemonCache::match(PiemonPerfCollector &result, uint32_t index, const char *queryStr) {
    _mtx.lock();
    MatchDataMap::iterator it = _matchDataMap.find(index);
    if (it == _matchDataMap.end()) {
        _matchDataMap[index] = result;
    } else if (result != it->second) {
        _matchFailed++;
//	fprintf(fppp, "Match Failed: query-index: %d, query-string: %s \n"
//		   "Last Query: bytesCount %d  docsCount %d  docsFound %d  docsReturn %d \n"
//		   "Curr Query: bytesCount %d  docsCount %d  docsFound %d  docsReturn %d \n", 
//		   index, queryStr,
//		   it->second._bytesCount, it->second._docsCount, it->second._docsFound, it->second._docsReturn,
//		   result._bytesCount, result._docsCount, result._docsFound, result._docsReturn);
        _matchDataMap[index] = result;
    }

    if (result._docsReturn <= 0) {
        _noDocsReturn ++;
    } else {
        _totalDocsReturn += result._docsReturn;
    }
    if (result._docsFound <= 0) {
        _noDocsFound ++;
    } else {
        _totalDocsFound += result._docsFound;
    }
    _totalBytesReturn += result._bytesCount;
    _mtx.unlock();
}
*/
void PiemonCache::recordBytesReturn(int64_t bytesReturn) {
    _mtx.lock();
    _totalBytesReturn += bytesReturn;
    _mtx.unlock();
}

void PiemonCache::recordCommand(int argc, char **argv) {
    strcat(cmd, PIEMON_VERSION);
    for(int i = 1; i<argc; i++) {
        strcat(cmd, (const char *)" ");
        if ((strlen(cmd) + strlen((const char*)argv[i])) >= CMD_LENGTH) {
            printf("Too long parameters!");
            exit(1);
        }
        strcat(cmd, (const char *)argv[i]);
    }
}

void PiemonCache::recordStoptime() {
    time(&_endTime);
}

void PiemonCache::addResponseTime(struct timeval &startTime, 
                                 struct timeval &endTime)
{
    _responseTimeMtx.lock();
    int timeVal = (endTime.tv_sec - startTime.tv_sec) * 10000 +
                  (endTime.tv_usec - startTime.tv_usec) / 100;
    if (timeVal < 0) {
        timeVal = 0;
    }
    _minResponseTime = timeVal < _minResponseTime ? timeVal : _minResponseTime;
    _maxResponseTime = timeVal > _maxResponseTime ? timeVal : _maxResponseTime;
    _totalResponseTime += timeVal;
    if(timeVal >= 0 && timeVal < _microtimeout *10){
        _FAKEresponseTime[timeVal]++;
    }
    if (timeVal >= 0 && timeVal < _timeout * 10000) {
        _responseTime[timeVal]++;
    }
    _responseTimeMtx.unlock();
}

float PiemonCache::getProcessTime(){
    _responseTimeMtx.lock();
    float retV = (float)_totalResponseTime;
    _responseTimeMtx.unlock();
return retV;

}

void PiemonCache::showResult() {
    time_t timeused = _endTime - _startTime;
    int successQuery = atomic_read(&_successQuery);
    printf("--- FROM(%02d/%02d/%02d %02d:%02d:%02d) ", 1 + localtime(&_startTime)->tm_mon, 
           localtime(&_startTime)->tm_mday, 1900 + localtime(&_startTime)->tm_year - 2000,
           localtime(&_startTime)->tm_hour, localtime(&_startTime)->tm_min, localtime(&_startTime)->tm_sec);
    printf("TO(%02d/%02d/%02d %02d:%02d:%02d) ", 1 + localtime(&_endTime)->tm_mon, 
           localtime(&_endTime)->tm_mday, 1900 + localtime(&_endTime)->tm_year - 2000,
           localtime(&_endTime)->tm_hour, localtime(&_endTime)->tm_min, localtime(&_endTime)->tm_sec);
    printf("TIME-USED(%ldh-%ldmin-%lds) ---\n", timeused/3600, timeused%3600/60, timeused%3600%60);

    printf("CMD: %s\n", cmd);
    if (timeused > 0) {
        printf("QPS:                           %.2f\n", (float)successQuery / timeused);
    } else {
        printf("QPS:                           %.2f\n", 0.00);
    }

    if (successQuery > 0) {
        printf("Latency:                       %.2f ms\n",
               (float)_totalResponseTime/successQuery/10.0);
    } else {
        printf("Latency:                       %.2f ms\n", 0.00);
    }

    printf("Query Success Number:          %d\n", successQuery);
    printf("Connect Failed Number:         %d\n", atomic_read(&_connectFailed));
    printf("Query Failed Number:           %d\n", atomic_read(&_queryFailed));
    printf("Query Timeout Number:          %d\n", atomic_read(&_queryTimeout));

    if (_limits < 0 && _packetType == HTTP_PACKET) {
        printf("Match Failed Number:           %d\n", _matchFailed);

        printf("No DocsReturn Number:          %ld (%.2f%%)\n", _noDocsReturn, 
               successQuery > 0 ? 100.0*_noDocsReturn/successQuery : 0.00);
        printf("Average DocsReturn Number:     %.2f\n", (successQuery - _noDocsReturn) > 0 ? 
               (double)_totalDocsReturn/(successQuery - _noDocsReturn) : 0.000);
        printf("No DocsFound Number:           %ld (%.2f%%)\n", _noDocsFound, 
               successQuery > 0 ? 100.0*_noDocsFound/successQuery : 0.00);
        printf("Average DocsFound Number:      %.2f\n", (successQuery - _noDocsFound) > 0 ? 
               (double)_totalDocsFound/(successQuery - _noDocsFound) : 0.00);
    } 

    printf("Average Return Length(Bytes):  %ld\n", successQuery > 0 ? 
           _totalBytesReturn/successQuery : 0);

    printf("Min Response Time:             %.1f ms\n", (float)_minResponseTime/10);
    printf("Max Response Time:             %.1f ms\n", (float)_maxResponseTime/10);
    int totNum = 0;
    int percent[] = {25, 50, 75, 90, 95, 99};
    int index = 0;
    float maxTime = 0.0;
    int lastNum = 0;
    if(_microtimeout != -1){
    for (int i = 0; index < 6 && i<_microtimeout * 10; i++) {
        totNum += _responseTime[i];
        if (totNum > 0 && totNum >= 
            (successQuery)/100*percent[index]) 
        {
            if(lastNum != totNum) {
                maxTime = (float)i/10;
                lastNum = totNum;
            }
            printf("%d Percentile:                 %.1f ms\n", percent[index], maxTime);
            index ++;
            if (index > 5) break;
        }
    }
    for (; index <= 5; index++) {
        printf("%d Percentile:                 %.1f ms\n", percent[index], maxTime);
    }
    printf("\n");
    }
    if(_microtimeout !=-1)
    { 
        int wholeCOUNT = 0;
       // printf("Here is the detail data of Rate time\n");
        for(int k=0;k<_microtimeout;k++){
            int onesecnum = 0;
        for(int b=0;b<10;b++){
            onesecnum += _responseTime[10*k+b];
        }
        wholeCOUNT = wholeCOUNT+onesecnum;
    }
    }
    else {
    for (int i = 0; index < 6 && i<_timeout * 10000; i++) {
        totNum += _responseTime[i];
        if (totNum > 0 && totNum >= 
            (successQuery)/100*percent[index]) 
        {
            if(lastNum != totNum) {
                maxTime = (float)i/10;
                lastNum = totNum;
            }
            printf("%d Percentile:                 %.1f ms\n", percent[index], maxTime);
            index ++;
            if (index > 5) break;
        }
    }
    for (; index <= 5; index++) {
        printf("%d Percentile:                 %.1f ms\n", percent[index], maxTime);
    }
    printf("\n");
}
}
