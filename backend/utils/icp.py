#This module contains ICPs
from utils.locations import locations
from utils.industries import industries
from utils.job_titles import job_titles

icps = {
    "Small Businesses": {
        "job_titles": job_titles,
        "employees": {"max": 50},
        "revenue": {"max": "Ksh 50M"},
        "industries": industries,
        "locations" : locations
    },
    
    "Mid-Size Companies": {
        "job_titles": job_titles,
        "employees": {"range": (51, 250)},
        "revenue": {"range": ("Ksh 51M", "Ksh 100M")},
        "industries": industries,
        "locations" : locations
    },
    
    "Large Enterprises": {
        "job_titles": job_titles,
        "employees": {"min": 251},
        "revenue": {"min": "Ksh 100M"},
        "industries": industries,
        "locations" : locations
    },
    
    "BPO Providers": {
        "job_titles": job_titles,
        "employees": {"range": (100, 1000)},
        "revenue": {"min": "$100M"},
        "industries": industries,
        "locations" : locations
    }
}