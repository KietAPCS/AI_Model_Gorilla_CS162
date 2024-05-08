import json
import csv
import pandas as pd

class Stop:
    def __init__(self, StopId, Code, Name, StopType, Zone, Ward, AddressNo, 
                Street, SupportDisability, Status, Lng, Lat, Search, Routes, RouteId, RouteVarId):
        self._StopId = StopId
        self._Code = Code
        self._Name = Name
        self._StopType = StopType
        self._Zone = Zone
        self._Ward = Ward
        self._AddressNo = AddressNo
        self._Street = Street
        self._SupportDisability = SupportDisability
        self._Status = Status
        self._Lng = Lng
        self._Lat = Lat
        self._Search = Search
        self._Routes = Routes
        self._RouteId = RouteId
        self._RouteVarId = RouteVarId

    @property
    def StopId(self):
        return self._StopId
    @StopId.setter
    def StopId(self, value):
        self._StopId = value
    
    @property
    def Code(self):
        return self._Code
    @Code.setter
    def Code(self, value):
        self._Code = value
    
    @property
    def Name(self):
        return self._Name
    @Name.setter
    def Name(self, value):
        self._Name = value
    
    @property
    def StopType(self):
        return self._StopType
    @StopType.setter
    def StopType(self, value):
        self._StopType = value
    
    @property
    def Zone(self):
        return self._Zone
    @Zone.setter
    def Zone(self, value):
        self._Zone = value
    
    @property
    def Ward(self):
        return self._Ward
    @Ward.setter
    def Ward(self, value):
        self._Ward = value
    
    @property
    def AddressNo(self):
        return self._AddressNo
    @AddressNo.setter
    def AddressNo(self, value):
        self._AddressNo = value
    
    @property
    def Street(self):
        return self._Street
    @Street.setter
    def Street(self, value):
        self._Street = value
    
    @property
    def SupportDisability(self):
        return self._SupportDisability
    @SupportDisability.setter
    def SupportDisability(self, value):
        self._SupportDisability = value
    
    @property
    def Status(self):
        return self._Status
    @Status.setter
    def Status(self, value):
        self._Status = value
    
    @property
    def Lng(self):
        return self._Lng
    @Lng.setter
    def Lng(self, value):
        self._Lng = value
    
    @property
    def Lat(self):
        return self._Lat
    @Lat.setter
    def Lat(self, value):
        self._Lat = value
    
    @property
    def Search(self):
        return self._Search
    @Search.setter
    def Search(self, value):
        self._Search = value
    
    @property
    def Routes(self):
        return self._Routes
    @Routes.setter
    def Routes(self, value):
        self._Routes = value

    @property
    def RouteId(self):
        return self._RouteId
    @RouteId.setter
    def RouteId(self, value):
        self._RouteId = value

    @property   
    def RouteVarId(self):
        return self._RouteVarId
    @RouteVarId.setter
    def RouteVarId(self, value):
        self._RouteVarId = value

class StopQuery():
    def __init__(self, fileName):
        self.StopList = []
        self.loadStopJson(fileName) 
    
    def __iter__(self):
        return iter(self.StopList)

    def loadStopJson(self, fileName):
        try:
            with open(f"jsonFiles/{fileName}", "r", encoding="utf-8") as file:
                for line in file:
                    data = json.loads(line)
                    for stop in data["Stops"]:
                        stopInstance = Stop(stop["StopId"], stop["Code"], stop["Name"], stop["StopType"], stop["Zone"], stop["Ward"], stop["AddressNo"], 
                                            stop["Street"], stop["SupportDisability"], stop["Status"], stop["Lng"], stop["Lat"], stop["Search"], stop["Routes"], data["RouteId"], data["RouteVarId"])
                        self.StopList.append(stopInstance)
        except Exception as e:
            print(f"Error loading stops.json: {str(e)}")
    
    def searchByABC(self, **keyArgs):
        queryList = ["StopId", "Code", "Name", "StopType", "Zone", "Ward", "AddressNo", 
                    "Street", "SupportDisability", "Status", "Lng", "Lat", "Search", "Routes", "RouteId", "RouteVarId"]
        queryResult = []
        for stop in self.StopList:
            match = True
            for key, value in keyArgs.items():
                stopAttr = str(getattr(stop, key, "Wrong key")).lower()
                
                if (stopAttr == "none"): stopAttr = "null"

                if (stopAttr == "wrong key"):
                    print(f"The key '{key}' is not in the list. \nPlease use one of the following: {queryList}")
                    return
                if stopAttr != value:
                    match = False
                    break
            if (match):
                queryResult.append(stop)

        if len(queryResult) == 0:
            print("No route found!")
        else:
            return queryResult

    def outputAsCSV(self, list):
        try:
            with open("output/outputCSVStops.csv", "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["StopId", "Code", "Name", "StopType", "Zone", "Ward", "AddressNo",
                                "Street", "SupportDisability", "Status", "Lng", "Lat", "Search", "Routes", "RouteId", "RouteVarId"])
                for route in list:
                    writer.writerow([route.StopId, route.Code, route.Name, route.StopType, route.Zone, route.Ward, route.AddressNo,
                                    route.Street, route.SupportDisability, route.Status, route.Lng, route.Lat, route.Search, route.Routes, route.RouteId, route.RouteVarId])
            print("CSV file created successfully.")
        except Exception as e:
            print(f"Error creating CSV file: {str(e)}")
    
    def outputAsCSVByPandas(self, listStop):
        try:
            df = pd.DataFrame([vars(stop) for stop in listStop])
            df.columns = df.columns.str.replace('_', '')
            df.to_csv("output/outputCSVPandasStops.csv", index=False, encoding="utf-8")
            print("CSV file created by pandas successfully.")
        except Exception as e:
            print(f"Error creating CSV file: {str(e)}")
    
    def outputAsJSON(self, listStop):
        try:
            with open("output/outputJSONStops.json", "w", encoding="utf-8") as file:
                for stop in listStop:
                    json.dump(vars(stop), file, ensure_ascii = False)
                    file.write('\n')
            print("JSON file created successfully.")
        except Exception as e:
            print(f"Error creating JSON file: {str(e)}")