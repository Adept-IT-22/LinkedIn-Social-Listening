import styles from "@/styles/Search.module.css";
import navbarstyles from "@/styles/Navbar.module.css";
export default function Search() {
    return (
        <div>
            <main className="main-container" style={{marginTop: "3em"}}>
                <h1>Leads</h1>
                <div className="leads-container">
                    <div className="leads-control-buttons">
                        
                    </div>
                    <div className="table-container">
                        <table className="table table-auto">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Job Title</th>
                                    <th>Company</th>
                                    <th>Email</th>
                                </tr>
                            </thead>
                            <tbody>
                                
                            </tbody>
                        </table>    
                    </div>
                </div>
            </main>
        </div>
    );
}