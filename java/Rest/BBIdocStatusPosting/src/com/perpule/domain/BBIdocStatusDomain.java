package com.perpule.domain;

public class BBIdocStatusDomain {
	String idocInTime;
	String idocConversionTime;
	String idocProcessTime;
	String idocProcessStatus;
	String remarks;
	String sourceSystemId;
	BBIdocStatusDetailDomain idocUpdateFor;
	
	public String getIdocInTime() {
		return idocInTime;
	}
	public void setIdocInTime(String idocInTime) {
		this.idocInTime = idocInTime;
	}
	public String getIdocConversionTime() {
		return idocConversionTime;
	}
	public void setIdocConversionTime(String idocConversionTime) {
		this.idocConversionTime = idocConversionTime;
	}
	public String getIdocProcessTime() {
		return idocProcessTime;
	}
	public void setIdocProcessTime(String idocProcessTime) {
		this.idocProcessTime = idocProcessTime;
	}
	public String getIdocProcessStatus() {
		return idocProcessStatus;
	}
	public void setIdocProcessStatus(String idocProcessStatus) {
		this.idocProcessStatus = idocProcessStatus;
	}
	public String getRemarks() {
		return remarks;
	}
	public void setRemarks(String remarks) {
		this.remarks = remarks;
	}
	public String getSourceSystemId() {
		return sourceSystemId;
	}
	public void setSourceSystemId(String sourceSystemId) {
		this.sourceSystemId = sourceSystemId;
	}
	public BBIdocStatusDetailDomain getIdocUpdateFor() {
		return idocUpdateFor;
	}
	public void setIdocUpdateFor(BBIdocStatusDetailDomain idocUpdateFor) {
		this.idocUpdateFor = idocUpdateFor;
	}	
}
