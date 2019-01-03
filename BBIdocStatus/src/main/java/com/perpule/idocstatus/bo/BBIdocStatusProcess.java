package com.perpule.idocstatus.bo;

import java.io.InterruptedIOException;
import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TimeZone;
import java.util.logging.Logger;
import javax.jms.Connection;
import javax.jms.ConnectionFactory;
import javax.jms.Destination;
import javax.jms.JMSException;
import javax.jms.MessageProducer;
import javax.jms.Session;
import javax.jms.TextMessage;
import org.apache.activemq.ActiveMQConnectionFactory;
import org.apache.commons.lang3.exception.ExceptionUtils;
import org.apache.commons.lang3.time.DateUtils;
import org.json.JSONObject;

import com.google.gson.Gson;
import com.perpule.idocstatus.constants.IDOCConstants;
import com.perpule.idocstatus.domain.BBIdocStatusDomain;
import com.perpule.idocstatus.domain.HTTPResponseObject;
import com.perpule.idocstatus.util.HTTPUtility;

public class BBIdocStatusProcess implements Runnable{
	
	private BBIdocStatusDomain bbIdocStatusDomain;
	private static final Logger LOGGER = Logger.getLogger(BBIdocStatusProcess.class.getName());
	private String mode;
	public BBIdocStatusProcess(BBIdocStatusDomain bbIdocStatusDomain,String mode) {
		this.bbIdocStatusDomain = bbIdocStatusDomain;
		this.mode=mode;
	}
	
	public void run() {
		try {
			Map<String, String> headers = new HashMap<String, String>();
			headers.put("Content-Type", "application/json");
			Gson gson = new Gson();
			bbIdocStatusDomain.setIdocInTime(convertToIst(bbIdocStatusDomain.getIdocInTime()));
			bbIdocStatusDomain.setIdocConversionTime(convertToIst(bbIdocStatusDomain.getIdocConversionTime()));
			bbIdocStatusDomain.setIdocProcessTime(convertToIst(bbIdocStatusDomain.getIdocProcessTime()));
			String jsonReqData = gson.toJson(bbIdocStatusDomain);
			HTTPResponseObject hTTPResponseObject=null;
			boolean status=false;
			String API_URL=IDOCConstants.TEST_API_URL;
			String MQ_URL=IDOCConstants.TEST_MQ_URL;
			String MQ_SUBJECT=IDOCConstants.TEST_MQ_SUBJECT;
			try {
				if("PROD".equalsIgnoreCase(mode)) {
					API_URL = IDOCConstants.PROD_API_URL;
					MQ_URL = IDOCConstants.PROD_MQ_URL;
					MQ_SUBJECT = IDOCConstants.PROD_MQ_SUBJECT;
				}else if("LOCAL".equalsIgnoreCase(mode)) {
					API_URL = IDOCConstants.LOCAL_API_URL;
					MQ_URL = IDOCConstants.LOCAL_MQ_URL;
					MQ_SUBJECT = IDOCConstants.LOCAL_MQ_SUBJECT;
				}
				hTTPResponseObject = HTTPUtility
						.invokeHTTPRequestAndGetResponse(API_URL, "POST", headers, jsonReqData);
				String firstResponse = hTTPResponseObject.getResult();
				if(firstResponse!=null) {
					JSONObject obj =  new JSONObject(firstResponse);
					if(obj != null && obj.has("isSuccessful")) {
						status = obj.getBoolean("isSuccessful");
					}
				}
				if (hTTPResponseObject != null && status == false) {
						LOGGER.info("Sleeping for 2 Minutes..");
						Thread.sleep(2000);
						LOGGER.info("UP after 2 minutes!!");
						hTTPResponseObject = HTTPUtility.invokeHTTPRequestAndGetResponse(API_URL,
								"POST", headers, jsonReqData);
						String lastResponse = hTTPResponseObject.getResult();
						if(lastResponse!=null) {
							JSONObject obj =  new JSONObject(lastResponse);
							if(obj != null && obj.has("isSuccessful")) {
								status = obj.getBoolean("isSuccessful");
							}
						}
				}
			} catch (Exception e) {
				LOGGER.severe(ExceptionUtils.getStackTrace(e));
			}
			if (hTTPResponseObject == null || status == false) {
				LOGGER.info("IDOC No - " + bbIdocStatusDomain.getIdocUpdateFor().getIdocNumber() + " for " + bbIdocStatusDomain.getIdocUpdateFor().getSiteCode() + " has been sent through MQ!!");
				MQPosting(jsonReqData, MQ_URL, MQ_SUBJECT);
			}else {
				LOGGER.info("IDOC No - " + bbIdocStatusDomain.getIdocUpdateFor().getIdocNumber() + " for " + bbIdocStatusDomain.getIdocUpdateFor().getSiteCode() + " has been sent through API!!");
			}
		} catch (Exception e) {
			LOGGER.severe(ExceptionUtils.getStackTrace(e));
		} 
	}
	
	 public void MQPosting(String reqestMessage,String url,String subject) throws JMSException{
     		ConnectionFactory connectionFactory = new ActiveMQConnectionFactory(url);
	        Connection connection = connectionFactory.createConnection();
	        connection.start();
	        Session session = connection.createSession(false,
	        Session.AUTO_ACKNOWLEDGE);
	        Destination destination = session.createQueue(subject);
	        MessageProducer producer = session.createProducer(destination);
	        TextMessage message = session.createTextMessage(reqestMessage);
	        producer.send(message);
	        connection.close();
     }
	 public String convertToIst(String dateString) throws ParseException {
		 SimpleDateFormat isoFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
		 Date date = isoFormat.parse(dateString);
		 Date newDate = DateUtils.addMinutes(date, 330);
		 return isoFormat.format(newDate);
	 }
}
