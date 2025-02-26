import Link from "next/link";
import Search from "../search/page";

export default function Navbar() {
  return (
    <div>
      <nav className="navbar">
        <ol className="navbar-list">
          <li className="navbar-item">
            <Link className="navbar-link" href="/">
              Dashboard
            </Link>
          </li>
          <li className="navbar-item">
            <Link className="navbar-link" href="/search">
              Leads
            </Link>
          </li>
        </ol>
        <div className="searchbar">
          <input className="nav-search" type="text" placeholder="Search" />
        </div>
      </nav>
    </div>
  );
}
