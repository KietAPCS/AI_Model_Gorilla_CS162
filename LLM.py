from graph2 import *
from var import *
from stop import *
from path import *
import openai
import urllib.parse
import json

#graph = Graph2("vars.json", "stops.json", "paths.json")

# Report issues
def raise_issue(e, model, prompt):
    issue_title = urllib.parse.quote("[bug] Hosted Gorilla: <Issue>")
    issue_body = urllib.parse.quote(f"Exception: {e}\nFailed model: {model}, for prompt: {prompt}")
    issue_url = f"https://github.com/ShishirPatil/gorilla/issues/new?assignees=&labels=hosted-gorilla&projects=&template=hosted-gorilla-.md&title={issue_title}&body={issue_body}"
    print(f"An exception has occurred: {e} \nPlease raise an issue here: {issue_url}")

# Query Gorilla server
def get_gorilla_response(prompt="", model="gorilla-openfunctions-v1", functions=[]):
    openai.api_key = "EMPTY" 
    openai.api_base = "http://luigi.millennium.berkeley.edu:8000/v1"
    try:
        completion = openai.ChatCompletion.create(
            model="gorilla-openfunctions-v1",
            temperature=0.0,
            messages=[{"role": "user", "content": prompt}],
            functions=functions,
        )
        response = completion.choices[0].message.content
        return response
        
    except Exception as e:
        print("Error:", e, model, prompt)
        
def get_prompt(user_query: str, functions: list = []) -> str:
    if len(functions) == 0:
        return f"USER: <<question>> {user_query}\nASSISTANT: There are no function definitions to call so nothing is done"
    functions_string = json.dumps(functions)
    return f"USER: <<question>> {user_query} <<function>> {functions_string}\nASSISTANT: I am an AI model and I will help you call the correct function in list of functions you provided based on your query. I will loop all the funciton definitions that you give and identify which description is most suitable so that I can choose. However, I will just look for the parameters that users type in, I won't look for the parameters that user don't type in."

def parse_response(response: str) -> tuple:
    start_idx = response.find('(')
    end_idx = response.rfind(')')
    
    if start_idx == -1 or end_idx == -1 or start_idx >= end_idx:
        raise ValueError("Invalid response format")
    
    api_function = response[:start_idx].strip()
    
    attributes_str = response[start_idx + 1:end_idx].strip()
    
    # Splitting attributes_str while considering quotes
    import shlex
    lexer = shlex.shlex(attributes_str, posix=True)
    lexer.whitespace += ','
    lexer.whitespace_split = True
    attributes_list = list(lexer)
    
    attributes = {}
    for pair in attributes_list:
        pair = pair.strip()
        if '=' in pair:
            key, value = pair.split('=', 1)
            key = key.strip()
            # Check for quoted value and remove quotes
            value = value.strip()
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]  # Remove surrounding quotes
            if value != "": attributes[key] = value.lower()
        else:
            raise ValueError(f"Invalid attribute format: {pair}")
    
    return api_function, attributes
    
function_doc = [
    {  
        "name" : "Shortest Path",
        "api_call": "shortest_path",
        "description": "The shortest path between two locations",
        "parameters": [
            {
                "name": "start",
                "description": "Starting location"
            },
            {
                "name": "end",
                "description": "Ending location"
            },
        ]
    },
    {  
        "name" : "Stop Query",
        "api_call": "stop_query",
        "description": "List out all the stops that have information given by user",
        "parameters": [
            {
                "name": "StopId",
                "description": "The stop_id of the stops"
            },
            {
                "name": "Code",
                "description": "The code of the stops"
            },
            {
                "name": "Name",
                "description": "The name of the stops"
            },
            {
                "name": "StopType",
                "description": "The type of the stops"
            },
            {
                "name": "Zone",
                "description": "The zone of the stops"
            },
            {
                "name": "Ward",
                "description": "The ward of the stops"
            },
            {
                "name": "AddressNo",
                "description": "The address_number of the stops"
            },
            {
                "name": "Street",
                "description": "The street of the stops"
            },
            {
                "name": "SupportDisability",
                "description": "The support_disability of the stops"
            },
            {
                "name": "Status",
                "description": "The status of the stops"
            },
            {
                "name": "Lng",
                "description": "The longitude of the stops"
            },
            {
                "name": "Lat",
                "description": "The latitude of the stops"
            },
            {
                "name": "Search",
                "description": "The search for the stops"
            },
            {
                "name": "Routes",
                "description": "The routes of the stops"
            },
            {
                "name": "RouteId",
                "description": "The route_id of the stops"
            },
            {
                "name": "RouteVarId",
                "description": "The route_var_id of the stops"
            }
        ]
    },
    {
        "name" : "RouteVarQuery",
        "api_call": "route_var_query",
        "description": "List out all the route_vars that have information given by user",
        "parameters": [
            {
                "name": "RouteId",
                "description": "The route_id of the route_vars"
            },
            {
                "name": "RouteVarId",
                "description": "The route_var_id of the route_vars"
            },
            {
                "name": "RouteVarName",
                "description": "The route_var_name of the route_vars"
            },
            {
                "name": "RouteVarShortName",
                "description": "The route_var_short_name of the route_vars"
            },
            {
                "name": "RouteNo",
                "description": "The route_no of the route_vars"
            },
            {
                "name": "StartStop",
                "description": "The start_stop of the route_vars"
            },
            {
                "name": "EndStop",
                "description": "The end_stop of the route_vars"
            },
            {
                "name": "Distance",
                "description": "The distance of the route_vars"
            },
            {
                "name": "Outbound",
                "description": "The outbound of the route_vars"
            },
            {
                "name": "RunningTime",
                "description": "The running_time of the route_vars"
            }
        ] 
    },
    {
        "name" : "Path Query",
        "api_call": "path_query",
        "description": "List out all the paths that have information given by user",
        "parameters": [
            {
                "name": "RouteId",
                "description": "The route_id of the paths"
            },
            {
                "name": "RouteVarId",
                "description": "The route_var_id of the paths"
            }
        ]
    },
    {
        "name" : "Top Ten Important Stops",
        "api_call": "top_ten_stops",
        "description": "Top ten important stops in the graph",
        "parameters": [
            {
                "name": "number",
                "description": "The number of most important stops"
            }
        ]
    },
    {
        "name" : "All Shortest Paths",
        "api_call": "all_shortest_paths",
        "description": "All the shortest paths in the graph",
        "parameters": [
            {
                "name": "type",
                "description": "The type of shortest paths to see"
            }
        ]
    },
]

while True:
    print("----------------------------------AI-MODEL----------------------------------")
    print("1. Query about stops")
    print("2. Query about route_var")
    print("3. Query about paths")
    print("4. Query about graph (All shortest paths - Top 10 stops - Shortest path)")
    print("5. Exit")
    
    choice = int(input("Enter your choice: "))
    
    if choice == 1:
        stop = StopQuery("stops.json")
        query = input("Enter your query: ")
        for x in function_doc:
            if x["name"] == "Stop Query":
                function_type = x
                break
        prompt = get_prompt(query, functions=[function_type])
        response = get_gorilla_response(prompt)
        print(response)
        function_call, attributes = parse_response(response)
        print(attributes)
        result = stop.searchByABC(**attributes)
        stop.outputAsJSON(result)
    elif choice == 2:
        route_var = RouteVarQuery("vars.json")
        query = input("Enter your query: ")
        for x in function_doc:
            if x["name"] == "RouteVarQuery":
                function_type = x
                break
        prompt = get_prompt(query, functions=[function_type])
        response = get_gorilla_response(prompt)
        print(response) 
        function_call, attributes = parse_response(response)
        result = route_var.searchByABC(**attributes)
        route_var.outputAsJSON(result)
    elif choice == 3:
        path = PathQuery("paths.json")
        query = input("Enter your query: ")
        for x in function_doc:
            if x["name"] == "Path Query":
                function_type = x
                break
        prompt = get_prompt(query, functions=[function_type])
        response = get_gorilla_response(prompt)
        print(response) 
        function_call, attributes = parse_response(response)
        result = path.searchByABC(**attributes)
        path.outputAsJSON(result)
    elif choice == 4:
        print("Loading graph...")
        graph = Graph2("vars.json", "stops.json", "paths.json")
        while True:
            query = input("Enter your query (enter exit to Exit): ")
            if query == "exit":
                break
            prompt = get_prompt(query, functions=function_doc)
            response = get_gorilla_response(prompt)
            print(response) 
            function_call, attributes = parse_response(response)
            if function_call == "shortest_path":
                start = int(attributes["start"])
                end = int(attributes["end"])
                dist, trace = graph.dijkstraOne(start)
                graph.findShortestPath(dist, trace, start, end)
            elif function_call == "top_ten_stops":
                graph.topTenImpoStops()
            elif function_call == "all_shortest_paths":
                graph.dijkstraAll()
                graph.saveDijkstraAllFile()
    elif choice == 5:
        print("Exiting...")
        break