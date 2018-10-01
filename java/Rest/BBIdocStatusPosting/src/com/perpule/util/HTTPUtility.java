package com.perpule.util;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Map;
import java.util.logging.Logger;

import javax.ws.rs.WebApplicationException;
import org.apache.commons.lang3.exception.ExceptionUtils;

import com.google.gson.Gson;
import com.perpule.bo.BBIdocStatusBO;
import com.perpule.domain.HTTPResponseObject;


public class HTTPUtility {
	private static final Logger LOGGER = Logger.getLogger(HTTPUtility.class.getName());
	public static HTTPResponseObject invokeHTTPRequestAndGetResponse(String urlString, String method, Map<String, String> headers,String data) {
		LOGGER.info("URL: " + urlString);
		LOGGER.info("Input parameters: Url: "+urlString+" Method: "+method+" headers: "+headers+" data: "+data);
	    URL url = null;
	    try {
	        url = new URL(urlString);
	        HttpURLConnection conn = null;
	        conn = (HttpURLConnection) url.openConnection();
	        conn.setRequestMethod(method);
	        conn.setConnectTimeout(30000);
	        conn.setReadTimeout(30000);

	        if (headers != null) {
	            for (Map.Entry<String, String> header : headers.entrySet()) {
	                conn.setRequestProperty(header.getKey(), header.getValue());
	            }
	        }

	        //conn.setRequestProperty("Content-Type", "application/json");

	        if (data != null) {
	            byte[] postDataBytes = data.toString().getBytes();
	            conn.setRequestProperty("Content-Length", String.valueOf(postDataBytes.length));
	            conn.setDoOutput(true);
	            conn.getOutputStream().write(postDataBytes);

	        }
	        
	        BufferedReader rd = null;
	        if(conn.getResponseCode() == 200 || conn.getResponseCode()==201){
	        	rd = new BufferedReader(new InputStreamReader(conn.getInputStream()));
	        }
	        else{
	        	rd = new BufferedReader(new InputStreamReader(conn.getErrorStream()));
	        }
	        StringBuilder result = new StringBuilder();

	        String line;
	        while ((line = rd.readLine()) != null) {
	            result.append(line);
	        }
	        rd.close();

	        LOGGER.info("Response " + result.toString());
			Gson gson = new Gson();

			HTTPResponseObject hTTPResponseObject = new HTTPResponseObject();
	        
	        hTTPResponseObject.setResult(result.toString());
	        hTTPResponseObject.setStatusCode(conn.getResponseCode());
	        hTTPResponseObject.setHeaderFields(conn.getHeaderFields());
	        
			String hTTPResponseObjectData = gson.toJson(hTTPResponseObject);
			LOGGER.info("hTTPResponseObjectData : " + hTTPResponseObjectData);
	        
	        return hTTPResponseObject;

	    } catch (Exception e) {
	    	LOGGER.info("invokeHTTPRequestWithStatusCodeInResponse failed");
	        LOGGER.severe(ExceptionUtils.getStackTrace(e));
	        throw new WebApplicationException();
	    }
	}
}


