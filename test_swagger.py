import unittest
from swagger import Cox

class TestSwagger(unittest.TestCase):
    def setUp(self):
        self.datasetId = "EOhUnqj02Ag"
        self.cox = Cox()

    ''' Checks if the correct response and type is returned for datasetId. '''
    def test_get_datasetId(self):
        response = requests.get("http://api.coxauto-interview.com/api/datasetid")
        assert(response.status_code == 200)
        self.cox.get_dataset_id()
        assert(isinstance(self.cox.datasetId, str))

    ''' Checks if the correct response and type is returned for vehicleIds. '''
    def test_get_vehicleIds(self):
        response = requests.get("http://api.coxauto-interview.com/api/Kx8I_AD22Ag/vehicles")
        assert(response.status_code == 200)
        self.cox.get_dataset_id()
        self.cox.get_vehicle_ids()
        assert(isinstance(self.cox.vehicleIds, list))
        assert(all(isinstance(id, int) for id in self.cox.vehicleIds))

    ''' Checks if the correct answer was posted. '''
    def test_correct_answer(self):
        self.assertEqual(self.cox.get_answer()['success'], True, "Should be True!")

    ''' Checks that the speed of the answer response is no more than 30 seconds. '''
    def test_speed(self):
        total_seconds = (self.cox.get_answer()["totalMilliseconds"] / 1000) % 60
        assert(total_seconds <= 30)

if __name__ == '__main__':
    unittest.main()
