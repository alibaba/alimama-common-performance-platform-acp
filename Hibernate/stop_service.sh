pid=`ps -ef | grep "python framework/webservice.py" | grep -v grep | awk '{print $2}'`
kill -9 $pid
