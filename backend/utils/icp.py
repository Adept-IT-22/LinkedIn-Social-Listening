#This module contains ICPs
from utils.locations import locations
from utils.industries import industries

icps = {
    "Small Businesses": {
        "job_titles": {
            "Founder", "CEO", "Marketing Manager", "Customer Service Manager", 
            "Entrepreneur", "Small Business Owner"
        },
        "employees": {"max": 50},
        "revenue": {"max": "Ksh 50M"},
        "industries": industries,
        "locations" : locations
    },
    
    "Mid-Size Companies": {
        "job_titles": {
            "CEO", "CFO", "CTO", "Head of Customer Care", "Operations Manager", 
            "IT Manager", "Customer Experience Manager"
        },
        "employees": {"range": (51, 250)},
        "revenue": {"range": ("Ksh 51M", "Ksh 100M")},
        "industries": industries,
        "locations" : locations
    },
    
    "Large Enterprises": {
        "job_titles": {
            "CEO", "CFO", "CTO", "CMO", "IT Security Manager", 
            "VP Customer Experience", "Chief Data Officer"
        },
        "employees": {"min": 251},
        "revenue": {"min": "Ksh 100M"},
        "industries": industries,
        "locations" : locations
    },
    
    "BPO Providers": {
        "job_titles": {
            "Regional Business Development Manager", "Operations Manager",
            "Client Relations Manager", "Chief Operations Officer"
        },
        "employees": {"range": (100, 1000)},
        "revenue": {"min": "$100M"},
        "industries": industries,
        "locations" : locations
    }
}