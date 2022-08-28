package com.liumapp.demo.docker.editor.utils;

import java.io.*;


public class SaveFile {
    private static String docPath = "/Users/seanking/Desktop/editor-service-master/doc"; // "/tmp/docker/doc"

    public static void savePic(InputStream inputStream, String fileName) {

        OutputStream os = null;
        try {
            byte[] bs = new byte[1024];
            int len;

            File tempFile = new File(docPath);
            if (!tempFile.exists()) {
                tempFile.mkdirs();
            }
            os = new FileOutputStream(tempFile.getPath() + File.separator + fileName);
            // 开始读取
            while ((len = inputStream.read(bs)) != -1) {
                os.write(bs, 0, len);
            }

        } catch (IOException e) {
            e.printStackTrace();
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            // 完毕，关闭所有链接
            try {
                os.close();
                inputStream.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
}
