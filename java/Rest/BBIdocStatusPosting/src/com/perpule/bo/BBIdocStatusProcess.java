package com.perpule.bo;

import java.io.InterruptedIOException;
import java.util.HashMap;
import java.util.Map;
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
import com.google.gson.Gson;
import com.perpule.constants.IDOCConstants;
import com.perpule.domain.BBIdocStatusDomain;
import com.perpule.domain.HTTPResponseObject;
import com.perpule.util.HTTPUtility;

public class BBIdocStatusProcess implements Runnable{
	
	private BBIdocStatusDomain bbIdocStatusDomain;
	private static final Logger LOGGER = Logger.getLogger(BBIdocStatusProcess.class.getName());
	
	public BBIdocStatusProcess(BBIdocStatusDomain bbIdocStatusDomain) {
		this.bbIdocStatusDomain = bbIdocStatusDomain;
	}
	
	public void run() {
		try {
			Map<String, String> headers = new HashMap<String, String>();
			headers.put("Content-Type", "application/json");
			Gson gson = new Gson();
			String jsonReqData = gson.toJson(bbIdocStatusDomain);
			HTTPResponseObject hTTPResponseObject=null;
			try {
				hTTPResponseObject = HTTPUtility
						.invokeHTTPRequestAndGetResponse(IDOCConstants.API_URL, "POST", headers, jsonReqData);
				if (hTTPResponseObject != null && hTTPResponseObject.getStatusCode() != 200) {
						Thread.sleep(2000);
						hTTPResponseObject = HTTPUtility.invokeHTTPRequestAndGetResponse(IDOCConstants.API_URL,
								"POST", headers, jsonReqData);
				}
			} catch (Exception e) {
				LOGGER.severe(ExceptionUtils.getStackTrace(e));
			}
			if (hTTPResponseObject == null || hTTPResponseObject.getStatusCode() != 200) {
				MQPosting(jsonReqData, IDOCConstants.MQ_URL, IDOCConstants.MQ_SUBJECT);
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
	
}
