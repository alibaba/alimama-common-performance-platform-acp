package com.alibaba.acp.biz;

import com.alibaba.acp.common.commonUtil;
import com.alibaba.acp.web.MainController;
import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;

import javax.servlet.http.HttpServletRequest;
import java.io.IOException;
import java.util.Date;

public class TaskManager {

    private final  static String token="xilj438jg09hl1-340";

    public static String getAllTask()throws IOException {
        String url = "http://127.0.0.1:12345/getalltask";
        String ret =  commonUtil.sendGet(url);
        JSONObject retObj = new JSONObject();
        JSONArray retArr = JSONArray.parseArray(ret);
        retObj.put("code",0);
        retObj.put("msg","");
        retObj.put("count",10000);
        retObj.put("data",retArr);
        return retObj.toJSONString();
    }

    public static String createTask(HttpServletRequest request)throws IOException {
        String qps = request.getParameter("qps");
        String target = request.getParameter("target");
        String query_path = request.getParameter("query_path");
        String query_type = request.getParameter("query_type");
        String token = TaskManager.token;
        String option_str = request.getParameter("option_str");
        String source = "running";
        String create_task = String.format
                ("http://127.0.0.1:8001/create?qps=%s&target=%s&query_path=%s&query_type=http&token=xilj438jg09hl1-340&option=111&source=acp_111id",qps,target,query_path);
        String task_ret = commonUtil.sendGet(create_task);
        JSONObject resObj = JSONObject.parseObject(task_ret);
        JSONObject task = JSONObject.parseObject(resObj.get("res").toString());
        String task_id = task.get("task_id").toString();

        Date date = new Date();
        String dateStr = date.toString().replace(" ","-");

        String url = String.format
                ("http://127.0.0.1:12345/createtask?" +
                                "timestamp=%s" +
                                "&taskid=%s" +
                                "&acpid=%s" +
                                "&target=%s" +
                                "&query=%s" +
                                "&qps=%s"+
                                "&protocol=%s" +
                                "&source=%s" +
                                "&option_str=%s" +
                                "&owner=%s" +
                                "&json_conf=%s",
                        dateStr ,task_id,"acp_id_123456",target,query_path,qps,"http","running",option_str,"acp-owner","json-conf");
        System.out.println("URL:"+url);
        String ret =  commonUtil.sendGet(url);

        String url1="";
        return ret;
    }

    public static String stopTask(HttpServletRequest request)throws IOException {
        String task_id = request.getParameter("task_id");
        String rid = request.getParameter("id");
        String stop_task = String.format
                ("http://127.0.0.1:8001/stop?taskid=%s&timestamp=111&token=xilj438jg09hl1-340",task_id);
        String task_ret = commonUtil.sendGet(stop_task);
        String url = String.format
                ("http://127.0.0.1:12345/stoptask?rid=%s",rid);
        String ret =  commonUtil.sendGet(url);

        return ret;
    }


    public static String getLatestQuota(HttpServletRequest request)throws IOException {
        String stop_task = String.format
                ("http://127.0.0.1:12346/getquota");
        String ret = commonUtil.sendGet(stop_task);

        return ret;
    }


}
