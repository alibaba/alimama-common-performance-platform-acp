#ifndef PIEMON_CACHE_H_
#define PIEMON_CACHE_H_ 

#include <stdint.h>
#include "atomic.h"
#include "PiemonLock.h"
#include "PiemonPerfCollector.h"
#include <map>
#define PIEMON_VERSION "PIEMON_2020_0331_"
#define CMD_LENGTH 10240

#define HELPINFO "===============If has any problems,contact =====================\n"       \
    "usage: ./"                    \
    PIEMON_VERSION                                                      \
    "[-r rate(cycletime)]\n"                           \
    "[-s seconds ] [-f fetches number]\n"                               \
    "[-k] [--help] [--version]\n"                                       \
    "<hostname> <port> <query-directory>\n"				\
    "-n <num> : run with <num> thread [1]\n"                            \
    "-r <num> : make <num> requests each second [0]\n"			\
    "-s <num> : run the test for <num> seconds [0]\n"			\
    "-t <num> : timeout is <num> seconds [5]\n"                         \
    "-q <string> : add this host to http header['-k host']\n"           \
    "-w <num> : 1 or 0, 1 means ASYNC,0 means SYNC [0]\n"           \
    "-a <num> : timeout is <num> microSeconds [No Default] (For Example: If set '-a 30',this quota will cover'-t 5',if not set,-t will do effect) \n"                         \
    "-l <num> : minimum response length for successful query\n"         \
    "-m <num> : max query length (bytes)[2048]\n"                      \
    "-o <string> : error log file path \n"                             \
    "-k : enable http keep-alive\n"                                     \
    "--http : send http packet [http]\n"                               \
    "--tcp  : send tcp packet \n"                                       \
    "--post  : send http post packet \n"                                       \
    "--help : show help info\n"						\
    "--version : show version\n"                                        \
    "<query-directory> : Directory of query file\n"			\
    "One start specifier, either -parallel or -rate, is required.\n"	\
    "One end specifier, either -fetches or -seconds, is required.\n"	\
    "<hostname> and <port> is required.\n"                                            \
	"eg: ./Piemon -r 10 -s 10 --http -o log.txt -k 10.0.0.0 12345 ~/queryDir\n"   \
        "    ./Piemon -r 10 -s 10 --tcp 10.0.0.0 12345 ~/searcherQueryDir -k \n"


namespace piemon {

enum PacketType {
    TCP_PACKET,
    HTTP_PACKET
};
class PiemonCache 
{
public:
    PiemonCache();
    ~PiemonCache();

    void init();
//    void match(PiemonPerfCollector &result, uint32_t index, const char *queryStr);
    void showResult();
    void recordCommand(int argc, char **argv);
    float getProcessTime();
    void addResponseTime(struct timeval &startTime, 
                         struct timeval &endTime);
    void recordStoptime();
    void recordBytesReturn(int64_t bytesReturn);

public: //assistant metrics for show
    time_t _startTime;
    time_t _endTime;
    char cmd[CMD_LENGTH + 1];

public: //metrics for show
    atomic_t _totalQuery;
    atomic_t _successQuery;
    atomic_t _connectFailed;
    uint32_t _matchFailed; //match() was locked, no need to be atomic_t
    atomic_t _queryFailed;
    atomic_t _queryTimeout;


    //statistic in match()
    int64_t _noDocsReturn;
    int64_t _noDocsFound;
    int64_t _totalDocsReturn;
    int64_t _totalDocsFound;
    int64_t _totalBytesReturn;

    
public: //inner data
    typedef std::map<uint32_t, PiemonPerfCollector> MatchDataMap;
    MatchDataMap _matchDataMap;
    bool _stop;

    /* 0.1 ms */
    int _minResponseTime;
    int _maxResponseTime;
    int64_t _totalResponseTime;
    int *_responseTime;
    int *_FAKEresponseTime;


    
public: //user parameters
    char *_spec;
    int _parallelNum;
    int _maxRT;
    int _maxQPS;
    int _maxTIMEOUT;
    int _threadNum;
    int _fetches;
    int _rate;
    int _limits;
    bool _keepAlive;
    int _seconds;
    char *_logPath;
    bool _help;
    bool _isfakehost;
    int  _is_async_;
    char *_host;
    char *_fakehost;
    char *_is_add_url_;
    int _port;
    int _proj_id;
    char *_urlDirectory;
    int _timeout;
    int _microtimeout;
    uint32_t _maxUriLength;
    PacketType _packetType;
    bool _httpPost;
    char *_hsf_interface;
    char *_hsf_interface_version;
    char *_hsf_group;
    char *_hsf_method;
    bool _hsf_async;
	
private:
    piemon::ThreadMutex _mtx;
    piemon::ThreadMutex _responseTimeMtx;


};
}

#endif
