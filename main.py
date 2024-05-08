from graph2 import *
from var import *
from stop import *
from path import *

#Graph2 is the main graph class which is used to create the graph and perform operations on it
#Graph1 is just an example of another representation of the graph but with high errors and not recommended to use
print("Loading Graph...")
graph = Graph2("vars.json", "stops.json", "paths.json")

if __name__ == '__main__':
    while True:
        print("-------------------------------------------------------------GRAPH-API-------------------------------------------------------------")
        print("1. See all paths of a StopID (vertice) to another StopID including (Time-Distance-RouteID-RouteVarID)")
        print("2. See all shortest paths of all pairs of StopID including (Time and Distance) using DIJKSTRA'S ALGORITHM  and save it to file")
        print("3. See a shortest path from a Start_Stop_ID to a End_Stop_ID and all the paths in between using DIJKSTRA'S ALGORITHM")
        print("4. See top 10 highest important stops in the graph including (ID-Lat-Lng-StopID-Imortance-Data)") 
        print("5. See all the edges in the graph including (Start_StopID-End_StopID-Time-Distance-RouteID-RouteVarID) (Warning: Might be a lot of data)")
        print("6. Exit")

        choice = int(input("Enter your choice: "))
        if choice == 1:
            stop_id = int(input("Enter StopID: "))
            result = []
            for path in graph.vertices[stop_id]:
                result.append(path)
            for each_path in result:
                print(f"To StopID: {each_path[1]} with Time: {each_path[0][0]}s; Distance: {each_path[0][1]}m; RouteID: {each_path[2][0]}; RouteVarID: {each_path[2][1]}")
        elif choice == 2:
            graph.dijkstraAll()
            graph.saveDijkstraAllFile()
        elif choice == 3:
            start_stop_id = int(input("Enter Start StopID: "))
            end_stop_id = int(input("Enter End StopID: "))
            dist, trace = graph.dijkstraOne(start_stop_id)
            graph.findShortestPath(dist, trace, start_stop_id, end_stop_id)
        elif choice == 4:
            graph.topTenImpoStops()
        elif choice == 5:
            result = []
            for stop_id in graph.numVertices:
                for path in graph.vertices[stop_id]:
                    result.append((stop_id, path[1], path[0][0], path[0][1], path[2][0], path[2][1]))
            for each_path in result:
                print(f"From StopID: {each_path[0]} to StopID: {each_path[1]} with Time: {each_path[2]}s; Distance: {each_path[3]}m; RouteID: {each_path[4]}; RouteVarID: {each_path[5]}")
        elif choice == 6:
            print("Exiting successfully")
            break
        else:
            print("Invalid choice")



        


