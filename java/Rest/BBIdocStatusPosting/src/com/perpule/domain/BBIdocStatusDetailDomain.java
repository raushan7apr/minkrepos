package com.perpule.domain;

public class BBIdocStatusDetailDomain {
	String siteCode;
	String idocNumber;
	String oldFIleName;
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
	public String getOldFIleName() {
		return oldFIleName;
	}
	public void setOldFIleName(String oldFIleName) {
		this.oldFIleName = oldFIleName;
	}
	public String getNewFileName() {
		return newFileName;
	}
	public void setNewFileName(String newFileName) {
		this.newFileName = newFileName;
	}
	
}
