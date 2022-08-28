package com.liumapp.demo.docker.editor.entity;

import org.springframework.stereotype.Component;


@Component
public class Editor {

    private String content;

    public Editor() {
    }

    public Editor(String content) {
        this.content = content;
    }

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
    }

}
