package com.perpule.idocstatus.bo;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.logging.Logger;
import org.apache.commons.lang3.exception.ExceptionUtils;
import com.perpule.idocstatus.domain.BBIdocStatusDomain;

public class BBIdocStatusBO {
		private static final Logger LOGGER = Logger.getLogger(BBIdocStatusBO.class.getName());
        public boolean sendIdocStatus(List<BBIdocStatusDomain> data) {
        	try {
        		ExecutorService executor = Executors.newFixedThreadPool(10);
				for (BBIdocStatusDomain bbIdocStatusDomain : data) {
					executor.submit(new BBIdocStatusProcess(bbIdocStatusDomain));
				} 
				return true;
			} catch (Exception e ) {
				LOGGER.severe(ExceptionUtils.getStackTrace(e));
			}
			return false;
        }
}
