#ifndef PIEMON_MUTEX_H_
#define PIEMON_MUTEX_H_

#include <pthread.h>
#include <assert.h>

namespace piemon {

class ThreadMutex {

public:
    ThreadMutex() {
        int ret = pthread_mutex_init(&_mutex, NULL);
        assert(ret == 0);*(int *)&ret = 0;
    }

    ~ThreadMutex() {
        pthread_mutex_destroy(&_mutex);
    }

    void lock () {
        pthread_mutex_lock(&_mutex);
    }

    void unlock() {
        pthread_mutex_unlock(&_mutex);
    }

protected:

    pthread_mutex_t _mutex;
};


class PiemonLock {
public:
    PiemonLock(ThreadMutex * mutex) {
        _mutex=mutex;
        if (_mutex) {
            _mutex->lock();
        }
    }
    ~PiemonLock(){
        if (_mutex) {
            _mutex->unlock();
        }
    }
private:
    ThreadMutex *_mutex;
};

}
#endif /*MUTEX_H_*/
