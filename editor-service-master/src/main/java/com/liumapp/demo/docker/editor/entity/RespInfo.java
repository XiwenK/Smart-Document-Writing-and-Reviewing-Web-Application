
package com.liumapp.demo.docker.editor.entity;

import lombok.Data;


@Data
public class RespInfo {
    private Integer status;

    private Object content;

    private String message;

    public RespInfo() {
    }


    public RespInfo(Integer status, Object content, String message) {
        this.status = status;
        this.content = content;
        this.message = message;
    }

    public RespInfo(Integer status, Object content) {
        this.status = status;
        this.content = content;
    }


}

