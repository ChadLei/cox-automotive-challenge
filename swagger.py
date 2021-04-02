import requests
import json
import threading

from collections import defaultdict

class Cox():
    def __init__(self):
        self.url_prefix = "http://api.coxauto-interview.com/api/"
        self.datasetId = ""
        self.vehicleIds = []
        self.all_dealers = defaultdict(list)
        self.all_vehicles = {}
        self.threads = []
        self.d_threads = []

    ''' Sets up get method with the datasetID api url and retrieves the dataset ID. '''
    def get_dataset_id(self):
        try:
            dataset_url = f"{self.url_prefix}datasetId"
            datasetId = requests.get(dataset_url).json()["datasetId"]
            self.datasetId = datasetId
        except requests.exceptions.RequestException as error:
        	print("Error: ", error)

    ''' Sets up get method with the vehicles api url and retrieves all the vehicle IDs. '''
    def get_vehicle_ids(self):
        try:
            vehicleIds_url = f"{self.url_prefix}{self.datasetId}/vehicles"
            vehicleIds = requests.get(vehicleIds_url).json()["vehicleIds"]
            self.vehicleIds = vehicleIds
        except requests.exceptions.RequestException as error:
        	print("Error: ", error)

    ''' Make a get request with each vehicle ID if it hasn't been visited yet. '''
    def get_vehicle_info(self, vehicleId):
        if vehicleId not in self.all_vehicles:
            vehicle_url = f"{self.url_prefix}{self.datasetId}/vehicles/{vehicleId}"
            vehicle_info = requests.get(vehicle_url).json()
            self.all_vehicles[vehicleId] = vehicle_info

    ''' Compiles all vehicle requests needed into threads and runs them all simultaneously. '''
    def compile_vehicle_threads(self):
        for vehicleId in self.vehicleIds:
            d = threading.Thread(target=self.get_vehicle_info, args=(vehicleId,))
            self.threads.append(d)
        for thread in self.threads:
            thread.start()
        for thread in self.threads:
            thread.join()

    ''' Make a get request with each dealer ID if it hasn't been visited yet. '''
    def get_dealer_info(self, vehicleId):
        dealerId = self.all_vehicles[vehicleId]["dealerId"]
        if dealerId not in self.all_dealers:
            dealer_url = f"{self.url_prefix}{self.datasetId}/dealers/{dealerId}"
            dealer_info = requests.get(dealer_url).json()
            self.all_dealers[dealerId] = dealer_info

    ''' Compiles all dealer requests needed into threads and runs them all simultaneously. '''
    def compile_dealer_threads(self):
        for vehicleId in self.vehicleIds:
            d_thread = threading.Thread(target=self.get_dealer_info, args=(vehicleId,))
            self.d_threads.append(d_thread)
        for d_thread in self.d_threads:
            d_thread.start()
        for d_thread in self.d_threads:
            d_thread.join()

    ''' Retrieves info on each vehicle and the corresponding dealer, and then stores it all in a dictionary. '''
    def add_vehicles_to_dealers(self):
        for vehicleId in self.vehicleIds:
            dealerId = self.all_vehicles[vehicleId]["dealerId"]
            self.all_dealers[dealerId]["vehicles"] = self.all_dealers[dealerId].get("vehicles",[])
            self.all_dealers[dealerId]["vehicles"].append({k: v for k,v in self.all_vehicles[vehicleId].items() if k != "dealerId"})

    ''' Initializes all required data and posts the answer. '''
    def get_answer(self):
        self.get_dataset_id()
        self.get_vehicle_ids()
        self.compile_vehicle_threads()
        self.compile_dealer_threads()
        self.add_vehicles_to_dealers()
        dealers = {"dealers": list(self.all_dealers.values())}
        answer_url = f"{self.url_prefix}{self.datasetId}/answer"
        answer_response = requests.post(answer_url, json=dealers).json()
        total_seconds = (answer_response["totalMilliseconds"] / 1000) % 60
        print(f"Success: {answer_response['success']}")
        print(f"Total time: {total_seconds} seconds")
        return answer_response

if __name__ == '__main__':
    cox = Cox()
    cox.get_answer()
