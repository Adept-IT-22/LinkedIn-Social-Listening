'use client'
import {useState, useEffect} from 'react';
import styles from "@/styles/Search.module.css";

interface Lead {
    name: string;
    jobTitle: string;
    company: string;
    location: string;
    employeeCount: string;
}

export default function Search() {
    //set state for leads, loading and errors
    const [allLeads, setAllLeads] =useState<Lead[]>([])
    const [leads, setLeads] = useState<Lead[]>([])
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [selectedIcp, setSelectedIcp] = useState("1")
    
    //fetch leads from api
    const fetchAllAuthors = async () => {
        try {
            //set loading to true
            setLoading(true)

            //fetch leads from backend and turn them into json
            const response = await fetch(`http://localhost:5000/all-authors`)
            const data = await response.json()

            //if fetch is succesfull set leads to qualified leads
            if (data.status === "success") {
                const parsedLeads = parseLeadData(data["allAuthors"] || [])
                setLeads(parsedLeads)
            } else {
                setError(data.message)
            }
            //if fetch leads fails set error to error message
        } catch (error) {
            setError("Error fetching leads")
            console.error(error)
            //when done set loading to false
        } finally {
            setLoading(false)
        }
    }

    //function to parse data from search
    const parseLeadData = (leadData: string[]) : Lead[] => {
        //split each lead string into these 5 parts
        return leadData.map(leadString => {
            const parts = leadString.split(" -")
            return {
                name: parts[0] || '',
                jobTitle: parts[1] || '',
                company: parts[2] || '',
                location: parts[3] || '',
                employeeCount: parts[4] || ''
            }
        })
    }

    const filterLeadsByIcp = (icp: string) => {
        if (icp == 'all') {
            setAllLeads(allLeads)
        } else {
            const filteredLeads = allLeads.filter(lead => {
                const employeeCount = lead.employeeCount

                //match employeecount to pattern
                const pattern = "/(\d+)\s*to\s*(\d+) | (\d+/"
                const match = employeeCount.match(pattern)

                if (match) {
                    const minEmployees = match[1] ? parseInt(match[1]) : parseInt(match[3])
                    const maxEmployees = match[2] ? parseInt(match[2]) : parseInt(match[3])

                    //check if icp matches employee count
                    switch(icp){
                        case "1":
                            return maxEmployees <= 50
                        case "2":
                            return minEmployees >= 51 || maxEmployees <= 200
                        case "3":
                            return minEmployees >= 201
                        case "4":
                            return minEmployees >= 1001
                        default:
                            return true
                    }
                }
                return false
            })
            setLeads(filteredLeads)
        }
    }

    return (
        <div>
            <main className="main-container flex flex-col items-center justify-center">
                <h1 className={styles.header}>Leads</h1>
                
                <div className={styles.buttonContainer}>
                    <button onClick= {() => {fetchAllAuthors}}
                    className={styles.searchButton}>Run The Search</button>
                </div>
                {/*show loading or error messages*/}
                {loading && <div>Loading...</div>}
                {error && <div>Error: {error}</div>}

                <div className={styles.pageContent}>
                    <div className={styles.tableContainer}>
                        <table className={styles.table}>
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Job Title</th>
                                    <th>Company</th>
                                    <th>Location</th>
                                    <th>Employee Count</th>
                                </tr>
                            </thead>
                            <tbody>
                                {leads.map((lead, index) => (
                                    <tr key={index}>
                                        <td>{lead.name}</td>
                                        <td>{lead.jobTitle}</td>
                                        <td>{lead.company}</td>
                                        <td>{lead.location}</td>
                                        <td>{lead.employeeCount}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>    
                    </div>
                    <div className={styles.searchContainer}>
                        <form className={styles.searchForm}>
                            <div className={styles.searchInput}>
                                <label htmlFor="category">Category</label>
                                <select id="category">
                                    <option value="Contact Center">Contact Center</option>
                                </select>
                            </div>
                            <div className={styles.searchInput}>
                                <label htmlFor="icp">ICP</label>
                                <select
                                    id = "icp"
                                    value = {selectedIcp}
                                    onChange = {(e) => {e.target.value}}
                                >
                                    <option value="1">1</option>
                                    <option value="2">2</option>
                                    <option value="3">3</option>
                                    <option value="4">4</option>
                                </select>
                            </div>
                        </form>
                        <div className={styles.searchButtonContainer}>
                            <button 
                                className={styles.searchButton}
                                onClick = {() => filterLeadsByIcp(selectedIcp)}
                            >
                                Search
                            </button>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}