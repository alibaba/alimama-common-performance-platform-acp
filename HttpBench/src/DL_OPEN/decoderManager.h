#ifndef _DECODER_MANAGER_CPP_
#define _DECODER_MANAGER_CPP_
#include <stdio.h>
#include <iostream>
#include <string>
using namespace std;
   class decoderManager{
      public:
           decoderManager() {}
           virtual ~decoderManager() {}
           virtual void Decode(string& targetStr) = 0;
      };
   extern "C" typedef decoderManager* create_t();
   extern "C" typedef void destroy_t(decoderManager*);
#endif 
