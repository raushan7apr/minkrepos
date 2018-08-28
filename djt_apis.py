import requests
from time import sleep, strftime, gmtime, localtime
import os
import json
import csv

# BASE_URL = "https://madrid.b1cloud.in:50000/b1s/v1/"
# company_db = "DJTRETAILERSTEST"
BASE_URL = "https://oklahoma.b1cloud.in:50000/b1s/v1/"
company_db = "DJTRETAILERSTESTTWO"
user_name = "b1cloud\\nav.user01"
password = "India***2018"

session_id = ""

barcode_details_list = []
batch_details_list = []
product_details_list = []
product_price_details_list = []
taxcode_rate_map = {}
item_store_map = []
item_batch_map = {}
warehouse_pricecode_map={}
warehouse_detail_list=[]
storemap={"01":"998","STR01":"999","DUM01":"1000"}
final_folder = '/home/anuragdalia1/dumpyard/DJT/' + str(strftime("%y%m%d", gmtime()))
#final_folder = '/Users/raushankumar/dumpyard/djt/' + str(strftime("%y%m%d", gmtime()))

def login():
	payload = "{\"CompanyDB\":\"DJTRETAILERSTESTTWO\",\"UserName\":\"b1cloud\\\\nav.user01\",\"Password\":\"India***2018\"\r\n}"
	global resp
	resp = requests.post(BASE_URL+"Login", headers={"Content-Type":"application/json"}, data=payload)
	if not os.path.exists(final_folder):
		os.system("sudo mkdir " + final_folder)
	return resp

def populate_tax_code(item):
	tax_code = str(item["U_TaxCode"])
	item_code = str(item["ItemCode"].encode('utf-8'))
	if tax_code == "None":
		return
	if tax_code in taxcode_rate_map:
		taxcode_rate_map[tax_code].append(item_code)
	else:
		taxcode_rate_map[tax_code] = []
		taxcode_rate_map[tax_code].append(item_code)

def fetch_item_details(items_list):
    storeDetailsColumns=["itemCode","storeCode","inStock","Ordered","MinimalStock","MaximalStock"]
    priceDetailsColumns=["itemCode","priceCode","price"]
    barcodeDetailsColumns = ["itemCode","barcodeId"]
    for item in items_list:
        product_details = {}
        itemCode = str(item["ItemCode"].encode('utf-8'))
        product_details["itemCode"] = itemCode
        product_details["productName"] = validateStr(item["ItemName"])
        product_details["productDescription"] = validateStr(item["ForeignName"])
        inventoryUOM = validateStr(item["InventoryUOM"])
        if inventoryUOM == "KILOGRAM":
            weightFlag = "YES"
        else:
            weightFlag = "NO"
        product_details["weightFlag"] = weightFlag
        product_details["hsn"] = str(item["U_HSNCODE"])
        product_details["manageBatch"]=str(item["ManageBatchNumbers"])
        product_details["cat"]=str(item["U_Category"])
        product_details["subCat"] = str(item["U_SUBCAT"])
        product_details["division"] = str(item["U_DIVISION"])
        product_details["UOM"] = inventoryUOM
        product_details["taxInclusive"] = str(item["VatLiable"])
        product_details["noSale"] = str(item["SalesItem"])
        product_details["noMarkdown"] = str(item["NoDiscounts"])
        product_details["department"] = str(item["U_PRODUCTGROUP"])
        product_details["subDepartment"] = str(item["U_BRAND"])
        product_details_list.append(product_details)

        #To save the respective store of sku in item_store_map
        store_list  = item["ItemWarehouseInfoCollection"]
        for store in store_list:
            store_details={}
            store_details["itemCode"]=itemCode
            store_details["storeCode"]=store["WarehouseCode"]
            store_details["inStock"]=store["InStock"]
            store_details["Ordered"]=store["Ordered"]
            store_details["MinimalStock"] = store["MinimalStock"]
            store_details["MaximalStock"] = store["MaximalStock"]
            item_store_map.append(store_details)
        write_csv("updated_item_store_map.csv",item_store_map,storeDetailsColumns)

        #To save all the prices of item in product_price_details_list
        price_list = item["ItemPrices"]
        for price in price_list:
            product_price_details = {}
            product_price_details["itemCode"] = itemCode
            product_price_details["priceCode"] = price["PriceList"]
            product_price_details["price"] = price["Price"]
            product_price_details_list.append(product_price_details)
        write_csv("updated_ppd.csv",product_price_details_list,priceDetailsColumns)

        #To Save all the barcodes of item in barcode_details_list
        barcode_list = item["ItemBarCodeCollection"]
        for barcode in barcode_list:
            barcode_details = {}
            barcode_details["barcodeId"] = barcode["Barcode"]
            barcode_details["itemCode"] = itemCode
            barcode_details_list.append(barcode_details)
        write_csv("updated_bd.csv", barcode_details_list, barcodeDetailsColumns)
        populate_tax_code(item)

def get_items():
    global resp
    resp = login()
    session_id = resp.json()['SessionId']
    headers={"B1SESSION": str(session_id),"ROUTEID": ".node0","Content-Type": "application/json"}
    itemApiURL = "Items"
    itemDetailsColumns=["itemCode","productName","productDescription","weightFlag","hsn","manageBatch","cat","subCat","division","UOM"
    ,"taxInclusive","noSale","noMarkdown","department","subDepartment"]
    nextPage = True
    deleteFile("updated_pd.csv")
    deleteFile("updated_ppd.csv")
    deleteFile("updated_bd.csv")
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
        write_csv("updated_pd.csv",product_details_list,itemDetailsColumns)

def get_warehouse_details():
    warehouseApiURL="Warehouses"
    warehouseColumns=["warehouseCode","cspCode","mrpCode","street","zipCode","location","block","country","floor","streetNo","state","warehouseName","gstin","warehouseType"]
    nextPage = True
    deleteFile("updated_warehouses.csv")
    while nextPage:
        response = requests.get(BASE_URL + warehouseApiURL, cookies=resp.cookies)
        data = response.json()
        warehouse_list = response.json()["value"]
        if 'odata.nextLink' in data:
            nextLink = response.json()["odata.nextLink"]
            warehouseApiURL = "Warehouses" + nextLink[nextLink.find('?'):]
        else:
			nextPage = None
        fetch_warehouse_details(warehouse_list)
        write_csv("updated_warehouses.csv", warehouse_detail_list, warehouseColumns)

def fetch_warehouse_details(warehouse_list):
    for warehouse in warehouse_list:
        warehouseDetails = {}
        warehouseDetails["warehouseCode"] = validateStr(str(warehouse["WarehouseCode"]))
        warehouseDetails["cspCode"]= str(warehouse["U_CSP_PriceList"])
        warehouseDetails["mrpCode"]= str(warehouse["U_MRP_PriceList"])
        warehouseDetails["street"] = validateStr(str(warehouse["Street"]))
        warehouseDetails["zipCode"] = str(warehouse["ZipCode"])
        warehouseDetails["location"] = str(warehouse["Location"])
        warehouseDetails["block"] = validateStr(str(warehouse["Block"]))
        warehouseDetails["country"] = validateStr(str(warehouse["Country"]))
        warehouseDetails["floor"] = validateStr(str(warehouse["BuildingFloorRoom"]))
        warehouseDetails["streetNo"] = str(warehouse["StreetNo"])
        warehouseDetails["state"] = str(warehouse["State"])
        warehouseDetails["warehouseName"] = validateStr(str(warehouse["WarehouseName"]))
        response = requests.get(BASE_URL + "WarehouseLocations(" + str(warehouse["Location"]) + ")", cookies=resp.cookies)
        warehouseDetails["gstin"] = str(response.json()["GSTIN"])
        warehouseDetails["warehouseType"]=str(warehouse["U_TYPE"])
        warehouse_detail_list.append(warehouseDetails)
	print(warehouseDetails)

def get_batch_numbers():
    batchNumberApiURL= "BatchNumberDetails"
    batchNumberColumns = ["ItemCode","BatchMRP","Batch"]
    nextPage=True
    deleteFile("updated_batches.csv")
    while nextPage:
        response = requests.get(BASE_URL+ batchNumberApiURL,cookies=resp.cookies)
        data=response.json()
        batch_list = response.json()["value"]
        if 'odata.nextLink' in data:
            nextLink=response.json()["odata.nextLink"]
            batchNumberApiURL = "BatchNumberDetails" + nextLink[nextLink.find('?'):]
        else:
            nextPage=None
        fetch_batch_numbers(batch_list)
        write_csv("updated_batches.csv",batch_details_list,batchNumberColumns)

def fetch_batch_numbers(batch_list):
    for batch in batch_list:
        itemCode = batch["ItemCode"]
        batch_details = {}
        batch_details["ItemCode"] = itemCode
        batch_details["BatchMRP"] = batch["U_BatchMRP"]
        batch_details["Batch"] = batch["Batch"]
        batch_details_list.append(batch_details)

def write_csv(fileName,data,columns):
    with open(final_folder + '/' + fileName, 'a') as pd:
        for product_details in data:
            content = ''
            for column in columns:
                content  += str(product_details[column]) + ','
            content = content[:-1]
            pd.write(content)
            pd.write('\n')
        pd.close()
    del data[:]

def write_tax():
    with open(final_folder + '/updated_tax_category.csv', 'w') as tax_category:
        for tax_code in taxcode_rate_map:
            rate = float(tax_code.split("@")[1]) / 2
            tax_category.write("DJT-" + tax_code + "," + "CGST" + "," + "TS" + "," + "TS" + tax_code + "," + str(
                rate) + "," + "0" + "," + "999999999.9999" + "," + "1" + "," + "1")
            tax_category.write('\n')
            tax_category.write("DJT-" + tax_code + "," + "SGST" + "," + "TS" + "," + "TS" + tax_code + "," + str(
                rate) + "," + "0" + "," + "999999999.9999" + "," + "1" + "," + "1")
            tax_category.write('\n')
        tax_category.close()
    with open(final_folder + '/updated_sku_tax_rel.csv', 'w') as sku_tax_rel:
        for tax_code, items in taxcode_rate_map.items():
            for item in items:
                sku_tax_rel.write(item + "," + "DJT-" + tax_code)
                sku_tax_rel.write('\n')
        sku_tax_rel.close()

def validateStr(text):
    try:
        #validateStr(str(item["ItemName"].encode('utf-8')))
        text = str(text.encode('utf-8'))
        text = text.replace(",","-")
        text = text.replace("\\n","-")
    except:
        return text
    return text

def deleteFile(fileName):
    if os.path.exists(final_folder + "/" + fileName):
        os.system("sudo rm " + final_folder + "/" + fileName)

if __name__ == "__main__" :
    login()
    get_batch_numbers()
    get_warehouse_details()
    get_items()
    write_tax()
