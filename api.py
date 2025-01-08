import requests
import json,os
from dotenv import load_dotenv

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
    # response = json.loads(response.text)
    # print("Service Creation Response:", response.text)
    return response.text
    
async def create_service(service_type, customer_name, address):
    # 3) Prepare Payload
    payload = {
        "Name": f"New  {service_type} connection in {address} for {customer_name}",
        "ProcessingTypeCode": "SRRQ",  # Service Request type
        "Customer": customer_name,          # Example customer
        # "CustomerID": "1000077",       # Customer ID
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
    # response = json.loads(response.text)
    # print("Service Creation Response:", response.text)
    return response.text

    