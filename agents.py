from autogen_agentchat.agents import AssistantAgent, UserProxyAgent, BaseChatAgent
import api as api

async def create_new_connection(customer_id:str,service_kind: str, service_type: str, customer_name: str, address: str) -> str:
    response = await api.create_service(customer_id,service_type, customer_name, address)
    print("response :: ", response)
    return response

async def create_new_customer(
    first_name: str,
    last_name: str,
    state_code: str,
    city: str,
    street: str,
    house_number: str,
    street_postal_code: str,
    email: str,
    phone: str
) -> str:
    response = await api.create_customer(
        first_name, last_name,
        state_code, city,
        street, house_number,
        street_postal_code,
        email, phone
    )
    print("response :: ", response)
    return response

def schedule_repair(service_type: str, account_id: str) -> str:
    return f"Repair scheduled for {service_type} on account {account_id}."

def disconnect_service(service_type: str, account_id: str) -> str:
    return f"Disconnection scheduled for {service_type} on account {account_id}."

def get_assistant_agent(model_client):
    public_utility_agent = AssistantAgent(
        name="public_utility_agent",
        description="A friendly customer service agent for a public utility company.",
        model_client=model_client,
        handoffs=[
           
            "new_customer_agent",
            "new_connection_agent",
            "repair_agent",
            "disconnect_agent",
        ],
        system_message="""
        You are a friendly customer service agent for PSE, a public utility company providing both electricity and water services.
        After your response always wait for user's response
        Your primary duties include:
        1. Greet every customer warmly and explain the services PSE offers.
        2. Handle general inquiries about billing, service usage, and service offerings.
        3. Always confirm whether the customer is new or an existing customer.
        4. If the customer is new:
           - Politely ask for the customer’s full name, the service type(s) they want (electricity, water, or both),
             and their complete address (house number, street, city, state, ZIP).
           
           - Transfer to new_customer_agent.
        5. If the customer is an existing customer:
           - Ask for the customer’s ID .
           - Confirm the customer’s request (new connection, repair, disconnection, etc.).
           - Transfer to new_connection_agent for new coonections
           - Transfer to repair_agent for repairs.
           - Transfer to disconnect_agent for disconnections.

        6. Use the keyword “TERMINATE” to indicate the conversation is complete.
        7. Remain polite, empathetic, and professional at all times.
        8. service_kind is either new connection or repair or disconnect
        """
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
        You are a specialized customer support agent for creating new customer accounts.
        - Collect the customer's first name, last name, address, and contact information.
        - Call the create_new_customer tool with the provided details.
        - After successfully creating the customer, transfer the conversation to new_connection_agent
          to set up their new service(s).
        """
    )
    return new_customer_agent

def get_new_connection_agent(model_client):
    new_connection_agent = AssistantAgent(
        name="new_connection_agent",
        description="A specialized agent for setting up new utility connections.",
        model_client=model_client,
        # handoffs=["result_summarizer"],
        tools=[create_new_connection],
        system_message="""
        You are a specialized agent for setting up new utility connections.
        - You receive customer information from new_customer_agent (new customer) OR an account ID from
          public_utility_agent (existing customer).
        - Ask for the service type(s) (electricity, water, or both) if not already known.
        - Call create_new_connection tool to provision the requested service(s).
        
        - Use the keyword 'TERMINATE' if the conversation is complete.
        """
    )
    return new_connection_agent

def get_repair_agent(model_client):
    repair_agent = AssistantAgent(
        name="repair_agent",
        description="A specialized agent for repairing utility services.",
        model_client=model_client,
        # tools=[schedule_repair],
        tools=[create_new_connection],
        system_message="""
        You are an agent specialized in scheduling repairs for electricity or water.
        - You only need an account ID and the service type to schedule a repair.
        - Use the keyword 'TERMINATE' to indicate the conversation is complete.
        """
    )
    return repair_agent

def get_disconnect_agent(model_client):
    disconnect_agent = AssistantAgent(
        name="disconnect_agent",
        description="A specialized agent for disconnecting utility services.",
        model_client=model_client,
        # tools=[disconnect_service],
        tools=[create_new_connection],
        system_message="""
        You are an agent specialized in disconnecting utility services.
        - You only need an account ID and the service type to schedule a disconnection.
        """
    )
    return disconnect_agent

def get_result_summarizer(model_client):
    result_summarizer = AssistantAgent(
        name="result_summarizer",
        description="A specialized agent for summarizing the results.",
        model_client=model_client,
        system_message="""
        You are a specialized agent for summarizing the results of the conversation.
        - Summarize the outcome and provide the customer with next steps or confirmation.
        - Use the keyword 'TERMINATE' to indicate the conversation is complete.
        """
    )
    return result_summarizer
