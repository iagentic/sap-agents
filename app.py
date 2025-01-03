import os

import chainlit as cl
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

USER_PROXY_MESSAGE = '''A human admin. Interact with the planner to discuss the plan. 
Plan execution needs to be approved by this admin.'''

model_client = OpenAIChatCompletionClient(
    model="gpt-4o",
    # api_key="YOUR_API_KEY",
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

public_utility_agent = AssistantAgent(
    name="public_utility_agent",
    model_client=model_client,
    # It can hand off control to the specialized agents or the user
    handoffs=["user","new_connection_agent", "repair_agent", "disconnect_agent"],
    system_message="""
- You are a customer service agent for a public utility company that provides electricity and water.
- You handle general questions about billing, service usage, and service offerings.
- You will ask the customer if they want a new service or repair existing service or disconnect existing service 
- If a customer wants to create a new connection, you will collect customer full name, service type  and address with unit/house number, street name, city state and zip code and then hand off to new connection agent.
- If a customer wants a repair ask for customer id and then  hand off to repair_agent.
- If a customer wants to disconnect a service ask for customer id and then hand off to disconnect agent.
- If a customer greets respond with a greeting.

- use the keyword 'TERMINATE' to indicate the conversation is complete.
""",
)
new_connection_agent = AssistantAgent(
    name="new_connection_agent",
    model_client=model_client,
    # It can hand off back to public_utility_agent or to the user
    # handoffs=["public_utility_agent", "user"],
    # Tools this agent can directly call
    tools=[create_new_connection],
    system_message="""You are an agent specialized in creating new connections for electricity or water.
- You only need customer name, address  and the type of service (electricity or water).
- If you need more information from the customer(e.g., name), ask the customer

- use the keyword 'TERMINATE' to indicate the conversation is complete.
""",
)

# ===== Agent 3: Repair Agent =====
repair_agent = AssistantAgent(
    name="repair_agent",
    model_client=model_client,
    handoffs=["public_utility_agent", "user"],
    tools=[schedule_repair],
    system_message="""You are an agent specialized in scheduling repairs for electricity or water.
- You only need an account ID and the service type to schedule a repair.

- use the keyword 'TERMINATE' to indicate the conversation is complete.
""",
)

# ===== Agent 4: Disconnect Agent =====
disconnect_agent = AssistantAgent(
    name="disconnect_agent",
    model_client=model_client,
    handoffs=["public_utility_agent", "user"],
    tools=[disconnect_service],
    system_message="""You are an agent specialized in disconnecting a service (electricity or water).
- You only need an account ID and the service type to process disconnection.
- If you need more info, request user, then hand off to the user.
- After disconnecting, hand off to public_utility_agent to finalize.
- use the keyword 'TERMINATE' to indicate the conversation is complete.
""",
)

# ===== Termination condition & the Swarm =====
# 1) If an agent specifically hands off to user (depending on your business flow), or
# 2) The word "TERMINATE" appears in agent messages, we end the conversation.
text_mention_termination = TextMentionTermination("TERMINATE")
max_messages_termination = MaxMessageTermination(max_messages=3)
termination = text_mention_termination | max_messages_termination

# Create a "team" or group of agents that can collaborate on a single conversation
# team = Swarm(
#     [public_utility_agent, new_connection_agent, repair_agent, disconnect_agent],
#     termination_condition=termination,
# )

team = SelectorGroupChat(
    [public_utility_agent, new_connection_agent, repair_agent, disconnect_agent],
    model_client = model_client,
    termination_condition=termination,
)
async def ask_helper(func, **kwargs):
    res = await func(**kwargs).send()
    while not res:
        res = await func(**kwargs).send()
    return res

class ChainlitAssistantAgent(AssistantAgent):
    """
    Wrapper for AutoGens Assistant Agent
    """
    def send(
        self,
        message: Union[Dict, str],
        recipient: BaseChatAgent,
        request_reply: Optional[bool] = None,
        silent: Optional[bool] = False,
    ) -> bool:
        cl.run_sync(
            cl.Message(
                content=f'*Sending message to "{recipient.name}":*\n\n{message}',
                author=self.name,
            ).send()
        )
        super(ChainlitAssistantAgent, self).send(
            message=message,
            recipient=recipient,
            request_reply=request_reply,
            silent=silent,
        )
        
class ChainlitUserProxyAgent(UserProxyAgent):
    """
    Wrapper for AutoGens UserProxy Agent. Simplifies the UI by adding CL Actions.
    """
    def get_human_input(self, prompt: str) -> str:
        if prompt.startswith(
            "Provide feedback to chat_manager. Press enter to skip and use auto-reply"
        ):
            res = cl.run_sync(
                ask_helper(
                    cl.AskActionMessage,
                    content="Continue or provide feedback?",
                    actions=[
                        cl.Action( name="continue", value="continue", label="✅ Continue" ),
                        cl.Action( name="feedback",value="feedback", label="💬 Provide feedback"),
                        cl.Action( name="exit",value="exit", label="🔚 Exit Conversation" )
                    ],
                )
            )
            if res.get("value") == "continue":
                return ""
            if res.get("value") == "exit":
                return "TERMINATE"

        reply = cl.run_sync(ask_helper(cl.AskUserMessage, content=prompt, timeout=60))

        return reply["output"].strip()

    def send(
        self,
        message: Union[Dict, str],
        recipient: BaseChatAgent,
        request_reply: Optional[bool] = None,
        silent: Optional[bool] = False,
    ):
        #cl.run_sync(
            #cl.Message(
            #    content=f'*Sending message to "{recipient.name}"*:\n\n{message}',
            #    author=self.name,
            #).send()
        #)
        super(ChainlitUserProxyAgent, self).send(
            message=message,
            recipient=recipient,
            request_reply=request_reply,
            silent=silent,
        )




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



@cl.on_chat_start
async def on_chat_start():
    print("A new chat session has started!")
    user_proxy  = ChainlitUserProxyAgent("Admin")
    cl.user_session.set("user_proxy", user_proxy)



@cl.on_message
async def run_conversation(message: cl.Message):
    # await cl.Message(
    #     content=f"Received: {message.content}",
    # ).send()
    # UserProxyAgent.on_messages(message)
    user_proxy  = cl.user_session.get("user_proxy")
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




