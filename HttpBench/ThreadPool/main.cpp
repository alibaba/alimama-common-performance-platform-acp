#include "threadpool.h"
#include <stdio.h> 
#include <unistd.h>
void* work(void* arg)
{
    char *p = (char*) arg;
    printf("threadpool callback fuction : %s.\n", p);
    sleep(1);
}

int main(void)
{
   struct threadpool *pool = threadpool_init(10, 20);
   threadpool_add_job(pool, work, const_cast<char*>("1"));
   threadpool_add_job(pool, work, const_cast<char*>("2"));
   threadpool_add_job(pool, work, const_cast<char*>("3"));
   threadpool_add_job(pool, work, const_cast<char*>("4"));
   threadpool_add_job(pool, work, const_cast<char*>("5"));
   threadpool_add_job(pool, work, const_cast<char*>("6"));
   threadpool_add_job(pool, work, const_cast<char*>("7"));
   threadpool_add_job(pool, work, const_cast<char*>("8"));
   threadpool_add_job(pool, work, const_cast<char*>("9"));
   threadpool_add_job(pool, work, const_cast<char*>("10"));
   threadpool_add_job(pool, work, const_cast<char*>("11"));
   threadpool_add_job(pool, work, const_cast<char*>("12"));
   threadpool_add_job(pool, work, const_cast<char*>("13"));
   threadpool_add_job(pool, work, const_cast<char*>("14"));
   threadpool_add_job(pool, work, const_cast<char*>("15"));
   threadpool_add_job(pool, work, const_cast<char*>("16"));
   threadpool_add_job(pool, work, const_cast<char*>("17"));
   threadpool_add_job(pool, work, const_cast<char*>("18"));
   threadpool_add_job(pool, work, const_cast<char*>("19"));
   threadpool_add_job(pool, work, const_cast<char*>("20"));
   threadpool_add_job(pool, work, const_cast<char*>("21"));
   threadpool_add_job(pool, work, const_cast<char*>("22"));
   threadpool_add_job(pool, work, const_cast<char*>("23"));
   threadpool_add_job(pool, work, const_cast<char*>("24"));
   threadpool_add_job(pool, work, const_cast<char*>("25"));
   threadpool_add_job(pool, work, const_cast<char*>("26"));
   threadpool_add_job(pool, work, const_cast<char*>("27"));
   threadpool_add_job(pool, work, const_cast<char*>("28"));
   threadpool_add_job(pool, work, const_cast<char*>("29"));
   threadpool_add_job(pool, work, const_cast<char*>("30"));
   threadpool_add_job(pool, work, const_cast<char*>("31"));
   threadpool_add_job(pool, work, const_cast<char*>("32"));
   threadpool_add_job(pool, work, const_cast<char*>("33"));
   threadpool_add_job(pool, work, const_cast<char*>("34"));
   threadpool_add_job(pool, work, const_cast<char*>("35"));
   threadpool_add_job(pool, work, const_cast<char*>("36"));
   threadpool_add_job(pool, work, const_cast<char*>("37"));
   threadpool_add_job(pool, work, const_cast<char*>("38"));
   threadpool_add_job(pool, work, const_cast<char*>("39"));
   threadpool_add_job(pool, work, const_cast<char*>("40"));
   sleep(5);
   threadpool_destroy(pool);
   return 0;
}
