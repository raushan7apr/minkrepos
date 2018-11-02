package com.perpule.idocstatus.constants;

public class IDOCConstants {
	public static final String TEST_MQ_URL = "tcp://192.168.10.21:61616";
	public static final String TEST_MQ_SUBJECT = "qPOS_IdocDashboard";
	public static final String TEST_API_URL = "http://192.168.10.27:8088//idocdashboardapi/v1/updateOrInsertIdocStatus";
	
	public static final String PROD_MQ_URL = "tcp://192.168.10.33:26116";
	public static final String PROD_MQ_SUBJECT = "qPOS_IdocDashboard";
	public static final String PROD_API_URL = "http://192.168.10.32//idocdashboardapi/v1/updateOrInsertIdocStatus";
	
	//public static final String LOCAL_MQ_URL = "tcp://localhost:61616";
	//public static final String LOCAL_MQ_SUBJECT = "MyQueue";
}
