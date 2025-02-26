import Link from "next/link";
import styles from '@/styles/Navbar.module.css';

export default function Navbar() {
    return (
      <nav className={styles.navbar}>
        <ol className={styles.navbarList}>
          <li className={styles.navbarItem}>
            <Link className={styles.nabvarLink} href="/">Dashboard</Link>
          </li>
          <li className={styles.navbarItem}>
            <Link className={styles.navbarLink} href="/search">Leads</Link>
          </li>
        </ol>
        <div className={styles.searchbar}>
          <input className={styles.navSearch} type = "text" placeholder="Search" />
        </div>
      </nav>
    );
}