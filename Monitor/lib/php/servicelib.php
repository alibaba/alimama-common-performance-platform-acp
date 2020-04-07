<?php
function getValue($keyname)
{
    $jsonStr = getenv('JSONINPUT'); 
    $decodeJson = json_decode($jsonStr, true);
    if (isset($decodeJson[$keyname])){
        return $decodeJson[$keyname];
    }
    return "";
}

function getJsonInput()
{
    return getenv('JSONINPUT');
}

function getJsonDict()
{
    $jsonStr = getenv('JSONINPUT'); 
    return json_decode($jsonStr, true);
}

function callService($hosts, $plugin, $params)
{
    $httpCmd = "http://127.0.0.1:9090/".$plugin."?".$params."&hosts=".$hosts;
    $serviceRes = file_get_contents($httpCmd);
    return $serviceRes;
}

function getServiceValue($host, $key, $serviceRes)
{
    $decodeJson = json_decode($serviceRes, true);
    if (isset($decodeJson[$host][$key])){
        return $decodeJson[$host][$key];
    }
    return "";
}

function checkAuthority($users, $groups)
{
    $user = getenv('USERINPUT');
    $group = getenv('USERGROUP');
    $groupArr = explode(",",$group);


    $usersArr = explode(",",$users);
    if ($users != ""){
        
        if ($user!="" && in_array($user,$usersArr)){
            return true;
        }
        echo '{"status":"failed","msg":"user auth failed"}';
        exit(10);
    }

    if ($groups==""){
        return true;
    }
    $groupsArr = explode(",",$groups);
    foreach ($groupArr as $agroup){
        if (in_array($agroup,$groupsArr)){
            return true;
        }
    }
    echo '{"status":"failed","msg":"user auth failed"}';
    exit(10);
}
