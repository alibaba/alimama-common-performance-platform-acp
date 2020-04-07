
function getValue
{
    keyname=$1
    VALUE=`echo $JSONINPUT | JSON.sh -l | grep $keyname | awk '{print $2}' | sed 's/^"//' | sed 's/"$//'` 
    
    echo $VALUE
}

function getJsonInput
{
    echo $JSONINPUT
}

function callService
{
    hosts=$1
    plugin=$2
    params=$3
    httpcmd="http://127.0.0.1:9090/${plugin}?${params}&hosts=${hosts}"
    serviceRes=`curl $httpcmd 2>/dev/null`
    echo "$serviceRes"
}

function getServiceValue
{
    host=$1
    key=$2
    serviceRes=$3
    value=`echo "$serviceRes" | JSON.sh -l | grep \"$host\",\"$key\" | awk '{print $2}' | sed 's/^"//' | sed 's/"$//'`
    echo -e "$value\c" 
}

function checkAuthority
{
    user=$USERINPUT
    group=$USERGROUP

    OLD_IFS=$IFS
    IFS=","
    users=("$1")

    if [ ! -z "$1" ]; then
        users=("$1")
        for auser in ${users[@]}; do
            [ $auser == $user ] && { IFS=$OLD_IFS; return 0; }
        done
        IFS=$OLD_IFS
        echo "{\"status\":\"failed\",\"err_info\":\"user auth failed\"}"
        exit 10
    fi


    [ -z "$2" ] && return 0
    IFS=","
    group_arr=("$group")
    groups_arr=("$2")
    for agroup in ${group_arr[@]}; do
       for bgroup in ${groups_arr[@]}; do
          [ "$agroup" == "$bgroup" ] && { IFS=$OLD_IFS; return 0;}
       done 
    done

    IFS=$OLD_IFS 
    echo "{\"status\":\"failed\",\"err_info\":\"user auth failed\"}"
    exit 10
}

##### log function #####
function LOG
{
    level=$1
    msg=$2
    echo "[$level] `date  +"%Y-%m-%d %H:%M:%S"` $msg" >> service.log
    if [ $DEBUG == 1 ]; then
        echo $msg
    fi
}

function DEBUG
{
    LOG DEBUG "$1"
}
function INFO
{
    LOG INFO "$1"
}
function WARN
{
    LOG WARN "$1"
}
function ERROR
{
    LOG ERROR "$1"
}
