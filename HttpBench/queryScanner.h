#ifndef QUERY_SCANNER_H_
#define QUERY_SCANNER_H_

#include <sys/types.h>
#include <string>
#include <inttypes.h> 
#include <stdint.h>

//typedef uint32_t uint32;
namespace piemon{
class queryScanner 
{
public:
    queryScanner() {}
    virtual ~queryScanner() {}
    
    virtual bool Init(const std::string &path) = 0;
    virtual bool ScanOneQuery(char *buf, uint32_t length, int32_t &index) = 0;
};
}

#endif
