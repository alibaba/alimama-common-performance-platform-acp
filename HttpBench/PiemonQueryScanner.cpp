#include "PiemonQueryScanner.h"
#include <iostream>
#include <fcntl.h>
#include <errno.h>
#include <dirent.h>
#include <sys/stat.h>
#include <cstring>
using namespace piemon;
using namespace std;

PiemonQueryScanner::PiemonQueryScanner() {
    _indexOfUrl = 0; 
    _indexOfUrlText = 0;
    _currUrlFile = NULL;
}

PiemonQueryScanner::~PiemonQueryScanner() {
    for (vector<FILE *>::iterator it = _fileList.begin();
         it != _fileList.end(); it ++) 
    {
        fclose((*it));
    }
    _fileList.clear();
}


bool PiemonQueryScanner::Init(const string &path) {
    struct stat file_type;
    if (lstat(path.c_str(), &file_type) < 0) {
        cerr<<"Wrong lstat, You should check you path["<<path<<"]!"<<endl; 
        return false;
    }
    if (S_ISREG(file_type.st_mode)) {
        readFile(path);
    } else if (S_ISDIR(file_type.st_mode)) {
        readDir(path);
    }
    if (_fileList.size() == 0) {
        cerr<<"warning : No usable query file in["<<path<<"]!"<<endl;
        return false;
    }
    return true;
}

bool PiemonQueryScanner::ScanOneQuery(char *buf, uint32_t length, int32_t &index) {
    piemon::PiemonLock guard(&_lockFileReader);

    if (NULL == _currUrlFile) {
        getNextFile(_currUrlFile);
    }

    if (fgets(buf, length, _currUrlFile) == NULL) {
        getNextFile(_currUrlFile); 
        if (fgets(buf, length, _currUrlFile) == NULL) {
            return false;
        }
    }
    
    for(uint32_t i = 0; i < length; i++, buf++) {
        if (*buf == '\n') {
            *buf = '\0';
            break;
        } else if (*buf == '\0') {
            break;
        }
    }
    _indexOfUrl++;
    index = _indexOfUrl;
    return true;
}

bool PiemonQueryScanner::readFile(const string &filename) {
    struct stat file_type;
    if (lstat(filename.c_str(), &file_type) < 0) {
        return -1;
    }
    if (0 == file_type.st_size) {
        cerr<<filename<<": is empty"<<endl;
        return false;
    } else {
        FILE *fp = fopen(filename.c_str(), "r");
        if (NULL == fp) {
            perror(filename.c_str());
            return false;
        } else {
            _fileList.push_back(fp);
            return true;
        }
    }
}

bool PiemonQueryScanner::readDir(const std::string &dirname) {
    struct dirent* dir_ent;
    DIR *dir;
    struct stat file_type;

    if ((dir = opendir(dirname.c_str())) == NULL) {
        perror(dirname.c_str());
        return -1;
    }
    while ((dir_ent = readdir(dir)) != NULL) {
        if (dir_ent->d_name[0] == '.') {
            continue;
        }
        if (dir_ent->d_name[0] == '#') {
            continue;
        }
        if (strlen(dir_ent->d_name) > 1 
            && dir_ent->d_name[strlen(dir_ent->d_name) - 1] == '~')  
        {
            continue;
        }
        
        string fullpath = dirname;
        fullpath += string("/");
        fullpath += string(dir_ent->d_name);

        if ((lstat(fullpath.c_str(), &file_type)) < 0) {
            cerr<<fullpath<<": wrong file/dir!"<<endl;
            continue;
        }

        if (S_ISREG(file_type.st_mode)) {
            readFile(fullpath);
        } else if (S_ISDIR(file_type.st_mode)) {
            readDir(fullpath);
        } else {
            cerr<<fullpath<<": is not regular file!"<<endl;
        }
    }
    closedir(dir);
    return true;
}

bool PiemonQueryScanner::getNextFile(FILE *&file) {
    _indexOfUrlText = _indexOfUrlText % _fileList.size();
    if (0 == _indexOfUrlText) {
        _indexOfUrl = 0;
    }
    file = (FILE *)_fileList.at(_indexOfUrlText);
    fseek(file, 0, 0);
    _indexOfUrlText ++;
    if ( NULL == file ) {
        return false;
    } else {
        return true;
    }
}
