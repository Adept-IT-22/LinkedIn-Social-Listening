import styles from "../styles/Homepage.module.css";
import Image from "next/image";
import Link from "next/link";

export default function Home() {
  return (
    <div className="">
      <main className={styles.mainContainer}>
        <div className={styles.header}>Dashboard</div>
        <div className={styles.dataAndChartContainer}>
          <div className={styles.dataContainer}>
          
            <div className={styles.contentContainer}>
              <p className={styles.containerHeader}>New Leads</p>
              <hr className={styles.dividingLine}/>
              <h1>17</h1>
            </div>
            <div className={styles.contentContainer}>
              <p className={styles.containerHeader}>Emails Sent</p>
              <hr className={styles.dividingLine}/>
              <h1>8</h1>
            </div>
            <div className={styles.contentContainer}>
              <p className={styles.containerHeader}>abc</p>
              <hr className={styles.dividingLine} />
              <h1>xyz</h1>
            </div>
          </div>
          <div className={styles.bothChartsContainer}>
            <div className={styles.chartContainer}>
              <p className={styles.containerHeader}>Lead Communication</p>
              <hr className={styles.dividingLine} />
              <div className={styles.chartData}>
                <div className={styles.leadData}>
                  <ol className={styles.dataList}>
                    <div className={styles.dataItem}>
                      <li></li>
                      <p>Total Leads: </p>
                      <h3>63</h3>
                    </div>
                    <div className={styles.dataItem}>
                      <li></li>
                      <p>Emails Sent: </p>
                      <h3>59</h3>
                    </div>
                    <div className={styles.dataItem}>
                      <li></li>
                      <p>Responded: </p>
                      <h3>42</h3>
                    </div>
                    <div className={styles.dataItem}>
                      <li></li>
                      <p>Ignored: </p>
                      <h3>7</h3>
                    </div>
                  </ol>
                </div>
                <div className={styles.actualChart}></div>
              </div>
            </div>
            <div className={styles.contentContainer}>
              <p className={styles.containerHeader}>xyz</p>
              <hr className={styles.dividingLine} />
              <h1>xyz</h1>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
