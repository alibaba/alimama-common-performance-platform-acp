#ifndef _MESSAGE_READER_H_
#define _MESSAGE_READER_H_
#include<stdio.h>
#include<fcntl.h>
#include<stdlib.h>
#include<string.h>
#include<sys/types.h>
#include<sys/ipc.h>
#include<sys/msg.h>
#include<sys/stat.h>
#include<iostream>
#include<unistd.h>
#include<errno.h>
#define BUF_SIZE 256
#define PROJ_ID  32
#define PATH_NAME "/tmp"
#define SERVER_MSG  1
#define CLIENT_MSG 2
using namespace std;

class MessageReader{
private:
struct mymsg
   {
     long msgtype;
     char content[256];
   }msgbuf;
int qid;
int msglen;
key_t msgkey;
public :
int Init(int proj_id){
  msgkey=ftok(PATH_NAME,proj_id);
//  msgkey=ftok(PATH_NAME,PROJ_ID);
  if(msgkey==-1)
   {
     cout<<"sorry key create failed: "<<strerror(errno)<<endl;
     exit(0);   
  }
  qid=msgget(msgkey,IPC_CREAT|0666);
  if(qid==-1)
   {
      cout<<"get msg quen failed "<<strerror(errno)<<endl;
      exit(0);
   }
  cout<<"获取消息队列成功"<<qid<<"\n";

}
int AsyncPoll(string& retval){
if(msgrcv(qid,&msgbuf,BUF_SIZE,CLIENT_MSG,IPC_NOWAIT)==-1){
//cout<<"no message"<<endl;
return -1;
}
else{
retval = msgbuf.content;
return 0;

}
}
};
#endif
