#ifndef THREAD_POOL_H
#define THREAD_POOL_H
#include<pthread.h>
struct job
{
	    void* (*callback_function)(void *arg);    //线程回调函数
		    void *arg;                                //回调函数参数
			    struct job *next;
};

struct threadpool
{
   int thread_num;                   //线程池中开启线程的个数
   int queue_max_num;                //队列中最大job的个数
   struct job *head;                 //指向job的头指针
   struct job *tail;                 //指向job的尾指针
   pthread_t *pthreads;              //线程池中所有线程的pthread_t
   pthread_mutex_t mutex;            //互斥信号量
   pthread_cond_t queue_empty;       //队列为空的条件变量
   pthread_cond_t queue_not_empty;   //队列不为空的条件变量
   pthread_cond_t queue_not_full;    //队列不为满的条件变量
   int queue_cur_num;                //队列当前的job个数
   int queue_close;                  //队列是否已经关闭
   int pool_close;                   //线程池是否已经关闭
};

//================================================================================================
////函数名：                   threadpool_init
////函数描述：                 初始化线程池
////输入：                    [in] thread_num     线程池开启的线程个数
////                         [in] queue_max_num  队列的最大job个数 
////输出：                    无
////返回：                    成功：线程池地址 失败：NULL
////================================================================================================
struct threadpool* threadpool_init(int thread_num, int queue_max_num);
//
////================================================================================================
////函数名：                    threadpool_add_job
////函数描述：                  向线程池中添加任务
////输入：                     [in] pool                  线程池地址
////                          [in] callback_function     回调函数
////                          [in] arg                     回调函数参数
////输出：                     无
////返回：                     成功：0 失败：-1
////================================================================================================
int threadpool_add_job(struct threadpool *pool, void* (*callback_function)(void *arg), void *arg);
//
////================================================================================================
////函数名：                    threadpool_destroy
////函数描述：                   销毁线程池
////输入：                      [in] pool                  线程池地址
////输出：                      无
////返回：                      成功：0 失败：-1
////================================================================================================
int threadpool_destroy(struct threadpool *pool);
//
////================================================================================================
////函数名：                    threadpool_function
////函数描述：                  线程池中线程函数
////输入：                     [in] arg                  线程池地址
////输出：                     无  
////返回：                     无
////================================================================================================
void* threadpool_function(void* arg);
#endif
