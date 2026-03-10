from chat.router_llm import route_query
from chat.default_llm import generate_default_response
from chat.sql_llm import formatted_response
from query.retreival import retrieve_chunks

def query_router(query: str):
    route = route_query(query)

    if route == "sql_data":
        return formatted_response(query)
    elif route == "cmpy_data":
        return retrieve_chunks(query)
    else:
        return generate_default_response(query)