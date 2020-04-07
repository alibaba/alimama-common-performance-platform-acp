#include <iostream>
#include "PiemonCache.h"
#include "PiemonSchedule.h"
#include "PiemonQueryScanner.h"
#include <getopt.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <netdb.h>
#include <signal.h>

using namespace std;
using namespace piemon;

PiemonSchedule *load = NULL;
int checkParam(PiemonCache *globalInfo, int argc, char **argv);
void signalHandler(int signal);
int main(int argc, char *argv[]) {
	close(2);
    PiemonCache *globalInfo = new PiemonCache;
    globalInfo->recordCommand(argc, argv);
    if (checkParam(globalInfo, argc, argv) < 0) {
        return -1;
    }
    globalInfo->init();
    PiemonQueryScanner *fileReader = NULL;
    if (globalInfo->_packetType == HTTP_PACKET) {
        fileReader = new PiemonQueryScanner;
    } else {
        fileReader = new PiemonQueryScanner;
    }
    if (!fileReader->Init(string(globalInfo->_urlDirectory))) {
        cerr<<"Piemon Error: read url Directory"<<endl;
        return -1;
    }
    signal(SIGINT, signalHandler);
    signal(SIGKILL, signalHandler);
    signal(SIGQUIT, signalHandler);
    signal(SIGTERM, signalHandler);
    signal(SIGSTOP, signalHandler);
    signal(SIGTSTP, signalHandler);

    load = new PiemonSchedule(fileReader, globalInfo);
    load->run();
    delete load;
    load = NULL;
    delete globalInfo;
	globalInfo = NULL;
    delete fileReader;
	fileReader = NULL;
    return 0;
}

void signalHandler(int signal) {
    if (load) {
        load->stop();
        exit(0);
    }
}

int checkParam(PiemonCache *globalInfo, int argc, char **argv) {
    const char * const short_options = "p:r:s:q:x:w:d:f:a:l:o:m:n:t:y:j:g:e:khvbc";
    const struct option long_options[] = {
        {"help", 0, NULL, 'h'},
        {"version", 0, NULL, 'v'},
        {"tcp", 0, NULL, 'b'},
        {"http", 0, NULL, 'c'},
        {"post",0,NULL,'z'},
        {0, 0, 0, 0}
    };
    int option;
    while((option = getopt_long(argc, argv, short_options, long_options, 
                                NULL)) != -1)
    {
        switch(option) {
        case 'y':
            globalInfo->_maxRT = atoi(optarg);
            if(globalInfo->_parallelNum <= 0) {
                fprintf(stderr, "%s: maxRT must be at least 1\n", argv[0]);
                return -1;
            }
            break;
        case 'j':
            globalInfo->_maxQPS = atoi(optarg);
            if(globalInfo->_parallelNum <= 0) {
                fprintf(stderr, "%s: maxQPS must be at least 1\n", argv[0]);
                return -1;
            }
            break;
        case 'g':
            globalInfo->_maxTIMEOUT = atoi(optarg);
            if(globalInfo->_parallelNum <= 0) {
                fprintf(stderr, "%s: maxTIMEOUT must be at least 1\n", argv[0]);
                return -1;
            }
            break;
        case 'p':
            globalInfo->_parallelNum = atoi(optarg);
            if(globalInfo->_parallelNum <= 0) {
                fprintf(stderr, "%s: parallel must be at least 1\n", argv[0]);
                return -1;
            }
            break;
        case 'n':
            globalInfo->_threadNum = atoi(optarg);
            if(globalInfo->_threadNum <= 0) {
                fprintf(stderr, "%s: thread num must be at least 1\n", argv[0]);
                return -1;
            }
            break;
        case 'r':
            globalInfo->_rate = atoi(optarg);
            if(globalInfo->_rate <= 0) {   
                fprintf(stderr, "%s: rate must be at least 1\n", argv[0]);
                return -1;
            }
            break;
        case 's':
            globalInfo->_seconds = atoi(optarg);
            if(globalInfo->_seconds == 0) {   
                fprintf(stderr, "%s: seconds should not be 0\n", argv[0]);
                return -1;
            }
            break;
        case 'q':
            globalInfo->_isfakehost = true;
            if( NULL == optarg) {
                fprintf(stderr, "%s: fakehost is invalid\n", argv[0]);
                return -1;
            }
            globalInfo->_fakehost = strdup(optarg);
            break;
        case 'x':
            globalInfo->_is_add_url_ = NULL;
            if( NULL == optarg) {
                fprintf(stderr, "%s: x: add_url is invalid\n", argv[0]);
                return -1;
            }
            globalInfo->_is_add_url_ = optarg;
            break;
        case 'w':
            globalInfo->_is_async_ = 0;
            if( NULL == optarg) {
                fprintf(stderr, "%s: async or sync is invalid\n", argv[0]);
                return -1;
            }
            globalInfo->_is_async_ = atoi(optarg);
            break;
        case 'd':
            globalInfo->_proj_id = 36;
            if( NULL == optarg) {
                fprintf(stderr, "%s: async or sync is invalid\n", argv[0]);
                return -1;
            }
            globalInfo->_proj_id = atoi(optarg);
            break;
        case 't':
            globalInfo->_timeout = atoi(optarg);
            if(globalInfo->_timeout <= 0) {
                fprintf(stderr, "%s: timeout must be at least 1\n", argv[0]);
                return -1;
            }
            break;
        case 'a':
            globalInfo->_microtimeout = atoi(optarg);
            if(globalInfo->_microtimeout <=0){
                fprintf(stderr,"%s: microtime must be positive! \n",argv[0]);
                return -3;
            }
            break;
        case 'f':
            globalInfo->_fetches = atoi(optarg);
            if(globalInfo->_fetches <= 0) {   
                fprintf(stderr, "%s: fetches must be at least 1\n", argv[0]);
                return -1;
            }
            break;
        case 'l':
            globalInfo->_limits = atoi(optarg);
            if(globalInfo->_limits < 0) {   
                fprintf(stderr, "%s: limits should not be negative\n", argv[0]);
                return -1;
            }
            break;
        case 'o':
            if( NULL == optarg) {
                fprintf(stderr, "%s: error_log file path is invalid\n", argv[0]);
                return -1;
            }
            globalInfo->_logPath = strdup(optarg);
            break;
	case 'm':
            globalInfo->_maxUriLength = atoi(optarg);
            if(globalInfo->_maxUriLength <= 0) {   
                fprintf(stderr, "%s: Max Query Length should not be more than 0\n", argv[0]);
                return -1;
            }
            break;
        case 'h':
            globalInfo->_help = true;
            break;
        case 'k':
            globalInfo->_keepAlive = true;
            break;
        case 'v':
            fprintf(stderr, "%s\n", PIEMON_VERSION);
            return -1;
            break;
        case 'c':
            break;
        case 'b':
            globalInfo->_packetType = TCP_PACKET;
            break;
        case 'z':
            globalInfo->_httpPost = true;
            break;
        default:
            globalInfo->_help = true;
        }
    }

    if((0 == globalInfo->_parallelNum && 0 == globalInfo->_rate) 
       || (globalInfo->_parallelNum > 0 && globalInfo->_rate > 0)) 
    {
        globalInfo->_help = true;
    }
    if((0 == globalInfo->_fetches && 0 == globalInfo->_seconds) 
       || (globalInfo->_fetches > 0 && globalInfo->_seconds > 0)) 
    {
       globalInfo->_help = true;
    }     
   
    if(globalInfo->_help || 1==argc) {
        fprintf(stderr, "%s\n", HELPINFO);
        return -1;
    }

    if( argc == optind) {
        fprintf(stderr, "Need specify hostname!\n");
        return -1;
    }

    globalInfo->_host = strdup(argv[optind]);

    optind ++;
    if(argc == optind) {
        fprintf(stderr, "Need specify port!\n");
        return -1;
    }

    globalInfo->_port = atoi(argv[optind]);

    if(globalInfo->_port <= 0) {
        fprintf(stderr, "%s:lack port\n", argv[optind]);
        return -1;
    }
    
    optind ++;
    if(argc != optind && *argv[optind] != '-') {
        globalInfo->_urlDirectory = strdup(argv[optind]);
    }
    if (NULL == globalInfo->_urlDirectory) {
        fprintf(stderr, "Need specify query file!\n");
        return -1;
    }
    struct hostent *myHostEnt = gethostbyname(globalInfo->_host);
    if(NULL == myHostEnt) {
        fprintf(stderr, "%s:wrong address\n", globalInfo->_host);
        return -1;
    }
    char ipAddr[50] = {0};
    inet_ntop(myHostEnt->h_addrtype, *myHostEnt->h_addr_list, ipAddr, sizeof(ipAddr));
    if(0 == *ipAddr) {
        fprintf(stderr, "%s:wrong address\n", globalInfo->_host);
        return -1;
    }
    globalInfo->_spec = (char *)malloc(strlen(ipAddr) + 15);
    assert(globalInfo->_spec);
    snprintf(globalInfo->_spec, strlen(ipAddr)+15, 
             "http://%s:%d", ipAddr, globalInfo->_port);
    printf("target host:%s\n",globalInfo->_host);
    return 0;
}

