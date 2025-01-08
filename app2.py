import os

import chainlit as cl
import agents as agents
from chainlit.input_widget import Select, Switch, Slider
from typing import Dict, Optional, Union, Callable
# from typing import Any, Dict, List
import api as api
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent, BaseChatAgent
from autogen_agentchat.conditions import HandoffTermination, TextMentionTermination,MaxMessageTermination
from autogen_agentchat.messages import HandoffMessage
from autogen_agentchat.teams import Swarm, SelectorGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
from dotenv import load_dotenv


load_dotenv() 

model_client = OpenAIChatCompletionClient(
    model="gpt-4o",
    
    api_key=os.getenv("OPENAI_API_KEY"),
    
)
groq_model_client = OpenAIChatCompletionClient(
    # model="gpt-4o",
    model="llama-3.3-70b-specdec",
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY"),
    # api_key=os.getenv("OPENAI_API_KEY"),
    model_capabilities={
        "vision": True,
        "function_calling": True,
        "json_output": True,
    },
)

# model_client = groq_model_client
text_mention_termination = TextMentionTermination("TERMINATE")
max_messages_termination = MaxMessageTermination(max_messages=3)
termination = text_mention_termination | max_messages_termination
team = SelectorGroupChat(
    [agents.get_assistant_agent(model_client), agents.get_new_connection_agent(model_client), agents.get_repair_agent(model_client), agents.get_disconnect_agent(model_client)],
    model_client = model_client,
    termination_condition=termination,
)
async def create_new_connection(service_type: str, customer_name: str, address:str) -> str:
    """Create a new connection for electricity or water."""
    # In real code, you would call an API or database here
    response =  await api.create_service(service_type, customer_name, address)
    print("response :: ",response)
    return response
    # return f"New {service_type} connection created for account {customer_name} at address{address}."

def schedule_repair(service_type: str, account_id: str) -> str:
    """Schedule a repair for an existing connection."""
    # In real code, you would call an API or database here
    return f"Repair scheduled for {service_type} on account {account_id}."

def disconnect_service(service_type: str, account_id: str) -> str:
    """Disconnect an existing service (electricity or water)."""
    # In real code, you would call an API or database here
    return f"Disconnection scheduled for {service_type} on account {account_id}."


# @cl.set_chat_profiles
# async def chat_profile():
#     return [
#         cl.ChatProfile(
#             name="GPT-3.5",
#             markdown_description="The underlying LLM model is **GPT-3.5**.",
#             icon="https://picsum.photos/200",
#         ),
#         cl.ChatProfile(
#             name="GPT-4",
#             markdown_description="The underlying LLM model is **GPT-4**.",
#             icon="https://picsum.photos/250",
#         ),
#     ]

@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="New Water Connection",
            message="Can you help me create a New Water Connection?",
            # icon="/public/idea.svg",
            ),

        cl.Starter(
            label="New Electricity Connection",
            message="Can you help me create a New Electricity Connection?",
            # icon="/public/learn.svg",
            ),
        cl.Starter(
            label="Repair my service",
            message="Can you help me with my service problem?",
            ),
        cl.Starter(
            label="Disconnect Service",
            message="I want to disconnect my service.",
            # icon="/public/write.svg",
            )
        ]
# ...

# @cl.password_auth_callback
# def auth_callback(username: str, password: str):
#     # Fetch the user matching username from your database
#     # and compare the hashed password with the value stored in the database
#     username1 = os.getenv("USERNAME")
#     password1 = os.getenv("PASSCODE")
#     if (username, password) == (username1, password1) :
#         return cl.User(
#             identifier="admin", metadata={"role": "admin", "provider": "credentials"}
#         )
#     else:
#         return None

@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("counter", 0)
    print("A new chat session has started!")
#     team = SelectorGroupChat(
#     [public_utility_agent, new_connection_agent, repair_agent, disconnect_agent],
#     model_client = model_client,
#     termination_condition=termination,
# )
    # user_proxy  = ChainlitUserProxyAgent("Admin")
    # cl.user_session.set("user_proxy", user_proxy)
    # await cl.Message(
    #     content="Hi There ! How can I help you today?",
    # ).send()



@cl.on_message
async def run_conversation(message: cl.Message):
    counter = cl.user_session.get("counter")
    counter += 1
    cl.user_session.set("counter", counter)
    print("counter",counter)
    # await cl.Message(
    #     content=f"Received: {message.content}",
    # ).send()
    # UserProxyAgent.on_messages(message)
    # user_proxy  = cl.user_session.get("user_proxy")
    import asyncio
    # asyncio.run(cl.make_async(public_utility_agent.on_messages(
    #     [TextMessage(content="What is your name? ", source="user")], cancellation_token=CancellationToken()
    # )))

    # response = asyncio.run(public_utility_agent.on_messages(
    #     [TextMessage(content=message.content, source="user")], cancellation_token=CancellationToken()
    # ))
    response = asyncio.run(team.run(task=message.content))
    print("inner_messages",response)
    # print("inner_messages",response.inner_messages)
    # print("chat message",response.chat_message.content)

    # print("Send to UI?",response.messages[-1].content)
    llm_content = ""
    for msg in response.messages:
        llm_content = msg.content 
        print("Send to UI?",msg.content)
    await cl.Message(
        content=llm_content,
    ).send()




