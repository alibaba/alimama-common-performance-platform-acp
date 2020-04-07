#include "PiemonPerfCollector.h"
#include <string.h>
#include <iostream>
using namespace std;

using namespace piemon;

PiemonPerfCollector::PiemonPerfCollector(uint32_t bytesCount, uint32_t docsFound,
               uint32_t docsCount, uint32_t docsReturn) {
    _bytesCount = bytesCount;
    _docsFound = docsFound;
    _docsCount = docsCount;
    _docsReturn = docsReturn;
}

PiemonPerfCollector::~PiemonPerfCollector() {
}
void PiemonPerfCollector::show() {
    cout<<" _bytesCount "<<_bytesCount;
    cout<<" _docsFound "<<_docsFound;
    cout<<" _docsCount "<<_docsCount;
    cout<<" _docsReturn "<<_docsReturn<<endl;
}
bool PiemonPerfCollector::operator==(const PiemonPerfCollector& res) const {
    return _docsFound == res._docsFound
        && _docsCount == res._docsCount
        && _docsReturn == res._docsReturn;
}

bool PiemonPerfCollector::operator!=(const PiemonPerfCollector& res) const {
    return _docsFound != res._docsFound
        || _docsCount != res._docsCount
        || _docsReturn != res._docsReturn;
}
