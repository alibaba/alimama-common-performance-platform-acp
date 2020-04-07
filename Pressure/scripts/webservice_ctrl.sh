export LD_LIBRARY_PATH=${PWD}/../python2.7.6/lib/python2.7/lib-dynload
export PATH=${PWD}/../python2.7.6/bin/:$PATH
export PYTHONPATH=${PWD}/../src

action=$1
if [ "x$action" == "xstart" ]
then
    cd ../src/service/ && nohup python webservice.py 8001 &
fi

if [ "x$action" == "xstop" ]
then
    pid=`ps -ef | grep "webservice.py 8001" | grep -v grep | awk '{print $2}'`
    kill $pid
fi
