#This module contains ICPs
from utils.locations import locations
from utils.industries import industries
from utils.job_titles import JOB_TITLES

icps = {
    "Small Businesses": {
        "job_titles": JOB_TITLES,
        "employees": {"max": 50},
        "revenue": {"max": "Ksh 50M"},
        "industries": industries,
        "locations" : locations
    },
    
    "Mid-Size Companies": {
        "job_titles": JOB_TITLES,
        "employees": {"range": (51, 250)},
        "revenue": {"range": ("Ksh 51M", "Ksh 100M")},
        "industries": industries,
        "locations" : locations
    },
    
    "Large Enterprises": {
        "job_titles": JOB_TITLES,
        "employees": {"min": 251},
        "revenue": {"min": "Ksh 100M"},
        "industries": industries,
        "locations" : locations
    }
}