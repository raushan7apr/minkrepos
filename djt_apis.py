import requests
import json
import csv

# BASE_URL = "https://madrid.b1cloud.in:50000/b1s/v1/"
# company_db = "DJTRETAILERSTEST"
BASE_URL = "https://oklahoma.b1cloud.in:50000/b1s/v1/"
company_db = "DJTRETAILERSTESTONE"
user_name = "b1cloud\\nav.user01"
password = "India***2018"

session_id = ""

barcode_details_list = []
batch_details_list = {}
product_details_list = []
product_price_details_list = []
taxcode_rate_map = {}
item_store_map = {}
item_batch_map = {}
warehouse_pricecode_map={}
storemap={"01":"998","STR01":"999"}
def login():
	payload = "{\"CompanyDB\":\"DJTRETAILERSTESTTWO\",\"UserName\":\"b1cloud\\\\nav.user01\",\"Password\":\"India***2018\"\r\n}"
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
	print("taxcode_rate_map  " + str(taxcode_rate_map))
	print("tax_code  " + tax_code)
	print("itemCode  " + item_code)
	if tax_code == "None":
		return
	if tax_code in taxcode_rate_map:
		taxcode_rate_map[tax_code].append(item_code)
	else:
		taxcode_rate_map[tax_code] = []
		taxcode_rate_map[tax_code].append(item_code)


def fetch_item_details(items_list):
	for item in items_list:
		product_details = {}
		itemCode = str(item["ItemCode"].encode('utf-8'))
		product_details["sku"] = itemCode
		try:
			product_details["productName"] = validateStr(str(item["ItemName"].encode('utf-8')))
		except:
				product_details["productName"] = str(item["ItemName"])
		try:
			product_details["productDescription"] = validateStr(str(item["ForeignName"].encode('utf-8')))
		except:
			product_details["productDescription"] = str(item["ForeignName"])
		try:
			inventoryUOM = str(item["InventoryUOM"].encode('utf-8'))
		except:
			inventoryUOM = str(item["InventoryUOM"])
		if inventoryUOM == "KILOGRAM":
			weightFlag = "YES"
		else:
			weightFlag = "NO"
		product_details["weightFlag"] = weightFlag
		product_details["hsn"] = str(item["ChapterID"])
		product_details_list.append(product_details)

		#To save the respective store of sku
		store_list  = item["ItemWarehouseInfoCollection"]
		for store in store_list:
			if itemCode in item_store_map:
				item_store_map[itemCode].append(store["WarehouseCode"])
			else:
				item_store_map[itemCode] = []
				item_store_map[itemCode].append(store["WarehouseCode"])

			product_price_details = {}
			product_price_details["sku"] = str(item["ItemCode"].encode('utf-8'))
			price_list = item["ItemPrices"]
			product_price_details["productMRP"] = None
			product_price_details["shopPrice"] = None
			product_price_details["isLatestPrice"] = "Y"
			product_price_details["warehouseCode"] = store["WarehouseCode"]

			for price in price_list:
				if str(price["PriceList"]) == str(warehouse_pricecode_map[store["WarehouseCode"]]["MRP_CODE"]):
					product_price_details["productMRP"] = roundOfDecimal(price["Price"])
				elif str(price["PriceList"]) == str(warehouse_pricecode_map[store["WarehouseCode"]]["CSP_CODE"]):
					product_price_details["shopPrice"] = roundOfDecimal(price["Price"])

			if str(item["ManageBatchNumbers"])=="tYES":
				batchList = batch_details_list.get(itemCode)
				if batchList == None:
					product_price_details_list.append(product_price_details)
				else:
					for batch in batchList:
						temp_product_price_details = {}
						temp_product_price_details["sku"]=product_price_details["sku"]
						temp_product_price_details["shopPrice"]=product_price_details["shopPrice"]
						temp_product_price_details["isLatestPrice"] = "Y"
						temp_product_price_details["warehouseCode"] = product_price_details["warehouseCode"]
						temp_product_price_details["productMRP"]=roundOfDecimal(batch["BatchMRP"])
						product_price_details_list.append(temp_product_price_details)
			else:
				product_price_details_list.append(product_price_details)
		populate_tax_code(item)

def validateStr(text):
	text = text.replace(",","-")
	text = text.replace("\\n","-")
	return text

def roundOfDecimal(value):
	if value is None:
		return 0
	else:
		return round(float(str(value)),2)

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
	get_warehouse_details()
	get_batch_numbers()
	itemApiURL = "Items"
	nextPage = True;
	while nextPage:
		response = requests.get(BASE_URL+itemApiURL,cookies=resp.cookies)
		data=response.json()
		items_list = response.json()["value"]
		if 'odata.nextLink' in data:
			nextLink=response.json()["odata.nextLink"]
			itemApiURL = "Items" + nextLink[nextLink.find('?'):]
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
			barcodeApiURL = "BarCodes" + nextLink[nextLink.find('?'):]
		else:
			nextPage=None
		fetch_barcode_details(barcodes_list)

def get_batch_numbers():
	batchNumberApiURL="BatchNumberDetails"
	nextPage=True
	while nextPage:
		response = requests.get(BASE_URL+batchNumberApiURL,cookies=resp.cookies)
		data=response.json()
		batch_list = response.json()["value"]
		if 'odata.nextLink' in data:
			nextLink=response.json()["odata.nextLink"]
			batchNumberApiURL = "BatchNumberDetails" + nextLink[nextLink.find('?'):]
		else:
			nextPage=None
	fetch_batch_numbers(batch_list)

def fetch_batch_numbers(batch_list):
	for batch in batch_list:
		itemCode = batch["ItemCode"]
		batch_details = {}
		batch_details["BatchMRP"] = batch["U_BatchMRP"]
		batch_details["Batch"] = batch["Batch"]
		if itemCode in batch_details_list:
			batch_details_list[itemCode].append(batch_details)
		else:
			batch_details_list[itemCode] = []
			batch_details_list[itemCode].append(batch_details)

def get_warehouse_details():
	warehouseApiURL="Warehouses"
	nextPage = True
	while nextPage:
		response = requests.get(BASE_URL + warehouseApiURL, cookies=resp.cookies)
		data = response.json()
		warehouse_list = response.json()["value"]
		if 'odata.nextLink' in data:
			nextLink = response.json()["odata.nextLink"]
			warehouseApiURL = "BatchNumberDetails" + nextLink[nextLink.find('?'):]
		else:
			nextPage = None
	fetch_warehouse_details(warehouse_list)

def fetch_warehouse_details(warehouse_list):
	for warehouse in warehouse_list:
		warehouseCode = warehouse["WarehouseCode"]
		warehouseDetails = {}
		warehouseDetails["CSP_CODE"]=warehouse["U_CSP_PriceList"]
		warehouseDetails["MRP_CODE"]=warehouse["U_MRP_PriceList"]
		warehouse_pricecode_map[warehouseCode]=warehouseDetails

def write_to_csv():
	with open('D:\DJT\scripts\\bd.csv', 'w') as bd:
		for barcode_details in barcode_details_list:
			storeList = item_store_map.get(barcode_details["sku"])
			if storeList != None:
				for store in storeList :
					bd.write(barcode_details["barcodeId"]+","+barcode_details["sku"]+","+storemap[store])
					bd.write('\n')
		bd.close()
	with open('D:\DJT\scripts\pd.csv', 'w') as pd:
		for product_details in product_details_list:
			storeList = item_store_map[product_details["sku"]]
			for store in storeList:
				pd.write(product_details["sku"]+","+product_details["productName"]+","+product_details["productDescription"]+","+product_details["hsn"]+","+product_details["weightFlag"]+","+storemap[store])
				pd.write('\n')
		pd.close()
	with open('D:\DJT\scripts\ppd.csv', 'w') as ppd:
		for product_price_details in product_price_details_list:
			ppd.write(product_price_details["sku"]+","+str(product_price_details["shopPrice"])+","+str(product_price_details["productMRP"])+","+product_price_details["isLatestPrice"]+","+storemap[product_price_details["warehouseCode"]])
			ppd.write('\n')
		ppd.close()
	with open('D:\DJT\scripts\sku_tax_rel.csv', 'w') as sku_tax_rel:
		for tax_code, items in taxcode_rate_map.items():
			for item in items:
				for key in warehouse_pricecode_map:
					sku_tax_rel.write(item+","+"DJT-"+tax_code+","+storemap[key])
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
	print(warehouse_pricecode_map)
	write_to_csv()