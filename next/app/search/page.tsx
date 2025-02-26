import Navbar from "../components/navbar";

export default function Search() {
  return (
    <div>
      <Navbar />
      <div className="main-container flex justify-center items-center h-screen">
        <table className="shadow-2xl border-1 border-white-200 2-6/12">
          <thead>
            <tr>
              <th>Name</th>
              <th>Job Title</th>
              <th>Company</th>
              <th>Email</th>
            </tr>
          </thead>
        </table>
      </div>
    </div>
  );
}
