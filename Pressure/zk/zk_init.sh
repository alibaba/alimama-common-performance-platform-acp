#!/bin/bash
cur_dir=$(dirname $0)
local_ip=$(hostname -i)
echo "====try to copy config files===="
bin_path="/opt/install/zookeeper-3.4.5/bin"
mkdir -p $bin_path
sudo cp -f $cur_dir/zkEnv.sh $bin_path/zkEnv.sh
sudo cp -f $cur_dir/zkServer.sh $bin_path/zkServer.sh
conf_path="/opt/install/zookeeper-3.4.5/conf"
mkdir -p $conf_path
sudo cp -f $cur_dir/log4j.properties $conf_path/log4j.properties
sudo cp -f $cur_dir/zoo.cfg $conf_path/zoo.cfg
sed -i "s/^server.1=.*/server.1=$local_ip:2888:3888/g" $conf_path/zoo.cfg
sudo cp -f $cur_dir/rm_zkData /etc/cron.d/rm_zkData
sudo mkdir -p /home/ads/zk_data
sudo mkdir -p /home/ads/zookeeper/dataLog
sudo touch /home/ads/zk_data/myid
echo "1" | sudo tee /home/ads/zk_data/myid
echo "====try to execute post script===="
bash $cur_dir/post.sh
