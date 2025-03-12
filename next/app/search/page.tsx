"use client";
import { useState} from "react";
import styles from "@/styles/Search.module.css";

interface Lead {
  name: string;
  jobTitle: string;
  company: string;
  industry: string;
  location: string;
  employeeCount: string;
}

export default function Search() {
  //set state for leads, loading and errors
  const [allLeads, setAllLeads] = useState<Lead[]>([]);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedIcp, setSelectedIcp] = useState("all");

  //fetch leads from eventsource api
  const fetchAllAuthors = () => {
    //initialize states
    setLoading(true); //set loading to true when a new search is run
    setError(null); //set error to null when a new search is run
    setLeads([]); //clear leads whenever a new search is run
    setAllLeads([]); //clear all leads when a new search is run

    //check if streaming is completed
    let streamingCompleted = false;

    //create a new eventsource
    const eventSource = new EventSource("http://localhost:5000/all-authors");

    //open connection to server
    eventSource.onopen = () =>  {
      console.log("Connection to server opened")
    }

    //take the data from the eventsource and parse it
    eventSource.onmessage = (event) => {
      console.log("Received data: ", event.data);
      const data = JSON.parse(event.data);

      //check if data has an error
      if (data.error) {
        setError(data.error);
        console.error(data.error)
        eventSource.close();
        return;
      }

      //otherwise parse the data and put it in leads & all leads
      const author = data.author;
      const parsedLead = parseLeadData([author])[0];

      //update leads and all leads
      setAllLeads((prev) => [...prev, parsedLead]);
      setLeads((prev) => [...prev, parsedLead]);
    };

    //check for errors in each sent event
    eventSource.onerror = (event) => {
      if(!streamingCompleted) {
        console.error("EventSource failed: ", event)
        setError("Connection to server failed");
        eventSource.close();
        setLoading(false);
      }
    };

    //end event
    eventSource.addEventListener("end", () => {
      console.log("Event stream ended")
      streamingCompleted = true
      setLoading(false)
      eventSource.close()
      })  
    
    //end connection if component unmounts
    return () => {
      eventSource.close()
      console.log("Connection closed on clean up")
    }
  };

  //function to parse data from search
  const parseLeadData = (leadData: string[]): Lead[] => {
    //split each lead string into these 6 parts
    return leadData.map((leadString) => {
      const parts = leadString.split(" -");
      return {
        name: parts[0] || "",
        jobTitle: parts[1] || "",
        company: parts[2] || "",
        industry: parts[3] || "",
        location: parts[4] || "",
        employeeCount: parts[5] || "",
      };
    });
  };

  const filterLeadsByIcp = (icp: string) => {
    if (icp == "all") {
      setLeads(allLeads);
    } else {
      const filteredLeads = allLeads.filter((lead) => {
        const employeeCount = lead.employeeCount;

        //match employee count to pattern
        const pattern = /(\d+)\s*to\s*(\d+)/;
        const match = employeeCount.match(pattern);

        if (match) {
          const minEmployees = parseInt(match[1]);
          const maxEmployees = parseInt(match[2]);

          //check if icp matches employee count
          switch (icp) {
            case "1":
              return maxEmployees <= 50;
            case "2":
              return minEmployees >= 51 && maxEmployees <= 200;
            case "3":
              return minEmployees >= 201 && maxEmployees <= 1000;
            case "4":
              return minEmployees >= 1001;
            default:
              return true;
          }
        }
        return false;
      });
      setLeads(filteredLeads);
    }
  };

  //Download Excel File
  const downloadExcel = async() => {
    try{
      //fetch data from backend
      const response = await fetch(
        "http://localhost:5000/download-excel",
        {method: "GET"}
      )

      //check if response is ok
      if(!response.ok){
        throw new Error("Failed to download file")
      }

      //convert response to binary large object
      const blob = await response.blob()

      //create url & anchor tag to download file
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      document.body.appendChild(a)
      a.href = url
      a.download = "Social Listening Results.xlsx"
      a.click() 

      //remove url and anchor tag
      a.remove()
      window.URL.revokeObjectURL(url)
    
    } catch(error) {
      //log any errors
      console.log("Error encountered: ", error)
  }
}

  return (
    <div>
      <main className="main-container flex flex-col items-center justify-center">
        <h1 className={styles.header}>Leads</h1>

        <div className={styles.buttonContainer}>
          <button onClick={fetchAllAuthors} className={styles.searchButton}>
            Run The Search
          </button>
          <button onClick={downloadExcel} className={styles.downloadButton}>
            Download Excel
          </button>
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
                  <th>Industry</th>
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
                    <td>{lead.industry}</td>
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
                  id="icp"
                  value={selectedIcp}
                  onChange={(e) => setSelectedIcp(e.target.value)}
                >
                  <option value="all">All</option>
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
                onClick={() => filterLeadsByIcp(selectedIcp)}
              >
                Filter
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
