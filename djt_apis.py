import requests
import json
import csv

BASE_URL = "https://madrid.b1cloud.in:50000/b1s/v1/"
company_db = "DJTRETAILERSTEST"
user_name = "b1cloud\\nav.user01"
password = "India***2018"

session_id = ""

barcode_details_list = []
product_details_list = []
product_price_details_list = []
taxcode_rate_map = {}

def login():
	payload = "{\"CompanyDB\":\"DJTRETAILERSTEST\",\"UserName\":\"b1cloud\\\\nav.user01\",\"Password\":\"India***2018\"\r\n}"
	resp = requests.post(BASE_URL+"Login", headers={"Content-Type":"application/json"}, data=payload)
	# print payload
	#data={"CompanyDB":"DJTRETAILERSTEST","UserName":"b1cloud\\nav.user01","Password":"India***2018"}
	#resp = requests.post(BASE_URL+"Login", headers={"Content-Type":"application/json"}, data=json.dumps(payload))
	
	# print resp.json()
	# print resp.cookies
	# print resp.json()['SessionId']
	return resp

def populate_tax_code(item):
	tax_code = str(item["U_TaxCode"])
	item_code = str(item["ItemCode"].encode('utf-8'))
	print "taxcode_rate_map : " + str(taxcode_rate_map)
	print "tax_code : " + tax_code
	print "itemCode : " + item_code
	if tax_code == "None":
		return
	if tax_code in taxcode_rate_map:
		taxcode_rate_map[tax_code].append(item_code)
	else:
		taxcode_rate_map[tax_code] = []
		taxcode_rate_map[tax_code].append(item_code)


def fetch_item_details(items_list):
	for item in items_list:
		# print item["ItemCode"]
		product_details = {}
		product_details["sku"] = str(item["ItemCode"].encode('utf-8'))
		try:
			product_details["productName"] = str(item["ItemName"].encode('utf-8')).replace(',','_')
		except:
				product_details["productName"] = str(item["ItemName"])
		try:
			product_details["productDescription"] = str(item["ForeignName"].encode('utf-8')).replace(',','_')
		except:
			product_details["productDescription"] = str(item["ForeignName"])
		try:
			inventoryUOM = str(item["InventoryUOM"].encode('utf-8')).replace(',','_')
		except:
			inventoryUOM = str(item["InventoryUOM"])
		if inventoryUOM == "KILOGRAM":
			weightFlag = "YES"
		else:
			weightFlag = "NO"
		product_details["weightFlag"] = weightFlag
		product_details["hsn"] = str(item["ChapterID"])
		product_details_list.append(product_details)

		product_price_details = {}
		product_price_details["sku"] = str(item["ItemCode"].encode('utf-8'))
		price_list = item["ItemPrices"]

		for price in price_list:
			if price["PriceList"] == 1:
				product_price_details["productMRP"] = price["Price"]
			elif price["PriceList"] == 2:
				product_price_details["shopPrice"] = price["Price"]
		product_price_details["isLatestPrice"] = "Y"
		product_price_details_list.append(product_price_details)
		populate_tax_code(item)

def fetch_barcode_details(barcodes_list):
	for barcode in barcodes_list:
		barcode_details = {}
		barcode_details["barcodeId"] = barcode["Barcode"]
		barcode_details["sku"] = barcode["ItemNo"]
		barcode_details_list.append(barcode_details)

def get_items():
	global resp
	resp = login()
	session_id = resp.json()['SessionId']
	headers={"B1SESSION": str(session_id),"ROUTEID": ".node0","Content-Type": "application/json"}
	itemApiURL = "Items"
	nextPage = True;
	while nextPage:
		response = requests.get(BASE_URL+itemApiURL,cookies=resp.cookies)
		data=response.json()
		items_list = response.json()["value"]
		if 'odata.nextLink' in data:
			nextLink=response.json()["odata.nextLink"]
			print(nextLink)
			itemApiURL = "Items" + nextLink[nextLink.find('?'):]
			print(itemApiURL)
		else:
			nextPage=None
		fetch_item_details(items_list)

def get_barcodes():	
	barcodeApiURL="BarCodes"
	nextPage=True;
	while nextPage:
		response = requests.get(BASE_URL+barcodeApiURL,cookies=resp.cookies)
		data=response.json()
		barcodes_list = response.json()["value"]
		if 'odata.nextLink' in data:
			nextLink=response.json()["odata.nextLink"]
			print(nextLink)
			barcodeApiURL = "BarCodes" + nextLink[nextLink.find('?'):]
		else:
			nextPage=None
		fetch_barcode_details(barcodes_list)

def write_to_csv():
	with open('D:\DJT\scripts\\bd.csv', 'w') as bd:
		for barcode_details in barcode_details_list:
			bd.write(barcode_details["barcodeId"]+","+barcode_details["sku"])
			bd.write('\n')
		bd.close()
	with open('D:\DJT\scripts\pd.csv', 'w') as pd:
		for product_details in product_details_list:
			pd.write(product_details["sku"]+","+product_details["productName"]+","+product_details["productDescription"]+","+product_details["hsn"]+","+product_details["weightFlag"])
			pd.write('\n')
		pd.close()
	with open('D:\DJT\scripts\ppd.csv', 'w') as ppd:
		for product_price_details in product_price_details_list:
			ppd.write(product_price_details["sku"]+","+str(product_price_details["shopPrice"])+","+str(product_price_details["productMRP"])+","+product_price_details["isLatestPrice"])
			ppd.write('\n')
		ppd.close()
	with open('D:\DJT\scripts\sku_tax_rel.csv', 'w') as sku_tax_rel:
		for tax_code, items in taxcode_rate_map.items():
			for item in items:
				sku_tax_rel.write(item+","+"DJT-"+tax_code)
				sku_tax_rel.write('\n')
		sku_tax_rel.close()
	with open('D:\DJT\scripts\\tax_category.csv', 'w') as tax_category:
		for tax_code in taxcode_rate_map:
			rate = float(tax_code.split("@")[1])/2
			tax_category.write("DJT-"+tax_code+","+"CGST"+","+"TS"+","+"TS"+tax_code+","+str(rate)+","+"0"+","+"999999999.9999"+","+"1"+","+"1")
			tax_category.write('\n')
			tax_category.write("DJT-"+tax_code+","+"SGST"+","+"TS"+","+"TS"+tax_code+","+str(rate)+","+"0"+","+"999999999.9999"+","+"1"+","+"1")
			tax_category.write('\n')
		tax_category.close()

if __name__ == "__main__" :
	#login()
	get_items()
	get_barcodes()
	# print barcode_details_list
	# print product_price_details_list
	print taxcode_rate_map
	write_to_csv()