import json
import csv
import pandas as pd

class Path:
    def __init__(self, lat, lng, RouteId, RouteVarId):
        self._lat = lat
        self._lng = lng
        self._RouteId = RouteId
        self._RouteVarId = RouteVarId
    
    @property
    def lat(self):
        return self._lat
    @lat.setter
    def lat(self, lat):
        self._lat = lat
    
    @property
    def lng(self):
        return self._lng
    @lng.setter
    def lng(self, lng):
        self._lng = lng
    
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
    
class PathQuery():
    def __init__(self, fileName):
        self.paths = []
        self.loadJson(fileName)
    
    def __iter__(self):
        return iter(self.paths)

    def loadJson(self, fileName):
        try:
            with open(f'jsonFiles/{fileName}', 'r', encoding='utf-8') as file:
                for line in file:
                    data = json.loads(line)
                    self.paths.append(Path(data['lat'], data['lng'], data['RouteId'], data['RouteVarId']))
        except Exception as e:
            print(f"Error loading paths.json: {str(e)}")

    def searchSiteCoordinate(self, latIn, lngIn):
        queryResult = []

        for path in self.paths:
            latCheck = False
            lngCheck = False
            for latVa in path.lat:
                if latIn == str(latVa):
                    latCheck = True
                    break
            for lngVa in path.lng:
                if lngIn == str(lngVa):
                    lngCheck = True
                    break
            if latCheck and lngCheck:
                queryResult.append(path)
        
        if len(queryResult) == 0:
            print("No site found!")
        else:
            return queryResult
            
    def searchByABC(self, **kwargs):
        queryList = ["RouteId", "RouteVarId"];
        queryResult = []

        for path in self.paths:
            match = True
            for key, value in kwargs.items():
                pathAttr = str(getattr(path, key, "Wrong key")).lower()

                if (pathAttr == "wrong key"):
                    print(f"The key '{key}' is not in the list. \nPlease use one of the following: {queryList}")
                    return
                if pathAttr != value:
                    match = False
                    break
            if (match):
                queryResult.append(path)
        
        if len(queryResult) == 0:
            print("No route found!")
        else:
            return queryResult
    
    def outputAsCSV(self, list):
        try:
            with open("output/outputCSV.csv", "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["lat", "lng", "RouteId", "RouteVarId"])
                for path in list:
                    writer.writerow([path.lat, path.lng, path.RouteId, path.RouteVarId])
            print("CSV file created successfully.")
        except Exception as e:
            print(f"Error creating CSV file: {str(e)}")
    
    def outputAsCSVByPandas(self, list):
        try:
            df = pd.DataFrame([vars(path) for path in list])
            df.columns = df.columns.str.replace('_', '')
            df.to_csv("output/outputCSVPandas.csv", index=False, encoding="utf-8")
            print("CSV file created by pandas successfully.")
        except Exception as e:
            print(f"Error creating CSV file: {str(e)}")

    def outputAsJSON(self, list):
        try:
            with open("output/outputJSONPaths.json", "w", encoding="utf-8") as file:
                for path in list:
                    json.dump(vars(path), file, ensure_ascii = False)
                    file.write('\n')
            print("JSON file created successfully.")
        except Exception as e:
            print(f"Error creating JSON file: {str(e)}")
    
    def outputAsGeoJson(self, list):
        try:
            with open("output/outputGeoJson.json", "w", encoding="utf-8") as file:
                file.write('{\n')
                file.write('    "type": "FeatureCollection",\n')
                file.write('    "features": [\n')
                for path in list:
                    file.write('    {\n')
                    file.write('      "type": "Feature",\n')
                    file.write('      "properties": {},\n')
                    file.write('      "geometry": {\n')
                    file.write('        "coordinates": [')
                    for i in range(len(path.lng)):
                        file.write('[' + str(path.lng[i]) + ',' + str(path.lat[i]) + ']')
                        if i != len(path.lng) - 1:
                            file.write(',')
                    file.write('],\n')
                    file.write('        "type": "LineString"\n')
                    file.write('      }\n')
                    file.write('    }')
                    if (list.index(path) != len(list) - 1):
                        file.write(', \n')
                    else:
                        file.write('\n')
                file.write('                ]\n')
                file.write('}\n')
            print("GeoJSON file created successfully.")
        except Exception as e:
            print(f"Error creating GeoJSON file: {str(e)}")

    def changeToPairs(self, data_list):
        try:
            with open("output/outputPairs.json", "w", encoding="utf-8") as file:
                for path in data_list:
                    file.write('[')
                    for i in range(len(path.lat)):
                        file.write('[' + str(path.lat[i]) + ',' + str(path.lng[i]) + ']')
                        if i != len(path.lat) - 1:
                            file.write(',')
                    file.write(']')
                    if (data_list.index(path) != len(data_list) - 1):
                        file.write(', \n')
            print("Pairs file created successfully.")
        except Exception as e:
            print(f"Error creating Pairs file: {str(e)}")
