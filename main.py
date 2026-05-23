'''
# pip install langgraph langchain langchain-openai langchain-groq langchain-community langchain-tavily psycopg[binary] psycopg_pool python-dotenv tavily-python pip install requests streamlit

# install PostgresSql and create database
CREATE DATABASE langgraph_memory;  ( or open pgadmin4 and create database there )
'''
# LangGraph Multi-Agent Travel Booking System with Long-Term Memory

# main.py

# =========================================================
# AI Travel Planning System using LangGraph
# main.py
# =========================================================

import os
import operator
import re

from typing import TypedDict, Annotated

import psycopg

from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver

from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
)

from langchain_groq import ChatGroq

# =========================================================
# LOAD ENV
# =========================================================

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# =========================================================
# IMPORT TOOLS
# =========================================================

from tools.flight_tool import search_flights
from tools.tavily_tool import tavily_search

from tools.visa_tool import get_visa_info
from tools.currency_tool import get_currency_rates
from tools.budget_tool import get_budget_estimate
from tools.weather_tool import get_weather
from tools.transport_tool import get_transport_info

# =========================================================
# LLM
# =========================================================

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3,
    max_tokens=1200
)


KNOWN_CITIES = [
    "dubai", "paris", "tokyo", "bali", "london", "new york", "singapore",
    "istanbul", "rome", "bangkok", "mumbai", "delhi", "pakistan", "india"
]


def extract_city(query: str) -> str:
    lowered = query.lower()
    for city in KNOWN_CITIES:
        if city in lowered:
            return city.title()

    match = re.search(r"(?:to|for|in|at|visit|travel to)\s+([A-Za-z][A-Za-z\s-]{2,})", query, re.IGNORECASE)
    if match:
        return match.group(1).strip().title()

    return query.strip().split()[0].title() if query.strip() else "Dubai"

# =========================================================
# STATE
# =========================================================

class TravelState(TypedDict):

    messages: Annotated[list[AnyMessage], operator.add]

    user_query: str

    flight_results: str
    hotel_results: str

    visa_info: str
    currency_info: str
    budget_info: str
    weather_info: str
    transport_info: str

    itinerary: str

    llm_calls: int


# =========================================================
# FLIGHT AGENT
# =========================================================

def flight_agent(state: TravelState):

    query = state["user_query"]

    flight_data = search_flights(query)

    return {
        "flight_results": flight_data,

        "messages": [
            AIMessage(content="Flight results fetched")
        ],

        "llm_calls": state.get("llm_calls", 0) + 1
    }


# =========================================================
# HOTEL AGENT
# =========================================================

def hotel_agent(state: TravelState):

    query = f"Best hotels for {state['user_query']}"

    hotel_results = tavily_search(query)

    return {
        "hotel_results": hotel_results,

        "messages": [
            AIMessage(content="Hotel information fetched")
        ],

        "llm_calls": state.get("llm_calls", 0) + 1
    }


# =========================================================
# VISA AGENT
# =========================================================

def visa_agent(state: TravelState):

    query = state["user_query"]

    visa_results = get_visa_info(query)

    return {
        "visa_info": visa_results,

        "messages": [
            AIMessage(content="Visa information fetched")
        ],

        "llm_calls": state.get("llm_calls", 0) + 1
    }


# =========================================================
# CURRENCY AGENT
# =========================================================

# Currency Agent
def currency_agent(state: TravelState):

    query = state["user_query"].lower()

    to_currency = "AED"

    if "india" in query:
        to_currency = "INR"

    elif "europe" in query:
        to_currency = "EUR"

    elif "pakistan" in query:
        to_currency = "PKR"

    currency_results = get_currency_rates(
        amount=1,
        from_currency="USD",
        to_currency=to_currency
    )

    return {
        "currency_info": str(currency_results),
        "messages": [
            AIMessage(content="Currency information fetched")
        ],
        "llm_calls": state.get("llm_calls", 0) + 1
    }


# =========================================================
# BUDGET AGENT
# =========================================================

# Budget Agent
# Budget Agent
def budget_agent(state: TravelState):

    query = state["user_query"].lower()

    flight_price = 350
    hotel_price = 120
    days = 5

    if "paris" in query:
        flight_price = 700
        hotel_price = 180

    elif "tokyo" in query:
        flight_price = 900
        hotel_price = 200

    elif "bali" in query:
        flight_price = 500
        hotel_price = 100

    elif "dubai" in query:
        flight_price = 400
        hotel_price = 120

    budget_results = get_budget_estimate(
        flight_price,
        hotel_price,
        days
    )

    return {
        "budget_info": str(budget_results),
        "messages": [
            AIMessage(content="Budget estimation fetched")
        ],
        "llm_calls": state.get("llm_calls", 0) + 1
    }

# =========================================================
# WEATHER AGENT
# =========================================================

def weather_agent(state: TravelState):

    city = extract_city(state["user_query"])

    weather_results = get_weather(city)

    return {
        "weather_info": weather_results,

        "messages": [
            AIMessage(content=f"Weather information fetched for {city}")
        ],

        "llm_calls": state.get("llm_calls", 0) + 1
    }


# =========================================================
# TRANSPORT AGENT
# =========================================================

# ---------------- TRANSPORT AGENT ----------------

def transport_agent(state: TravelState):

    query = state["user_query"].lower()

    # Default values
    origin = "Dubai Airport"

    if "dubai" in query:
        destination = "Burj Khalifa"

    elif "paris" in query:
        destination = "Eiffel Tower"

    elif "tokyo" in query:
        destination = "Tokyo Tower"

    elif "bali" in query:
        destination = "Ubud"

    else:
        destination = "City Center"

    transport_results = get_transport_info(
        origin,
        destination
    )

    if isinstance(transport_results, dict) and transport_results.get("error"):
        transport_results = {
            "error": (
                f"Transport data unavailable ({transport_results['error']}). "
                f"Check Google Maps API key, billing, and Directions API access."
            )
        }

    return {
        "transport_info": str(transport_results),

        "messages": [
            AIMessage(content="Transport information fetched")
        ],

        "llm_calls": state.get("llm_calls", 0) + 1
    }


# =========================================================
# ITINERARY AGENT
# =========================================================

def itinerary_agent(state: TravelState):

    prompt = f"""
    Create a complete travel itinerary.

    USER REQUEST:
    {state['user_query']}

    FLIGHTS:
    {state['flight_results']}

    HOTELS:
    {state['hotel_results']}

    VISA:
    {state['visa_info']}

    CURRENCY:
    {state['currency_info']}

    BUDGET:
    {state['budget_info']}

    WEATHER:
    {state['weather_info']}

    TRANSPORT:
    {state['transport_info']}
    """

    response = llm.invoke([

        SystemMessage(
            content=(
                "You are an expert AI travel planner. "
                "Do not criticize or complain about tool mismatches. "
                "If any tool data is missing, unavailable, or not clearly usable, "
                "continue with practical assumptions for the user's requested destination. "
                "Never include internal validation complaints in user-facing itinerary text."
            )
        ),

        HumanMessage(content=prompt)

    ])

    return {

        "itinerary": response.content,

        "messages": [response],

        "llm_calls": state.get("llm_calls", 0) + 1
    }


# =========================================================
# FINAL AGENT
# =========================================================

def final_agent(state: TravelState):

    final_prompt = f"""
    Generate FINAL COMPLETE TRAVEL RESPONSE.

    USER QUERY:
    {state['user_query']}

    =================================================

    FLIGHTS:
    {state['flight_results']}

    =================================================

    HOTELS:
    {state['hotel_results']}

    =================================================

    VISA:
    {state['visa_info']}

    =================================================

    CURRENCY:
    {state['currency_info']}

    =================================================

    BUDGET:
    {state['budget_info']}

    =================================================

    WEATHER:
    {state['weather_info']}

    =================================================

    TRANSPORT:
    {state['transport_info']}

    =================================================

    ITINERARY:
    {state['itinerary']}
    """

    response = llm.invoke([

        SystemMessage(
            content="You are an advanced AI travel planning assistant."
        ),

        HumanMessage(content=final_prompt)

    ])

    return {

        "messages": [response],

        "llm_calls": state.get("llm_calls", 0) + 1
    }


# =========================================================
# GRAPH
# =========================================================

graph = StateGraph(TravelState)

# =========================================================
# ADD NODES
# =========================================================

graph.add_node("flight_agent", flight_agent)

graph.add_node("hotel_agent", hotel_agent)

graph.add_node("visa_agent", visa_agent)

graph.add_node("currency_agent", currency_agent)

graph.add_node("budget_agent", budget_agent)

graph.add_node("weather_agent", weather_agent)

graph.add_node("transport_agent", transport_agent)

graph.add_node("itinerary_agent", itinerary_agent)

graph.add_node("final_agent", final_agent)

# =========================================================
# EDGES
# =========================================================

graph.add_edge(START, "flight_agent")

graph.add_edge("flight_agent", "hotel_agent")

graph.add_edge("hotel_agent", "visa_agent")

graph.add_edge("visa_agent", "currency_agent")

graph.add_edge("currency_agent", "budget_agent")

graph.add_edge("budget_agent", "weather_agent")

graph.add_edge("weather_agent", "transport_agent")

graph.add_edge("transport_agent", "itinerary_agent")

graph.add_edge("itinerary_agent", "final_agent")

graph.add_edge("final_agent", END)

# =========================================================
# POSTGRES CHECKPOINTER
# =========================================================

_conn = psycopg.connect(
    DATABASE_URL,
    autocommit=True
)

checkpointer = PostgresSaver(_conn)

checkpointer.setup()

# =========================================================
# COMPILE APP
# =========================================================

app = graph.compile(
    checkpointer=checkpointer
)

# =========================================================
# CLI TESTING
# =========================================================

if __name__ == "__main__":

    config = {
        "configurable": {
            "thread_id": "user_aarohi"
        }
    }

    user_input = input("Enter travel request: ")

    result = app.invoke(

        {
            "messages": [
                HumanMessage(content=user_input)
            ],

            "user_query": user_input,

            "flight_results": "",
            "hotel_results": "",

            "visa_info": "",
            "currency_info": "",
            "budget_info": "",
            "weather_info": "",
            "transport_info": "",

            "itinerary": "",

            "llm_calls": 0
        },

        config=config
    )

    print("\n================ FINAL RESPONSE ================\n")

    for msg in result["messages"]:
        print(msg.content)