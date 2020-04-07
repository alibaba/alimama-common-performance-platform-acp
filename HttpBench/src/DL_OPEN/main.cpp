#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>
#include "decoderManager.h"
#include <string>
#include <iostream>
using namespace std;

//动态链接库路径
#define LIB_CACULATE_PATH "./libdecoder.so"

//函数指针
typedef int (*CAC_FUNC)(int, int);

int main()
{
    void *handle;
    char *error;
    CAC_FUNC cac_func = NULL;

    //打开动态链接库
    handle = dlopen(LIB_CACULATE_PATH, RTLD_LAZY);
    if (!handle) {
    fprintf(stderr, "%s\n", dlerror());
    exit(EXIT_FAILURE);
    }

    //清除之前存在的错误
    dlerror();

    //获取一个函数
    create_t* create_fun = (create_t*)dlsym(handle, "create");
    if ((error = dlerror()) != NULL)  {
    fprintf(stderr, "%s\n", error);
    exit(EXIT_FAILURE);
    }
    
    destroy_t* destroy_fun = (destroy_t*)dlsym(handle,"destroy");
    if ((error = dlerror()) != NULL)  {
    fprintf(stderr, "%s\n", error);
    exit(EXIT_FAILURE);
    }

   decoderManager* manager = create_fun();
   string str("fasdfasd");
   cout<<str<<endl;
   manager->Decode(str);
   cout<<str<<endl;
   destroy_fun(manager); 
   



    //关闭动态链接库
    dlclose(handle);
    exit(EXIT_SUCCESS);
}
