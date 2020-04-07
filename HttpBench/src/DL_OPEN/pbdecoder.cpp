#ifndef _PB_DECODER_CPP_
#define _PB_DECODER_CPP_
#include<stdio.h>
#include<string>
#include<iostream>
#include<string>
#include "decoderManager.h"
using namespace std;
   class pbDecoder:public decoderManager{
     virtual void Decode(string& targetStr){
      string str("666");
     } 

     };
extern "C" decoderManager* create(){
     return new pbDecoder;
}
extern "C" void destroy(decoderManager* p){
     delete p;

}
#endif
