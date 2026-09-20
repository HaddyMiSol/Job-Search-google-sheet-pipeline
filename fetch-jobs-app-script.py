function fetchAndLogJobs() {
  var spreadsheet = SpreadsheetApp.openById("REPLACE_WITH_SPREADSHEET_ID");
  var sheet = spreadsheet.getActiveSheet();

  var existingData = sheet.getDataRange().getValues();
  var existingLinks = {};
  for (var i = 1; i < existingData.length; i++) {
    existingLinks[existingData[i][5]] = true; // Column F (Application Link)
  }

  var addedCount = 0;
  var oneMonthAgo = new Date();
  oneMonthAgo.setMonth(oneMonthAgo.getMonth() - 1); // 1-month threshold

  // --- SOURCE 1: JSearch ---
  var apiKey = "REPLACE_WITH_YOUR_JSEARCH_XRAPIDKEY";
  var queries = [
    "Data Analyst remote hybrid Nigeria",
    "Analytics Engineer remote",
    "Data Engineer entry level remote"
  ];

  var headers = {
    "X-RapidAPI-Key": apiKey,
    "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
  };

  queries.forEach(function(query) {
    var url = "https://jsearch.p.rapidapi.com/search-v2?query=" + encodeURIComponent(query) + "&num_pages=1&date_posted=month";
    try {
      var options = { method: "get", headers: headers, muteHttpExceptions: true };
      var response = UrlFetchApp.fetch(url, options);

      Logger.log("JSearch Response Code for '" + query + "': " + response.getResponseCode());

      if (response.getResponseCode() === 200) {
        var data = JSON.parse(response.getContentText());

        if (data.data && Array.isArray(data.data.jobs)) {
          Logger.log("JSearch fetched " + data.data.jobs.length + " listings for query: " + query);

          data.data.jobs.forEach(function(job) {
            // Strict property existence check before reading properties
            if (
              !job
              || typeof job !== "object"
              || !("job_title" in job)
              || !("employer_name" in job)
              || (!("job_apply_link" in job) && !("job_google_link" in job))
            ) {
              Logger.log("Skipped invalid or incomplete JSearch job entry");
              return;
            }

            var jobTitle = job.job_title || "";
            var company = job.employer_name || "";
            var jobUrl = job.job_apply_link || job.job_google_link || "";
            var location = job.job_location || job.job_country || "Anywhere";
            var isRemote = job.job_is_remote ? "Remote" : "Hybrid";
            var postedDateStr = job.job_posted_at_datetime_utc || "";
            var postedDate = postedDateStr ? new Date(postedDateStr) : new Date();

            if (postedDate >= oneMonthAgo) {
              if (processAndValidateAndAdd(jobTitle, company, jobUrl, location, isRemote, postedDate, existingLinks, sheet)) {
                addedCount++;
              }
            }
          });
        } else {
          Logger.log("JSearch response missing or invalid jobs array for query: " + query);
        }
      } else {
        Logger.log("JSearch Error Body: " + response.getContentText());
      }
      Utilities.sleep(2000);
    } catch (e) {
      Logger.log("JSearch Exception: " + e.toString());
    }
  });

  // --- SOURCE 2: Arbeitnow API ---
  try {
    var response2 = UrlFetchApp.fetch("https://www.arbeitnow.com/api/job-board-api", { muteHttpExceptions: true });
    var data2 = JSON.parse(response2.getContentText());
    if (data2.jobs && Array.isArray(data2.jobs)) {
      data2.jobs.forEach(function(job) {
        // Strict property existence check
        if (
          !job
          || typeof job !== "object"
          || !("title" in job)
          || !("company_name" in job)
          || !("url" in job)
        ) {
          Logger.log("Skipped invalid or incomplete Arbeitnow job entry");
          return;
        }

        var jobTitle = job.title || "";
        var company = job.company_name || "";
        var jobUrl = job.url || "";
        var location = job.location || "";
        var isRemote = job.remote ? "Remote" : "Hybrid/Full-time";
        var postedDate = job.created_at ? new Date(job.created_at * 1000) : new Date();

        if (postedDate >= oneMonthAgo) {
          if (processAndValidateAndAdd(jobTitle, company, jobUrl, location, isRemote, postedDate, existingLinks, sheet)) {
            addedCount++;
          }
        }
      });
    }
  } catch (e) {
    Logger.log("Arbeitnow error: " + e.toString());
  }

  Logger.log("Execution complete. Total new verified jobs added: " + addedCount);
}

function processAndValidateAndAdd(jobTitle, company, jobUrl, location, isRemote, postedDate, existingLinks, sheet) {
  if (!jobUrl) {
    Logger.log("Rejected: Missing job URL for \"" + jobTitle + "\" at \"" + company + "\"");
    return false;
  }
  if (existingLinks[jobUrl]) {
    Logger.log("Rejected: Duplicate job URL: " + jobUrl);
    return false;
  }

  var lowerTitle = jobTitle.toLowerCase();
  var lowerLoc = (location || "").toLowerCase();

  var isDataAnalyst = lowerTitle.includes("data analyst") || lowerTitle.includes("bi analyst") || lowerTitle.includes("business intelligence");
  var isAnalyticsEng = lowerTitle.includes("analytics engineer");
  var isDataEng = lowerTitle.includes("data engineer");
  var isDataSpecialist = lowerTitle.includes("data specialist");
  var isVisSpecialist = lowerTitle.includes("visualization") || lowerTitle.includes("tableau") || lowerTitle.includes("power bi");

  var isTargetRole = isDataAnalyst || isAnalyticsEng || isDataEng || isDataSpecialist || isVisSpecialist;
  if (!isTargetRole) {
    Logger.log("Rejected: Role does not match target: " + jobTitle);
    return false;
  }

  var isExcluded = lowerTitle.includes("sales") ||
                   lowerTitle.includes("finance") ||
                   lowerTitle.includes("manager") ||
                   lowerTitle.includes("director") ||
                   lowerTitle.includes("m&a") ||
                   lowerTitle.includes("controller") ||
                   lowerTitle.includes("full-stack") ||
                   lowerTitle.includes("devops") ||
                   lowerTitle.includes("qa engineer") ||
                   lowerTitle.includes("frontend") ||
                   lowerTitle.includes("backend");
  if (isExcluded) {
    Logger.log("Rejected: Excluded role keyword in title: " + jobTitle);
    return false;
  }

  var isJunior = lowerTitle.includes("junior") || lowerTitle.includes("entry") || lowerTitle.includes("intern") || lowerTitle.includes("associate");
  if (isJunior && !isDataEng) {
    Logger.log("Rejected: Junior level role but not Data Engineer: " + jobTitle);
    return false;
  }

  var isNigeria = lowerLoc.includes("nigeria") || lowerLoc.includes("lagos") || lowerLoc.includes("abuja");
  var isRemoteFlag = String(isRemote).toLowerCase().includes("remote");
  var hasVisaSponsorship = lowerTitle.includes("visa") || lowerTitle.includes("sponsorship") || lowerLoc.includes("worldwide") || lowerLoc.includes("global") || lowerLoc.includes("anywhere");
  var isEmptyOrAnywhere = (lowerLoc === "" || lowerLoc === "anywhere");

  var isValidLocation = isNigeria || isRemoteFlag || hasVisaSponsorship || isEmptyOrAnywhere;

  if (!isValidLocation) {
    Logger.log("Rejected: Location not valid: " + location + " | Remote: " + isRemote);
    return false;
  }

  var dateString = postedDate.toISOString().split('T')[0];
  sheet.appendRow([
    jobTitle,
    company,
    isRemote,
    location || "Global/Remote",
    dateString,
    jobUrl
  ]);

  existingLinks[jobUrl] = true;
  Logger.log("SUCCESS ADDED: " + jobTitle);
  return true;
}
