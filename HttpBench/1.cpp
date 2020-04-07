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

int main(int argc,char *argv[])
{
    CURL * curl;
    CURLcode res;
    char * response = NULL;

    if(argc !=2){
        printf("Usage:file<url>;\n");
        return -1;
    }

curl = curl_easy_init();
   
    if(curl!=NULL){
 //       printf("Usage:file<%s>;\n",argv[1]);
        curl_easy_setopt(curl,CURLOPT_URL,argv[1]);
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

             printf("curl_wasy_perform error = %s",curl_easy_strerror(res));
         }
        printf("response<%s>\n",response);

        curl_easy_cleanup(curl);
    }


}
