package com.liumapp.demo.docker.editor.controller;

import com.alibaba.fastjson.JSON;
import com.liumapp.demo.docker.editor.entity.Editor;
import com.liumapp.demo.docker.editor.utils.Html2PDF;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;


@RestController
@RequestMapping(value = "html")
public class IndexController {

    @RequestMapping(value = "pdf")
    public String getContent (@RequestBody Editor editor) {
        Html2PDF html2PDF = new Html2PDF();
        String path = "/Users/seanking/Desktop";
        // System.getProperty("user.dir")
        html2PDF.html2pdf( path + "/test.pdf" , editor.getContent());
        return JSON.toJSONString("success");
    }
}
