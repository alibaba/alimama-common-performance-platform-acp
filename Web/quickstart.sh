#!/bin/bash

TIP="[Ali-tomcat Setup]"
tomcat_package="taobao-tomcat-dev.tar.gz"
download_tomcat_url="http://hsf.taobao.net/software/dev/$tomcat_package"
get_recommended_sar_url="http://ops.jm.taobao.org:9999/pandora-web/api/getRecommandSarVersion.do"

# package application
mvn clean package
war=`pwd`/acp-test-start/target/acp-test-start-1.0.0-SNAPSHOT.war
if [ $? -eq 0 ]; then
	echo "$TIP: package application success."
else
	echo "$TIP: package application fail."
fi

# create install folder "ali-tomcat"
mkdir ali-tomcat
if [ $? -eq 0 ]
then
	echo "$TIP: ali-tomcat folder has been created."
else
	echo "$TIP: ali-tomcat folder exsits. use it."
fi

# download ali-tomcat
cd ali-tomcat
wget $download_tomcat_url
if [ $? -eq 0 ]
then
	echo "$TIP: Download $tomcat_package successful."
else
	echo "$TIP: Download $tomcat_package failed!"
	exit 1
fi

# unzip taobao-tomcat-dev.tar.gz
path=`tar -tzf $tomcat_package | grep /bin/catalina.sh`
catalina_home=${path/\/bin\/catalina.sh/}
tar -xzf $tomcat_package
if [ $? -eq 0 ]
then
	echo "$TIP: Uzip $tomcat_package successful."
	rm $tomcat_package*
else
	echo "$TIP: Uzip $tomcat_package failed!"
	exit 1
fi

# get recommanded sar version
sar_version_raw=`curl $get_recommended_sar_url`
sar_version="$(echo "${sar_version_raw}" | tr -d '[[:space:]]')"
download_sar_url="http://ops.jm.taobao.org:9999/pandora-web/sar/$sar_version/taobao-hsf.tgz"

# download pandora(taobao-hsf.sar)
cd $catalina_home/deploy
if [ $? -ne 0 ]
then
	echo "$TIP: Open ~/ali-tomcat/$catalina_home/deploy failed."
	exit 1
fi
wget $download_sar_url
if [ $? -eq 0 ]
then
	echo "$TIP: Download pandora(taobao-hsf.tgz) successful."
else
	echo "$TIP: Download pandora(taobao-hsf.tgz) failed!"
	exit 1
fi

# unzip pandora(taobao-hsf.tgz)
tar -xzf taobao-hsf.tgz
if [ $? -eq 0 ]
then
	echo "$TIP: Uzip pandora(taobao-hsf.tgz) successful."
	rm taobao-hsf.tgz*
else
	echo "$TIP: Uzip pandora(taobao-hsf.tgz) failed!"
	exit 1
fi

# deploy war
cp $war ./
../bin/catalina.sh run


echo "===================================================================================================="
echo "Your Ali-tomcat & Pandora environment has been created successfully!"
echo ""
echo "* Ali-tomcat Version:      $catalina_home"
echo "* Sar Version:             $sar_version"
echo "* Ali-Tomcat Path:         ~/ali-tomcat/$catalina_home"
echo "* Pandora(taobao-hsf.sar): ~/ali-tomcat/$catalina_home/deploy/taobao-hsf.sar"
echo "* Web Application:         Please put your war under \"~/ali-tomcat/$catalina_home/deploy\""
echo "===================================================================================================="
exit 0