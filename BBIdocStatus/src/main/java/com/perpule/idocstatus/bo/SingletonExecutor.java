package com.perpule.idocstatus.bo;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.logging.Logger;

public class SingletonExecutor {

	private static volatile SingletonExecutor instance;
	private static Object mutex = new Object();
	
	private ExecutorService executor = null;
	
	private static final Logger LOGGER = Logger.getLogger(SingletonExecutor.class.getName());

	private SingletonExecutor() {
		this.executor = Executors.newFixedThreadPool(1000);
	}

	public static SingletonExecutor getInstance() {
		LOGGER.info("Fetching the singleton executor");
		SingletonExecutor result = instance;
		if (result == null) {
			LOGGER.info("Executor not present");
			synchronized (mutex) {
				result = instance;
				if (result == null){
					LOGGER.info("Creating a new executor");
					instance = result = new SingletonExecutor();
				}else{
					LOGGER.info("Using existing executor");
				}	
			}
		}
		return result;
	}
	
	public ExecutorService getExecutorService(){
		return this.executor;
	}
	
}
