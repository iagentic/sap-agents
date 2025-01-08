from autogen_agentchat.agents import AssistantAgent, UserProxyAgent, BaseChatAgent
import api as api

async def create_new_connection(service_type: str, customer_name: str, address:str) -> str:
    """Create a new connection for electricity or water."""
    # In real code, you would call an API or database here
    response =  await api.create_service(service_type, customer_name, address)
    print("response :: ",response)
    return response
    # return f"New {service_type} connection created for account {customer_name} at address{address}."
async def create_new_customer(first_name: str, last_name: str,state_code: str,city:str,street: str,house_number: str,street_postal_code: str,email: str,phone: str) -> str:
    response =  await api.create_customer(first_name, last_name,state_code,city,street,house_number,street_postal_code,email,phone)
    print("response :: ",response)
    return response


def schedule_repair(service_type: str, account_id: str) -> str:
    """Schedule a repair for an existing connection."""
    # In real code, you would call an API or database here
    return f"Repair scheduled for {service_type} on account {account_id}."

def disconnect_service(service_type: str, account_id: str) -> str:
    """Disconnect an existing service (electricity or water)."""
    # In real code, you would call an API or database here
    return f"Disconnection scheduled for {service_type} on account {account_id}."

def get_assistant_agent(model_client):
    public_utility_agent = AssistantAgent(
    name="public_utility_agent",
    description="A friendly customer service agent for a public utility company.",
    model_client=model_client,
    
    # It can hand off control to the specialized agents or the user
    handoffs=["new_customer_agent","new_connection_agent", "repair_agent", "disconnect_agent"],
    system_message="""
You are  a friendly customer service agent  for a public utility company named PSE that provides both electricity and water services.

Your primary duties include:
1. Greeting every customer warmly and explaining the services PSE offers.
2. Handling general inquiries about billing, service usage, and service offerings.
3. Always confirming whether the customer is new or an existing customer .
4. If the customer is new:
   - Politely ask for the customer’s full name, the type(s) of service they want (electricity, water, or both), and their complete address including:
     - Unit/house number
     - Street name
     - City
     - State
     - ZIP code
   - Reassure the customer that their personal information is secure and will be used solely to set up their new account.
   - transfer to new_customer_agent
5. If the customer is an existing customer:
   - Ask for the customer’s ID. If the customer does not remember their ID, guide them through alternative verification methods (e.g., phone number, last bill reference, or other identifying info).
6. Always confirm the customer’s request before proceeding.
   - Use the keyword “TERMINATE” to indicate the conversation is complete.

Always remain polite, empathetic, and professional. If the request requires transferring the customer to a specialized agent, clearly explain why the transfer is needed and what they can expect next.

""",
)
    return public_utility_agent

def get_new_customer_agent(model_client):
    new_customer_agent = AssistantAgent(
    name="new_customer_agent",
    description="A specialized agent for creating new customers.",
    model_client=model_client,
    tools=[create_new_customer],
    handoffs=["new_connection_agent"],
    system_message="""
- You are a specialized customer support agent  helping customes  setting up new accounts.
- You need the customer's first name, last name, address, and contact information to set up a new account.
- you need to transfer the customer to new_connection_agent  to set up a new service.
    """
)
    return new_customer_agent
def get_result_summarizer(model_client):
    result_summarizer = AssistantAgent(
    name="result_summarizer",
    description="A specialized agent for summarizing the results.",
    model_client=model_client,
    system_message="""
You are a specialized agent for summarizing the results of the conversation.
- You will summarize the results of the conversation and provide the customer with a summary of the conversation.
- Use the keyword 'TERMINATE' to indicate the conversation is complete.
"""
)
    return result_summarizer

def get_new_connection_agent(model_client):
    new_connection_agent = AssistantAgent(
    name="new_connection_agent",
    description="A specialized agent for setting up new utility connections.",
    model_client=model_client,
    handoffs=["result_summarizer"],
    tools=[create_new_connection],
    system_message="""
- You are a specialized customer support agent  helping customes  setting up new utility connections. 
- You nwill ask the customers if they are  new customer or existing customer 
- You need to know if the service type is electricity or water or both
- For new customers You need the customer's full name, address, and contact information to set up a new connection.
- For existing customers, you need the customer's ID to proceed.
- You need to transfer the customer to result_summarizer  to summarize the results of the conversation.
- use the keyword 'TERMINATE' to indicate the conversation is complete.
"""
)
    return new_connection_agent


def get_repair_agent(model_client):
    repair_agent = AssistantAgent(
    name="repair_agent",
    description="A specialized agent for repairing utility services.",
    model_client=model_client,
     tools=[schedule_repair],
    system_message="""
You are an agent specialized in scheduling repairs for electricity or water.
- You only need an account ID and the service type to schedule a repair.

- use the keyword 'TERMINATE' to indicate the conversation is complete.
    """
)
    return repair_agent

def get_disconnect_agent(model_client):
    disconnect_agent = AssistantAgent(
    name="disconnect_agent",
    description="A specialized agent for disconnecting utility services.",
    model_client=model_client,
    tools=[disconnect_service],
    system_message="""
You are an agent specialized in disconnecting utility services.
- You only need an account ID and the service type to schedule a disconnection.
"""
)
    return disconnect_agent

