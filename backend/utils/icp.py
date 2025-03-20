#This module contains ICPs
from locations import Locations

class ICP():
    icps = { 
        "icp1": { 
            "job title": {
            "founder", "ceo", "cto", "cfo", "chief", "president", "outsourcing", 
            "customer"
        },
        "employees": {"max": 50},
        "locations": Locations.locations
        },

        "icp2": { 
            "job title": {
            "founder", "ceo", "cto", "cfo", "chief", "president", "outsourcing", 
            "customer"
        },
        "employees": {"range": (51, 200)},
        "locations": Locations.locations
        },

        "icp3": { 
            "job title": {
            "founder", "ceo", "cto", "cfo", "chief", "president", "outsourcing", 
            "customer"
        },
        "employees": {"range": (201, 1000)},
        "locations": Locations.locations
        },

        "icp4": { 
            "job title": {
            "founder", "ceo", "cto", "cfo", "chief", "president", "outsourcing", 
            "customer"
        },
        "employees": {"min": 1001},
        "locations": Locations.locations
        }
    }
