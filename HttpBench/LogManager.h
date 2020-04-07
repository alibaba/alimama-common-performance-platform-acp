#ifndef _LOG_MANAGER_CPP_
#define _LOG_MANAGER_CPP_
#include <ctime>
#include <signal.h>
#include <string.h>
#include <sys/wait.h>
#include <iostream>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <fcntl.h>
#include <sys/wait.h>
using namespace std;
namespace NewLog{
class LogManager{
    private:
        //FILE *fp;
        int  fp;
        time_t t;
    public:
        int Init(const char* path){
        creat(path,0755);
        if((fp=open(path,O_WRONLY|O_APPEND))>=0)
            return 0;
        else return -1;
        }
       int WriteOneLog(const char *on_what){
       //fprintf(fp,"%s\n",on_what);
       write(fp,on_what,strlen(on_what));
       fsync(fp);
       return 0;
     }
       void Flush(){
       delete this;
       }
       ~LogManager(){
      close(fp);
       }
};
}
#endif
