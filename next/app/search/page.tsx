"use client";
import { useState, useEffect } from "react";
import styles from "@/styles/Search.module.css";

interface Lead {
  name: string;
  job_title: string;
  company: string;
  industry:string;
  location: string;
  employee_count: string;
  icp: string;
  score: number;
  linkedin_post: string;
}

export default function Search() {
  //set state for leads, loading ,errors and ICP
  const [allLeads, setAllLeads] = useState<Lead[]>([]);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedIcp, setSelectedIcp] = useState("all");

  //fetch leads from eventsource api
  const fetchAllAuthors = () => {
    // Initialize states
    setLoading(true);
    setError(null);
    setLeads([]);
    setAllLeads([]);

    // Create a new EventSource
    const eventSource = new EventSource("http://localhost:5000/stream-leads");

    eventSource.onmessage = (event) => {
      try {
        console.log("Received data: ", event.data);
        const data = JSON.parse(event.data);

        // Check if data has an error
        if (data?.error) {
          setError(data.error);
          eventSource.close();
          return;
        }

        // Validate required fields
        if (!data?.author || !data?.icp || data?.score === undefined) {
          console.warn("Incomplete data received:", data);
          return;
        }

        // Parse and enhance the lead data
        const parsedLead = parseLeadData([data.author])[0];
        const leadWithDetails: Lead = {
          ...parsedLead,
          icp: data.icp,
          score: data.score,
        };

        // Update state using functional updates
        setAllLeads((prev) => [...prev, leadWithDetails]);
        setLeads((prev) => [...prev, leadWithDetails]);
      } catch (parseError) {
        console.error("Error parsing event data:", parseError);
        setError("Failed to parse lead data");
        eventSource.close();
      }
    };

    eventSource.onerror = () => {
      // Only handle error if not already closed
      if (eventSource.readyState !== EventSource.CLOSED) {
        if (eventSource.readyState == EventSource.CONNECTING) {
          console.log("Streaming has been completed.");
          eventSource.close();
          setLoading(false);
        } else {
          setError("Connection to server failed");
          eventSource.close();
          setLoading(false);
        }
      }
    };

    // Cleanup function for component unmount
    return () => {
      eventSource.close();
    };
  };

  //function to parse data from search
  const parseLeadData = (leadData: any[]): Lead[] => {
    try {
      return leadData.map((lead) => ({
        name: lead.name || "",
        job_title: lead.job_title || "",
        company: lead.company || "",
        industry: lead.industry || "",
        location: lead.location || "",
        employee_count: lead.employee_count || "",
        linkedin_post: lead.linkedin_post || "",
        icp: lead.icp || "Unknown",
        score: lead.score || 0,
      }));
    } catch (e) {
      console.error("Error parsing leads", e);
      return [];
    }
  };

  const filterLeadsByIcp = (icp: string) => {
    if (icp == "all") {
      setLeads(allLeads);
    } else {
      const filteredLeads = allLeads.filter((lead) => {
        // First try to use the icp field if available
        if (lead.icp) {
          switch (icp) {
            case "1":
              return lead.icp === "Small Businesses";
            case "2":
              return lead.icp === "Mid-Size Companies";
            case "3":
              return lead.icp === "Large Enterprises";
            case "4":
              return lead.icp === "BPO Providers";
            default:
              return true;
          }
        }
        const employeeCount = lead.employee_count;
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
  const downloadExcel = async () => {
    try {
      //fetch data from backend
      const response = await fetch("http://localhost:5000/download-excel", {
        method: "GET",
      });

      //check if response is ok
      if (!response.ok) {
        throw new Error("Failed to download file");
      }

      //convert response to binary large object
      const blob = await response.blob();

      //create url & anchor tag to download file
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      document.body.appendChild(a);
      a.href = url;
      a.download = "Social Listening Results.xlsx";
      a.click();

      //remove url and anchor tag
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      //log any errors
      console.log("Error encountered: ", error);
    }
  };

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
                  <th>LinkedIn Post</th>
                  <th>ICP</th>
                  <th>Score</th>
                </tr>
              </thead>
              <tbody>
                {leads.map((lead, index) => {
                  let icpClass = ""; //variable to hold icp class

                  switch (lead.icp.toLowerCase()) {
                    case "small businesses":
                      icpClass = "icp-1";
                      break;
                    case "mid-size companies":
                      icpClass = "icp-2";
                      break;
                    case "large enterprises":
                      icpClass = "icp-3";
                      break;
                    case "bpo providers":
                      icpClass = "icp-4";
                      break;
                    default:
                      icpClass = "";
                      break;
                  }

                  return (
                    <tr key={index} className={icpClass}>
                      <td>{lead.name}</td>
                      <td>{lead.job_title}</td>
                      <td>{lead.company}</td>
                      <td>{lead.industry}</td>
                      <td>{lead.location}</td>
                      <td>{lead.employee_count}</td>
                      <td>{lead.linkedin_post}</td>
                      <td>{lead.icp}</td>
                      <td>{lead.score}</td>
                    </tr>
                  );
                })}
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
