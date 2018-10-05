package com.perpule.idocstatus.resource;

import java.util.List;
import javax.ws.rs.Consumes;
import javax.ws.rs.GET;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import com.perpule.idocstatus.bo.BBIdocStatusBO;
import com.perpule.idocstatus.domain.BBIdocStatusDomain;

@Path("v1")
public class BBIdocStatusResource {

	@POST
	@Path("/sendIdocStatus")
	@Consumes(MediaType.APPLICATION_JSON)
	public Response sendIdocStatus(List<BBIdocStatusDomain> bbIdocStatusDomainList) {
		boolean status = new BBIdocStatusBO().sendIdocStatus(bbIdocStatusDomainList);
		if(status) {
			return Response.status(200).entity("Success").build();
		}else {
			return Response.status(500).entity("Failure").build();
		}
	}
	
	
	@GET
	@Produces(MediaType.TEXT_PLAIN)
	public String getHello() {
		return "Deployment Successfull.....";
	}
}
