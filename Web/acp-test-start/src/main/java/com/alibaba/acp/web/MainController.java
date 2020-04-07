package com.alibaba.acp.web;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.serializer.SerializerFeature;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseBody;
import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;

import javax.servlet.http.HttpServletRequest;
import java.io.IOException;
import java.util.Date;
import com.alibaba.acp.common.*;
import com.alibaba.acp.biz.TaskManager;
import org.springframework.web.servlet.mvc.method.annotation.JsonViewResponseBodyAdvice;

@Controller
public class MainController {
    private static final String token = "123abc";

    @RequestMapping("/")
    public String root() {
        return "index";
    }
    @RequestMapping("/tasklist")
    public String tasklist()
    {
        return "gateway4";
    }

    @RequestMapping("/taskmonitor")
    public String taskmonitor()
    {
        return "monitor";
    }

    @RequestMapping("/createtask")
    public String root2() {
              return "gateway5";
    }

    @RequestMapping("taskdetail")
    public String pressdetail(HttpServletRequest request) {
        return "pressdetail";
    }

    @RequestMapping("pressdetail2")
    public String pressdetail2(HttpServletRequest request) {
        return "pressdetail2";
    }

    @RequestMapping("pressdetail3")
    public String pressdetail3(HttpServletRequest request) {
        return "pressdetail3";
    }

    @RequestMapping("/test3")
    public String root3()
    {
       return "index2";
    }

    @RequestMapping("/pressquery")
    public String pressquery()
    {
        return "pressquery";
    }
    @RequestMapping(value="/api/getQueryList")
    @ResponseBody
    public String getQueryList(HttpServletRequest request) throws  IOException{
        String res =  commonUtil.sendGet("http://10.103.67.40:8001/queryList");
        JSONObject obj = JSONObject.parseObject(res);
        JSONArray retArr = new JSONArray();
        Integer seq = 1;
        for(String key:obj.keySet()){
            seq++;
            JSONObject retObj = new JSONObject();
            String proto_name = key;
            JSONArray FileArr = JSONArray.parseArray(obj.get(key).toString());
            retObj.put("title",key);
            retObj.put("id",seq);
            retObj.put("checked",true);
            retObj.put("spread",true);
            JSONArray smallArr = new JSONArray();
            for(int x=0;x<FileArr.size();x++){
                String fileName = FileArr.get(x).toString();
              //  System.out.println("aaaa"+fileName);
                JSONObject smallObj = new JSONObject();
                smallObj.put("id",seq);
                smallObj.put("title",fileName);
                seq++;
                smallArr.add(smallObj);
            }
            retObj.put("children",smallArr);
            retArr.add(retObj);

        }
        JSONArray fRetArr = new JSONArray();
        for(int v=0;v<3;v++){
            JSONObject aObj = new JSONObject();
            JSONArray aArr = new JSONArray();
            aObj.put("title",String.format("bizline-%d",v));
            aObj.put("id",seq);
            aObj.put("checked",true);
            aObj.put("spread",true);
            aArr = retArr;
            aObj.put("children",aArr);
            seq++;
            fRetArr.add(aObj);
        }
System.out.println("776666"+fRetArr.toJSONString());
       return JSON.toJSONString(fRetArr,SerializerFeature.DisableCircularReferenceDetect);
    }



    public String getTaskList()
    {
        return "";
    }
    @RequestMapping(value="/api/getLatestQuota")
    @ResponseBody
    public String getLatestQuota(HttpServletRequest request) throws  IOException{
        return TaskManager.getLatestQuota(request);
    }

    @RequestMapping(value="/api/getalltask")
    @ResponseBody
    public String getalltask    (HttpServletRequest request)throws IOException {
        return TaskManager.getAllTask();


       /* String url = "http://127.0.0.1:12345/getalltask";
        String ret =  commonUtil.sendGet(url);
        JSONObject retObj = new JSONObject();
        JSONArray retArr = JSONArray.parseArray(ret);
        retObj.put("code",0);
        retObj.put("msg","");
        retObj.put("count",10000);
        retObj.put("data",retArr);
        return retObj.toJSONString(); */
    }

    @RequestMapping(value="/api/createtask")
    @ResponseBody
    public String createtask(HttpServletRequest request)throws IOException {
        return TaskManager.createTask(request);

    /*    String qps = request.getParameter("qps");
        String target = request.getParameter("target");
        String query_path = request.getParameter("query_path");
        String query_type = request.getParameter("query_type");
        String token =MainController.token;
        String option_str = request.getParameter("option_str");
        String source = "running";
        String create_task = String.format
                ("http://127.0.0.1:8001/create?qps=%s&target=%s&query_path=%s&query_type=http&token=123abc&option=111&source=acp_111id",qps,target,query_path);
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
        String ret =  commonUtil.sendGet(url);

        String url1="";
        return ret; */
    }


    @RequestMapping(value="/api/stoptask")
    @ResponseBody
    public String stoptask(HttpServletRequest request)throws IOException {

        return TaskManager.stopTask(request);
       /* String task_id = request.getParameter("task_id");
        String rid = request.getParameter("id");
        String stop_task = String.format
                ("http://127.0.0.1:8001/stop?taskid=%s&timestamp=111&token=123abc",task_id);
        String task_ret = commonUtil.sendGet(stop_task);
        String url = String.format
                ("http://127.0.0.1:12345/stoptask?rid=%s",rid);
        String ret =  commonUtil.sendGet(url);

        return ret; */
    }

    @RequestMapping("/checkpreload.htm")
    public @ResponseBody String checkPreload() {
        return "success";
    }
}
