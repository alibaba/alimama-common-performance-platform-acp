#ifndef PIEMON_QUERY_SCANNER_H_
#define PIEMON_QUERY_SCANNER_H_

#include "queryScanner.h"
#include <vector>
#include <stdio.h>
#include "PiemonLock.h"

namespace piemon {
class PiemonQueryScanner : public queryScanner
{
public:
    PiemonQueryScanner();
    ~PiemonQueryScanner();
    bool Init(const std::string &path);
    bool ScanOneQuery(char *buf, uint32_t length, int32_t &index);

private:
    bool readFile(const std::string &filename);
    bool readDir(const std::string &dirname);
    bool getNextFile(FILE *&file);
    
private:
    std::vector<FILE *> _fileList;
    int _indexOfUrl; 
    int _indexOfUrlText;
    FILE *_currUrlFile;
    piemon::ThreadMutex _lockFileReader;
};
}

#endif 
