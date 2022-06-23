import http.client
from tabulate import tabulate
import requests
import json
import re
client_id = '9db32cd2-46ea-4e15-9b4d-04db994264dd'

def requestsender(method,url,payload,headers):
    conn = http.client.HTTPSConnection("sandbox.handelsbanken.com")
    if payload != 0:
        conn.request(method,url,payload,headers)
    else:
        conn.request(method,url,headers=headers)
        return conn.getresponse()
    res = conn.getresponse()
    data = res.read()
    return data
def displaytransactions(accounts, authtoken):
    global client_id
    for acc in accounts:
        headers = {
            'X-IBM-Client-Id': client_id,
            'Authorization': authtoken,
            'TPP-Transaction-ID': "REPLACE_THIS_VALUE--",
            'TPP-Request-ID': "REPLACE_THIS_VALUE--",
            'accept': "application/json"
            }
        data = {"httpCode" : "oo"}
        while 'httpCode' in data.keys():
            data = requestsender("GET","/openbanking/psd2/v2/accounts/"+acc["accountId"]+"/transactions",0,headers).read()
            data = json.loads(data.decode("utf-8"))
        transactions = data["transactions"]
        print("------------------------- Account information --------------------------------------------------")
        print("\tAccount ID: ",acc["accountId"])
        print("\tIBAN : ",acc["iban"])
        print("\tBBAN : ", acc["bban"])
        print("\tCurrency : ", acc["currency"])
        print("\tBIC : ", acc["bic"])
        print("\tClearing Number : ",acc["clearingNumber"])
        print("\tAccount Owner : ", acc['ownerName'])
        print("------------------------------------------------------------------------------------------------")
        print("                         Account Transactions")
        print("-------------------------------------------------------------------------------------------------")
        tblist = []
        for tr in transactions:
            amountinfo = tr["amount"]
            tblist.append([tr["status"],amountinfo["currency"],amountinfo["content"],tr["transactionDate"],tr["creditDebit"],tr["remittanceInformation"]])
        print(tabulate(tblist,headers=["Status","Currency","Amount","Transaction Date","Credit/Debit","Remittance Information"],tablefmt='orgtbl'))
        print("--------------------------------------------------------------------------------------------------\n\n")
# Step 1 Get the first Access Token
payload = "client_id="+client_id+"&grant_type=client_credentials&scope=AIS"
heads = {
    'Accept': "application/json",
    'Content-Type': "application/x-www-form-urlencoded",
    'accept': "application/json"
    }
data = json.loads(requestsender("POST","/openbanking/oauth2/token/1.0",payload,heads).decode("utf-8"))
access_token = "Bearer "+data['access_token']
#Step 2 Initiate the consents
payload = "{\"access\":\"ALL_ACCOUNTS\"}"
headers = {
    'X-IBM-Client-Id': client_id,
    'Authorization': access_token,
    'Country': "NL",
    'TPP-Transaction-ID': "c8271b81-4229-5a1f-bf9c-758f11c1f5b1",
    'TPP-Request-ID': "6b24ce42-237f-4303-a917-cf778e5013d6",
    'content-type': "application/json",
    'accept': "application/json"
    }
data = json.loads(requestsender("POST","/openbanking/psd2/v1/consents",payload,headers).decode("utf-8"))
while 'httpCode' in data.keys(): data = json.loads(requestsender("POST","/openbanking/psd2/v1/consents",payload,headers).decode("utf-8"))
consent = data["consentId"]
#Step 3 Getting the Authorization Key by consent granting
headers = { 'accept': "application/json" }
url = "/openbanking/redirect/oauth2/authorize/1.0?client_id="+client_id+"&response_type=code&scope=AIS%3A"+consent+"&redirect_uri=https://www.x23478ww.com/&state=NL"
data = requestsender("GET",url,0,headers)
r = requests.get(data.headers["Location"])
htmlcontent = r.text.splitlines()
authcontent = [s for s in htmlcontent if s.__contains__("var authorizationCode =")]
auth_code = re.findall("'([^']*)'",authcontent[0])[0]
#Step 4 getting the Auth Grant Token
payload = "client_id="+client_id+"&grant_type=authorization_code&scope=AIS:"+consent+"&code="+auth_code+"&redirect_uri=https://www.some234.com/"
headers = {
    'content-type': "application/x-www-form-urlencoded",
    'accept': "application/json"
}
data = json.loads(requestsender("POST","/openbanking/redirect/oauth2/token/1.0",payload,headers).decode("utf-8"))
newaccess_token = "Bearer "+data["access_token"]
#Step 5 Getting all the accounts
headers = {
    'X-IBM-Client-Id': client_id,
    'Authorization': newaccess_token,
    'TPP-Transaction-ID': "some-random-becitstesting",
    'TPP-Request-ID': "as-same-as-mentioned-above",
    'accept': "application/json"
    }
data = {"httpCode" : "oo"}
while 'httpCode' in data.keys():
    data = requestsender("GET","/openbanking/psd2/v2/accounts",0,headers).read()
    data = json.loads(data.decode("utf-8"))
accounts = data['accounts']
displaytransactions(accounts, newaccess_token)

