from var import *
from stop import *
from path import *
from math import sin, cos, sqrt, atan2, radians
from pyproj import Transformer
from time import sleep
from tqdm import tqdm
import heapq
import math
import csv

lat_lng_crs = "EPSG:4326"  
target_crs = "EPSG:3405"  
transformer = Transformer.from_crs(lat_lng_crs, target_crs)

topo = []
visited = {}
edges = {}

def dfs(u):
    global topo
    global visited
    global edges
    visited[u] = True
    for v in edges[u]:
        if not visited[v]:
            dfs(v)
    topo.append(u)

class Graph2():
    def __init__(self, fileName1, fileName2, fileName3):
        varQuery = RouteVarQuery(fileName1)
        stopQuery = StopQuery(fileName2)
        pathQuery = PathQuery(fileName3)

        self.INF = 10**9

        self.numVertices = set([i.StopId for i in tqdm(stopQuery.StopList)])
        self.vertices = {}
        self.timeAll = {}
        self.pathAll = {}
        self.dist = {}
        self.trace = {}
        #count important
        self.cnt = {}
        self.impo = {}

        for i in tqdm(self.numVertices):
            self.vertices[i] = []
            self.timeAll[i] = {}
            self.pathAll[i] = {}
            self.dist[i] = {}
            self.trace[i] = {}
            #count important
            self.cnt[i] = {}
            self.impo[i] = 0

            for j in self.numVertices:
                self.dist[i][j] = self.INF
                self.trace[i][j] = -1
                self.timeAll[i][j] = []
                self.pathAll[i][j] = []
                self.cnt[i][j] = 0

        for routeVarObject in tqdm(varQuery.routeVarList):
            averageSpeed = routeVarObject.Distance / (routeVarObject.RunningTime * 60)
            routeId = routeVarObject.RouteId
            routeVarId = routeVarObject.RouteVarId

            stopObject = stopQuery.searchByABC(RouteId = str(routeId), RouteVarId = str(routeVarId))
            pathObject = pathQuery.searchByABC(RouteId = str(routeId), RouteVarId = str(routeVarId))[0]

            stops = [[stop.StopId, stop.Lat, stop.Lng] for stop in stopObject]
            coordinates = [[x, y] for x, y in zip(pathObject.lat, pathObject.lng)]

            startStopId = stops[0][0]
            stops = stops[1:]

            for stop in stops:
                endStopId = stop[0]

                x = stop[1]
                y = stop[2]

                minDist = self.INF

                for i in range(len(coordinates)):
                    curDist = self.distanceLL(x, y, coordinates[i][0], coordinates[i][1])
                    if curDist < minDist:
                        minDist = curDist
                        closestPoint = i
                
                distance = 0
                path = coordinates[0:closestPoint + 1]
                pathXY = [[*transformer.transform(point[0],point[1])] for point in path]
                coordinates = coordinates[closestPoint:]

                for p1, p2 in zip(pathXY, pathXY[1:]):
                    distance += self.distanceXY(p1[0], p1[1], p2[0], p2[1])

                time = distance / averageSpeed

                self.vertices[startStopId].append(((time, distance), endStopId, (routeId, routeVarId)))  
                self.timeAll[startStopId][endStopId].append([time, routeId, routeVarId])
                self.pathAll[startStopId][endStopId].append([path, routeId, routeVarId])
                
                startStopId = endStopId


    def dijkstraAll(self):
        for st in tqdm(self.numVertices):
            self.dist[st][st] = 0
            self.cnt[st][st] = 1 #count important
            minHeap = []
            heapq.heappush(minHeap,(0, st))
            shortest = {}
            while minHeap:
                w, u = heapq.heappop(minHeap)
                if u in shortest:
                    continue
                shortest[u] = w
                for dis, v, f in self.vertices[u]:
                    if v not in shortest:
                        if w + dis[0] < self.dist[st][v]:
                            self.cnt[st][v] = self.cnt[st][u] #count important
                            self.dist[st][v] = w + dis[0]
                            self.trace[st][v] = [u, f[0], f[1]]
                            heapq.heappush(minHeap, (w + dis[0], v))  
                        elif w + dis[0] == self.dist[st][v]:
                            self.cnt[st][v] += self.cnt[st][u] #count important


    def saveDijkstraAllFile(self):
        try:
            with open('output/allShortestPathsGraph2.txt', 'w') as file:
                for i in tqdm(self.numVertices):
                    file.write(f"Start from {i}: [")
                    for j in self.numVertices:
                        file.write(f"{i}->{j}:{self.dist[i][j]}s; ")
                    file.write("]\n")
            print("Save file successfully")
            file.close()
        except Exception as e:
            print(e)

    def dijkstraOne(self, start):
        dist = {}
        trace = {}
        dist[start] = {}
        trace[start] = {}
        for j in self.numVertices:
            dist[start][j] = self.INF
            trace[start][j] = -1

        trace[start][start] = 1
        dist[start][start] = 0
        minHeap = []
        heapq.heappush(minHeap,(0, start))
        visited = set()

        while minHeap:
            w, u = heapq.heappop(minHeap)
            if u in visited:
                continue
            visited.add(u)
            for dis, v, f in self.vertices[u]:
                if w + dis[0] < dist[start][v]:
                    dist[start][v] = w + dis[0]
                    trace[start][v] = [u, f[0], f[1]]
                    heapq.heappush(minHeap, (w + dis[0], v))
        
        return dist, trace

    def findShortestPath(self, dist, trace, start, end):
        path = []
        path.append(end)
        x = trace[start][end][0]
        while (x != start):
            path.append(x)
            x = trace[start][x][0]
        path.append(start)
        path.reverse()

        tracePath = {}
        for i in path:
            tracePath[i] = {}
        
        for i in range(len(path) - 1):
            routeId = trace[start][path[i+1]][1]
            routeVarId = trace[start][path[i+1]][2]
            for j in self.pathAll[path[i]][path[i+1]]:
                if j[1] == routeId and j[2] == routeVarId:
                    tracePath[path[i]][path[i+1]] = j[0]
                    break

        try:
            with open('output/shortestPathGraph2.txt', 'w') as file:
                file.write(f"Shortest path from {start} to {end}: ")
                for i in path:
                    file.write(f"{i}")
                    if i != end:
                        file.write("->")
                file.write("\n")
                file.write(f"Total time: {dist[start][end]} seconds")
                file.write("\n")
                for i in range(len(path) - 1):
                    if i != end:
                        file.write(f"From {path[i]}->{path[i+1]} in RouteId: {trace[start][path[i+1]][1]} and RouteVarId: {trace[start][path[i+1]][2]}: ")
                        for x, y in tracePath[path[i]][path[i+1]]:
                            file.write(f"[{y},{x}]")
                            if [x,y] != tracePath[path[i]][path[i+1]][-1]:
                                file.write("->")
                        file.write("\n")
            print("Find shortest path and save successfully.")
            file.close()
        except Exception as e:
            print("Error: " + str(e))


        try:
            with open("output/shortestPaths.json", "w", encoding="utf-8") as file:
                file.write('{\n')
                file.write('    "type": "FeatureCollection",\n')
                file.write('    "features": [\n')
                file.write('    {\n')
                file.write('      "type": "Feature",\n')
                file.write('      "properties": {},\n')
                file.write('      "geometry": {\n')
                file.write('        "coordinates": [')

                for i in range(len(path) - 1):
                    for x, y in tracePath[path[i]][path[i+1]]:
                        file.write(f"[{y},{x}]")
                        if [x,y] != tracePath[path[len(path) - 2]][path[len(path) - 1]][-1]:
                            file.write(',')
                file.write('],\n')
                file.write('        "type": "LineString"\n')
                file.write('      }\n')
                file.write('    }')
                file.write('\n')
                file.write('                ]\n')
                file.write('}\n')
            print("GeoJSON file created successfully.")
        except Exception as e:
            print(f"Error creating GeoJSON file: {str(e)}")
    
    def countImportantStops(self):
        global topo
        global visited
        global edges

        for st in tqdm(self.numVertices):
            topo = []
            for i in self.numVertices:
                edges[i] = []
                visited[i] = False
            
            #Remove all edges not shortest path
            for i in self.numVertices:
                for j in self.vertices[i]:
                    if (self.dist[st][i] + j[0][0] == self.dist[st][j[1]]):
                        edges[i].append(j[1])

            for i in self.numVertices:
                if not visited[i]:
                    dfs(i)
            
            dp = {}
            for i in topo:
                dp[i] = 1
                for j in edges[i]:
                    dp[i] += dp[j]

                self.cnt[st][i] *= dp[i]
        
        for v in tqdm(self.numVertices):
            for u in self.numVertices:
                self.impo[v] += self.cnt[u][v]

    def topTenImpoStops(self):
        self.dijkstraAll()
        self.countImportantStops()
        topTen = sorted(self.impo.items(), key = lambda x: x[1], reverse = True)[:10]
        try:
            with open('output/topTenImportantStopsGraph2.txt', 'w', encoding="utf-8") as file:
                file.write("Top 10 important stops in the graph:\n")
                index = 1
                for i in tqdm(topTen):
                    stop = StopQuery("stops.json").searchByABC(StopId = str(i[0]))[0]
                    file.write(f"{index}. StopID: {i[0]}; Important: {i[1]}; Lat: {stop.Lat}; Lng: {stop.Lng}; Name: {stop.Name}; Code: {stop.Code}; StopType: {stop.StopType}; Zone: {stop.Zone}; Ward: {stop.Ward}; AddressNo: {stop.AddressNo}; Street: {stop.Street}; SupportDisability: {stop.SupportDisability}; Status: {stop.Status}; Routes: {stop.Routes}; RouteId: {stop.RouteId}; RouteVarId: {stop.RouteVarId}; Search: {stop.Search}\n")
                    index += 1

            print("Top 10 important stops saved successfully.")
            file.close()
        except Exception as e:
            print("Error: " + str(e))

    def distanceXY(self, x1, y1, x2, y2):
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

    def distanceLL(self, lat1, lng1, lat2, lng2):
        R = 6371.0
        lat1 = radians(lat1)   
        lng1 = radians(lng1)
        lat2 = radians(lat2)
        lng2 = radians(lng2)
        dislng = lng2 - lng1
        dislat = lat2 - lat1
        a = sin(dislat / 2)**2 + cos(lat1) * cos(lat2) * sin(dislng / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c * 1000