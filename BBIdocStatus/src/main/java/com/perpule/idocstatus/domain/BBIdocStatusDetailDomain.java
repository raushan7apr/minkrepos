package com.perpule.idocstatus.domain;

public class BBIdocStatusDetailDomain {
	String siteCode;
	String idocNumber;
	String oldFileName;
	String newFileName;
	
	public String getSiteCode() {
		return siteCode;
	}
	public void setSiteCode(String siteCode) {
		this.siteCode = siteCode;
	}
	public String getIdocNumber() {
		return idocNumber;
	}
	public void setIdocNumber(String idocNumber) {
		this.idocNumber = idocNumber;
	}
	public String getOldFileName() {
		return oldFileName;
	}
	public void setOldFileName(String oldFIleName) {
		this.oldFileName = oldFIleName;
	}
	public String getNewFileName() {
		return newFileName;
	}
	public void setNewFileName(String newFileName) {
		this.newFileName = newFileName;
	}
	
}
