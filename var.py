import json
import csv
import pandas as pd

class RouteVar:
    def __init__(self, RouteId, RouteVarId, RouteVarName, RouteVarShortName, RouteNo, StartStop, EndStop, Distance, Outbound, RunningTime):
        self._RouteId = RouteId
        self._RouteVarId = RouteVarId
        self._RouteVarName = RouteVarName
        self._RouteVarShortName = RouteVarShortName
        self._RouteNo = RouteNo
        self._StartStop = StartStop
        self._EndStop = EndStop
        self._Distance = Distance
        self._Outbound = Outbound
        self._RunningTime = RunningTime
    
    @property
    def RouteId(self):
        return self._RouteId
    @RouteId.setter
    def RouteId(self, RouteId):
        self._RouteId = RouteId
    
    @property
    def RouteVarId(self):
        return self._RouteVarId
    @RouteVarId.setter
    def RouteVarId(self, RouteVarId):
        self._RouteVarId = RouteVarId
    
    @property
    def RouteVarName(self):
        return self._RouteVarName
    @RouteVarName.setter
    def RouteVarName(self, RouteVarName):
        self._RouteVarName = RouteVarName

    @property
    def RouteVarShortName(self):
        return self._RouteVarShortName
    @RouteVarShortName.setter
    def RouteVarShortName(self, RouteVarShortName):
        self._RouteVarShortName = RouteVarShortName

    @property
    def RouteNo(self):
        return self._RouteNo
    @RouteNo.setter
    def RouteNo(self, RouteNo):
        self._RouteNo = RouteNo

    @property
    def StartStop(self):
        return self._StartStop
    @StartStop.setter
    def StartStop(self, StartStop):
        self._StartStop = StartStop

    @property
    def EndStop(self):
        return self._EndStop
    @EndStop.setter
    def EndStop(self, EndStop):
        self._EndStop = EndStop

    @property
    def Distance(self):
        return self._Distance
    @Distance.setter
    def Distance(self, Distance):
        self._Distance = Distance

    @property
    def Outbound(self):
        return self._Outbound
    @Outbound.setter
    def Outbound(self, Outbound):
        self._Outbound = Outbound

    @property
    def RunningTime(self):
        return self._RunningTime
    @RunningTime.setter
    def RunningTime(self, RunningTime):
        self._RunningTime = RunningTime

class RouteVarQuery():
    # This class is used to query the routeVarList
    def __init__(self, fileName):
        self.routeVarList = [] 
        self.loadJson(fileName) 
        
    def __iter__(self):
        return iter(self.routeVarList)

    def loadJson(self, fileName):
        try:
            with open(f"jsonFiles/{fileName}", "r", encoding="utf-8") as file:
                for line in file:
                    data = json.loads(line)
                    for item in data:
                        route_var = RouteVar(**item)
                        self.routeVarList.append(route_var)
        except FileNotFoundError:
            print("File not found.")
        except json.JSONDecodeError:
            print("Error decoding JSON.")
    
    def searchByABC(self, **keyArgs):
        queryList = ["RouteId", "RouteVarId", "RouteVarName", "RouteVarShortName", 
                    "RouteNo", "StartStop", "EndStop", "Distance", "Outbound", "RunningTime"]
        result = []
        for route in self.routeVarList:
            match = True
            for key, value in keyArgs.items():
                routeAttr = str(getattr(route, key, "Wrong key")).lower()
                
                if routeAttr == "wrong key":
                    print(f"The key '{key}' is not in the list. \nPlease use one of the following: {queryList}")
                    return
                if routeAttr != value:
                    match = False
                    break
            if match:
                result.append(route)
        
        if len(result) == 0:
            print("No route found!")
        else:
            return result

    def outputAsCSV(self, list):
        try:
            with open("output/outputCSVRoutes.csv", "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["RouteId", "RouteVarId", "RouteVarName", "RouteVarShortName", "RouteNo", "StartStop", "EndStop", "Distance", "Outbound", "RunningTime"])
                for route in list:
                    writer.writerow([route.RouteId, route.RouteVarId, route.RouteVarName, route.RouteVarShortName, route.RouteNo, route.StartStop, route.EndStop, route.Distance, route.Outbound, route.RunningTime])
            print("CSV file created successfully.")
        except Exception as e:
            print(f"Error creating CSV file: {str(e)}")

    def outputAsCSVByPandas(self, listRoute):
        try:
            df = pd.DataFrame([vars(route) for route in listRoute])
            df.columns = df.columns.str.replace('_', '')
            df.to_csv("output/outputCSVPandasRoutes.csv", index=False, encoding="utf-8")
            print("CSV file created by pandas successfully.")
        except Exception as e:
            print(f"Error creating CSV file: {str(e)}")

    def outputAsJSON(self, listRoute):
        try:
            with open("output/outputJSONRoutes.json", "w", encoding="utf-8") as file:
                for route in listRoute:
                    json.dump(vars(route), file,ensure_ascii = False)
                    file.write('\n')
            print("JSON file created successfully.")
        except Exception as e:
            print(f"Error creating JSON file: {str(e)}")