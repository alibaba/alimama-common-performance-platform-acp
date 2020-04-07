#ifndef HTTPINTERFACE_H_
#define HTTPINTERFACE_H_
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <curl/curl.h>
static size_t save_response_callback(void *buffer,size_t size,size_t count,void **response)
{
    char * ptr = NULL;
//    printf("buffer is %s\n",(char *)buffer);
    ptr =(char *) malloc(count*size + 4);
    memcpy(ptr,buffer,count*size);
    *response = ptr;

    return count;
}

//int main(int argc,char *argv[])
int queryF(const char *url)
{
    CURL * curl;
    CURLcode res;
    char * response = NULL;


curl = curl_easy_init();
   
    if(curl!=NULL){
  //      printf("Usage:file<%s>;\n",url);
        curl_easy_setopt(curl,CURLOPT_URL,url);
        curl_easy_setopt(curl,CURLOPT_WRITEFUNCTION,&save_response_callback);
        curl_easy_setopt(curl,CURLOPT_WRITEDATA,&response);

curl_easy_setopt(curl,CURLOPT_COOKIESESSION,1L);
        curl_easy_setopt(curl,CURLOPT_COOKIEFILE,"/dev/null");
        curl_easy_setopt(curl,CURLOPT_SSL_VERIFYPEER,1);
        //curl_easy_setopt(curl,CURLOPT_CAPATH,"/etc/ssl/cert/");
        curl_easy_setopt(curl,CURLOPT_CAINFO,"ca-cert.pem");

        curl_easy_setopt(curl,CURLOPT_SSL_VERIFYHOST,1);
        curl_easy_setopt(curl,CURLOPT_VERBOSE,1L);
        curl_easy_setopt(curl,CURLOPT_TIMEOUT,30);

        res = curl_easy_perform(curl);
        if(res != CURLE_OK){
            return -1;
            curl_easy_cleanup(curl);
     //        printf("curl_wasy_perform error = %s",curl_easy_strerror(res));
         }
 //       printf("response<%s>\n",response);
        else{
			return 0;
        curl_easy_cleanup(curl);
		 }
    }
    return 0;

}
#endif
