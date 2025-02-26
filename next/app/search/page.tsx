'use client'
import {useState, useEffect} from 'react';
import styles from "@/styles/Search.module.css";
import navbarstyles from "@/styles/Navbar.module.css";

interface Lead {
    name: string;
    jobTitle: string;
    company: string;
    location: string;
    employeeCount: number;
}

export default function Search() {
    //set state for leads, loading and errors
    const [leads, setLeads] = useState<Lead[]>([])
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)
    
    //fetch leads from api
    const fetchLeads = async () => {
        try {
            //set loading to true
            setLoading(true)

            //fetch leads from backend and turn them into json
            const response = await fetch("http://localhost:5000")
            const data = await response.json()

            //if fetch is succesfull set leads to qualified leads
            if (data.status === "success") {
                setLeads(data.qualifiedLeads)
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

    //side effect to fetch leads
    useEffect(() => {
        fetchLeads()
    }, [])

    //search button code
    //const handleSearch = async () => {
        //try {
            //setLoading(true)
            //const response = await fetch("https://localhost:5000", {
                //method: 'POST', 
                //headers: {
                    //'Content-Type': 'application/json',
                //},
                //body: JSON.stringify({
                    ////search parameters
                //})
            //})
            //const data = await response.json()
            //setLeads(data)
        //} catch (error) {
            //setError("Error searching leads")
            //console.error(error)
        //} finally {
            //setLoading(false)
        //}
    //}
    //show Loading... if loading
    if (loading) return <div>Loading...</div>

    //show error if there's an error
    if (error) return <div>Error: {error}</div>

    return (
        <div>
            <main className="main-container flex flex-col items-center justify-center" style={{marginTop: "3em"}}>
                <h1>Leads</h1>
                <div className={styles.leadsContainer}>
                    <div className="leads-control-buttons">
                        <button onClick={fetchLeads}
                        className="bg-blue-500 text-white px-4 py-2 rounded-md">Search</button>
                    </div>
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
                                        <td>{lead.location}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>    
                    </div>
                </div>
            </main>
        </div>
    );
}