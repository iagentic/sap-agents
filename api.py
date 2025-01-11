import requests
import json,os
from dotenv import load_dotenv
from pyodata import Client


load_dotenv() 

# Base URL for the OData service
CUSTOMER_BASE_URL = os.getenv("CUSTOMER_BASE_URL")
CUSTOMER_URL = f"{CUSTOMER_BASE_URL}/IndividualCustomerCollection"

SO_BASE_URL = os.getenv("SERVICE_ORDER_BASE_URL")
SERVICE_URL = f"{SO_BASE_URL}/ServiceRequestCollection"
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

# 1) Initialize session
session = requests.Session()
session.auth = (USERNAME, PASSWORD)

# 2) Fetch CSRF Token
headers = {
    "x-csrf-token": "fetch",
    "Accept": "application/json"
}

# response = session.get(BASE_URL, headers=headers)
# if response.status_code == 200:
#     csrf_token = response.headers.get("x-csrf-token")
#     session.cookies.update(response.cookies)  # Update session with cookies
#     print("CSRF Token:", csrf_token)
async def create_customer(first_name, last_name,state_code,city,street,house_number,street_postal_code,email,phone):
    payload = {
    "FirstName": first_name,
    "LastName": last_name,
    # "FormattedName": "John Doe",
    "CountryCode": "US",
    "StateCode": state_code,
    "City": city,
    "Street": street,
    "HouseNumber": house_number,
    "StreetPostalCode": street_postal_code,
    "Email": email,
    "Phone": phone,
    "RoleCode": "CRM000",  # Example role code for customer
    "LifeCycleStatusCode": "2"  # Active status
}
    CUSTOMER_BASE_URL = os.getenv("CUSTOMER_BASE_URL")
    CUSTOMER_URL = f"{CUSTOMER_BASE_URL}/IndividualCustomerCollection"

    
    USERNAME = os.getenv("USERNAME")
    PASSWORD = os.getenv("PASSWORD")

    # 1) Initialize session
    session = requests.Session()
    session.auth = (USERNAME, PASSWORD)

    # 2) Fetch CSRF Token
    headers = {
        "x-csrf-token": "fetch",
        "Accept": "application/json"
    }
    response = session.get(CUSTOMER_BASE_URL, headers=headers)
    if response.status_code == 200:
        csrf_token = response.headers.get("x-csrf-token")
        session.cookies.update(response.cookies)  # Update session with cookies
        print("CSRF Token:", csrf_token)
    # 4) Send POST Request
    headers = {
        "Content-Type": "application/json",
        "X-CSRF-Token": csrf_token,
        "Accept": "application/json"
    }
    response = session.post(CUSTOMER_URL, headers=headers, json=payload)
    data = json.loads(response.text)
    customer_id = data["d"]["results"]["CustomerID"]
    print("Customer Creation Response:", customer_id)
    # print("Service Creation Response:", response.text)
    return "customer id is "+customer_id
    
async def create_service(customer_id,service_kind="",service_type="", customer_name="", address=""):
    customer_name = await get_customer_by_ID(customer_id)
    # 3) Prepare Payload
    payload = {
        "Name": f"{service_kind}  {service_type} connection in {address} for {customer_name}",
        "ProcessingTypeCode": "SRRQ",  # Service Request type
        "Customer": customer_name,          # Example customer
        "CustomerID":customer_id,     
            # Customer ID
        "ServicePriorityCode": "3",    # Normal priority
        "ServiceRequestLifeCycleStatusCode": "1",  # Open
        "DataOriginTypeCode": "1",     # Manual data entry
        "ServiceAndSupportTeam": "S3110",  # Example support team
        "AssignedTo": "8000000207"     # Example assigned user
    }
    SO_BASE_URL = os.getenv("SERVICE_ORDER_BASE_URL")
    SERVICE_URL = f"{SO_BASE_URL}/ServiceRequestCollection"
    USERNAME = os.getenv("USERNAME")
    PASSWORD = os.getenv("PASSWORD")

    # 1) Initialize session
    session = requests.Session()
    session.auth = (USERNAME, PASSWORD)

    # 2) Fetch CSRF Token
    headers = {
        "x-csrf-token": "fetch",
        "Accept": "application/json"
    }
    response = session.get(SO_BASE_URL, headers=headers)
    if response.status_code == 200:
        csrf_token = response.headers.get("x-csrf-token")
        session.cookies.update(response.cookies)  # Update session with cookies
        print("CSRF Token:", csrf_token)
    # 4) Send POST Request
    headers = {
        "Content-Type": "application/json",
        "X-CSRF-Token": csrf_token,
        "Accept": "application/json"
    }
    
    response = session.post(SERVICE_URL, headers=headers, json=payload)
    data = json.loads(response.text)
    service = data["d"]["results"]["Name"]
    service_url = data["d"]["results"]["__metadata"]["uri"]
    # print("Service Creation Response:", response.text)
    # f" New '{service}', is created for customer  '{customer_id}'"

    return f"  '{service}', is created for customer  '{customer_id}' reference url is {service_url}/?$format=json"


async def get_customer_by_ID(customer_id):
    CUSTOMER_BASE_URL = os.getenv("CUSTOMER_BASE_URL")
    CUSTOMER_URL = f"{CUSTOMER_BASE_URL}/IndividualCustomerCollection('{customer_id}')"
    USERNAME = os.getenv("USERNAME")
    PASSWORD = os.getenv("PASSWORD")

    # 1) Initialize session
    session = requests.Session()
    session.auth = (USERNAME, PASSWORD)

    # 2) Fetch CSRF Token
    headers = {
        "x-csrf-token": "fetch",
        "Accept": "application/json"
    }
    response = session.get(CUSTOMER_BASE_URL, headers=headers)
    if response.status_code == 200:
        csrf_token = response.headers.get("x-csrf-token")
        session.cookies.update(response.cookies)  # Update session with cookies
        print("CSRF Token:", csrf_token)
    
    
    url = f"https://my351356.crm.ondemand.com/sap/c4c/odata/v1/customer/IndividualCustomerCollection?$filter=CustomerID eq '{customer_id}'&$format=json"

    response = session.get(url, headers=headers)
    data = json.loads(response.text)
    customer = data["d"]["results"][0]["FormattedName"]
    print("Customer details ::",customer)
    return customer
    