export LD_LIBRARY_PATH=${PWD}/../tools/python2.7.6/lib/python2.7/lib-dynload
export PATH=${PWD}/../tools/python2.7.6/bin/:${PWD}/tools/bin/:$PATH
export PYTHONPATH=${PWD}/../
export CLASSPATH=${PWD}/lib/java:.
python -m zk.py
