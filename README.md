# Automated Multi-Source Job Tracking Pipeline

A serverless data pipeline built with **Google Apps Script** and **Google Sheets** that automatically aggregates, filters, and logs targeted job opportunities from major platforms like LinkedIn, Indeed, and public developer boards. 

---

## Project Architecture & Data Flow

```text
[ JSearch API (LinkedIn/Indeed) ] ──┐
                                   ├──> [ Apps Script Processing Engine ] ──> [ Strict Validation Rules ] ──> [ Google Sheets Database ]
[ Arbeitnow API (Public Feed) ]  ──┘        (Deduplication & Transformation)

```


1. **Extraction (ELT - Extract):** Connects to the JSearch API (aggregating LinkedIn, Indeed, and Glassdoor) and public job boards (Arbeitnow) using secure HTTP requests.
2. **Transformation & Validation:** Evaluates incoming records against a rigorous set of business rules:
   * **Target Role Filtering:** Isolates specific titles (Data Analyst, Analytics Engineer, Data Engineer, Data Specialist, Visualization Specialist).
   * **Exclusion Guards:** Instantly drops irrelevant classifications (Sales, Finance, Management, Directors, Software Engineering/DevOps).
   * **Seniority Constraints:** Enforces strict leveling rules (e.g., entry-level allowed exclusively for Data Engineering; mid-level+ required for Analytics/BI).
   * **Geographic & Compliance Routing:** Validates local listings (Nigeria/Remote/Hybrid) against international remote or visa-sponsored positions.
   * **Freshness Window:** Restricts pipeline intake to listings posted within the last 30 days.
3. **Loading (Load):** Checks existing records in Google Sheets to prevent duplicate entries and appends clean, verified rows automatically.

---

## Key Features

* **Zero Infrastructure Cost:** Runs entirely on serverless Google Apps Script infrastructure with automated daily time-driven triggers.
* **Smart Deduplication:** Cross-references incoming application URLs with existing sheet rows to maintain a pristine database.
* **Robust Error Handling:** Features safe exception logging and muted HTTP exception handling to ensure pipeline stability during API downtime.

---

## Tech Stack & Tools

* **Language:** JavaScript (Google Apps Script V8 Engine)
* **Storage & BI Interface:** Google Sheets
* **APIs & Integrations:** JSearch (RapidAPI), Arbeitnow API
* **Version Control:** Git & GitHub

---

## Setup and Installation Guide

### 1. Create Your Tracking Sheet
* Create a new Google Sheet and title it (e.g., *Job Tracker*).
* Set up your header row with the following columns:
  * `Col A`: Job Title
  * `Col B`: Company
  * `Col C`: Location Type
  * `Col D`: Country/Region
  * `Col E`: Date Posted
  * `Col F`: Application Link

### 2. Configure the Google Apps Script
* In your Google Sheet, click on **Extensions** > **Apps Script** or paste this in your browser -> https://script.google.com/home.
* Delete any placeholder code and paste the pipeline script into the editor.
* Replace `"REPLACE_WITH_SPREADSHEET_ID"` with your actual Google Sheet ID (found in your sheet's URL between `/d/` and `/edit`).
* Insert your RapidAPI key for JSearch into the `apiKey` variable (REPLACE_WITH_YOUR_JSEARCH_XRAPIDAPIKEY). See how to get the RapidAPI key for JSearch below;

```text
* Go to https://rapidapi.com/hub and sign in for free
* In the search bar, search for JSearch API and click on the first one, then subscribe to the Basic Plan
* Select 'Subscribe to Run' tab in the new interface and then run.
* Under the Request tab, click Headers, you will see 'x-API key' which is your RapidAPI key.
```


### 3. Set Up Daily Automation
* In the Apps Script sidebar, click the **Clock icon (Triggers)**.
* Click **+ Add Trigger**.
* Choose `fetchAndLogJobs` as the function to run.
* Set the event source to **Time-driven** and choose a **Day timer** interval.
* Click **Save**.

### 4. Setup for other job roles
* Edit the code section below of the App Script to the job role you are searching for

```text
// --- SOURCE 1: JSearch ---
  var apiKey = "REPLACE_WITH_YOUR_JSEARCH_XRAPIDAPIKEY";
  var queries = [
    "Data Analyst remote hybrid Nigeria",
    "Analytics Engineer remote",
    "Data Engineer entry level remote"
  ];
```


```text
  var isDataAnalyst = lowerTitle.includes("data analyst") || lowerTitle.includes("bi analyst") || lowerTitle.includes("business intelligence");
  var isAnalyticsEng = lowerTitle.includes("analytics engineer");
  var isDataEng = lowerTitle.includes("data engineer");
  var isDataSpecialist = lowerTitle.includes("data specialist");
  var isVisSpecialist = lowerTitle.includes("visualization") || lowerTitle.includes("tableau") || lowerTitle.includes("power bi");

  var isTargetRole = isDataAnalyst || isAnalyticsEng || isDataEng || isDataSpecialist || isVisSpecialist;
```


---

## License
This project is open-source and available under the [MIT License](LICENSE).
