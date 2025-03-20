import styles from "../styles/Homepage.module.css";
import Image from "next/image";
import Link from "next/link";

export default function Home() {
  return (
    <div className="">
      <main className={styles.mainContainer} style={{ marginTop: "3em" }}>
        <div className={styles.header}>Dashboard</div>
        <div className={styles.dataContainer}>
          <div className={styles.contentContainer}>
            <p>New Leads</p>
            <h1>17</h1>
          </div>
          <div className={styles.contentContainer}>
            <p>Emails Sent</p>
            <h1>8</h1>
          </div>
          <div className={styles.contentContainer}>
            <p>Abc</p>
            <h1>xyz</h1>
          </div>
        </div>
      </main>
    </div>
  );
}
