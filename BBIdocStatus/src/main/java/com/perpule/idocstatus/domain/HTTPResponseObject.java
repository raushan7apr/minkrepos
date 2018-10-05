package com.perpule.idocstatus.domain;

import java.util.List;
import java.util.Map;

public class HTTPResponseObject {

	private String result;
	
	private int statusCode;
	
	private Map<String,List<String>> headerFields;

	public String getResult() {
		return result;
	}

	public void setResult(String result) {
		this.result = result;
	}

	public int getStatusCode() {
		return statusCode;
	}

	public void setStatusCode(int statusCode) {
		this.statusCode = statusCode;
	}

	public Map<String, List<String>> getHeaderFields() {
		return headerFields;
	}

	public void setHeaderFields(Map<String, List<String>> headerFields) {
		this.headerFields = headerFields;
	}
	
}