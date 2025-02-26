import Link from "next/link";
import styles from "@/styles/Navbar.module.css";
export default function Navbar() {
    return (
        <nav className={styles.navbar}>
          <ol className={styles.navbarList}>
            <li className={styles.navbarLink}>
              <Link className={styles.navbarLink} href="/">Dashboard</Link>
            </li>
            <li className={styles.navbarLink}>
              <Link className={styles.navbarLink} href="/search">Leads</Link>
            </li>
          </ol>
          <div className={styles.navSearch}>
            <input className={styles.navSearchInput} type="text" placeholder="Search" />
          </div>
        </nav>
    )
}
