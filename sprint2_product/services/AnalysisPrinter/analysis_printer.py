import urllib.request
import json
import csv
import time
import logging
import os.path

# Script for fetching analysis results from SonarQube and priting them as
# csv-file.

ISSUES_URL = "http://sonar-server:9000/api/issues/search"
ANALYSIS_PROGRESS_URL = "http://sonar-server:9000/api/ce/task?id="
HEADER_ROW = ["projectName",
            "creationDate",
            "creationCommitHash",
            "type",
            "squid",
            "component",
            "severity",
            "startLine",
            "endLine",
            "resolution",
            "status",
            "message",
            "effort",
            "debt",
            "author"]
TASK_ID_KEY = "ceTaskId"

SCANNER_POLLING_TIMEOUT_S = 600 # 10 min
SCANNER_POLLING_WAIT_S = 5

FILE_REPORT = "/usr/src/.scannerwork/report-task.txt"
FILE_ANALYSIS = "/usr/out/analysis.csv"


logger = logging.getLogger("Analyzer")
# For some reason info level is not shown, so everything is at least in
# warning. Doesn't matter though since only the text is logged
logger.setLevel(logging.INFO)


def issues_json_to_csv_matrix(issues_json):
    issues_csv_matrix = [
        HEADER_ROW
    ]
    for issue in issues_json["issues"]:
        issues_csv_row = []
        issues_csv_row.append(if_field_exists(issue, "project"))
        issues_csv_row.append(if_field_exists(issue, "creationDate"))
        issues_csv_row.append(if_field_exists(issue, "hash"))
        issues_csv_row.append(if_field_exists(issue, "type"))
        issues_csv_row.append(if_field_exists(issue, "rule"))
        issues_csv_row.append(if_field_exists(issue, "component"))
        issues_csv_row.append(if_field_exists(issue, "severity"))
        if "textRange" in issue:
            issues_csv_row.append(if_field_exists(issue["textRange"], "startLine"))
            issues_csv_row.append(if_field_exists(issue["textRange"], "endLine"))
        issues_csv_row.append(if_field_exists(issue, "resolution"))
        issues_csv_row.append(if_field_exists(issue, "status"))
        issues_csv_row.append(if_field_exists(issue, "message"))
        issues_csv_row.append(if_field_exists(issue, "effort"))
        issues_csv_row.append(if_field_exists(issue, "debt"))
        issues_csv_row.append(if_field_exists(issue, "author"))
        issues_csv_matrix.append(issues_csv_row)
    return issues_csv_matrix


def if_field_exists(json, field):
    """ Return empty string if filed is not in json
    """
    try:
        return json[field]
    except KeyError:
        return ""


def get_analysis_id():
    config_file = open(FILE_REPORT)

    for line in config_file:
        key, value = line.split("=",1)
        if key == TASK_ID_KEY:
            return value


def analysis_in_progress(url):
    progress_json = get_json(url)
    return progress_json["task"]["status"] == "IN_PROGRESS"


def get_json(url):
    return json.load(urllib.request.urlopen(url))


def write_csv_matrix(csv_matrix):
    logger.warning("Writing analysis results to CSV")
    with open(FILE_ANALYSIS, 'w+') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerows(csv_matrix)
    logger.warning(f"Analysis file written to {FILE_ANALYSIS}")


def wait_scanner():
    # Calculate number of polls before timeout
    max_polls = SCANNER_POLLING_TIMEOUT_S // SCANNER_POLLING_WAIT_S
    logger.warning("Polling {} times with {} wait time".format(
        max_polls, SCANNER_POLLING_WAIT_S
    ))

    for _ in range(max_polls):
        if os.path.exists(FILE_REPORT):
            return get_analysis_id()
        logger.warning("No report file found, waiting before new poll")
        time.sleep(SCANNER_POLLING_WAIT_S)

    # Timeout reached if we end up here
    logger.error("Timeout reached while waiting for sonar-scanner")
    raise RuntimeError("Timeout reached")


def wait_sonar_server_analysis(analysis_id):
    progress_url = ANALYSIS_PROGRESS_URL + analysis_id
    logger.warning(f"Waiting task to be complited by polling {progress_url}")
    while analysis_in_progress(progress_url):
        time.sleep(5)


def main():
    # Wait for scanning and analyis to finish
    analysis_id = wait_scanner()
    wait_sonar_server_analysis(analysis_id)

    # Analysis is finished: fetch results and print csv.
    issues_json = get_json(ISSUES_URL)
    issues_csv_matrix = issues_json_to_csv_matrix(issues_json)
    write_csv_matrix(issues_csv_matrix)


if __name__ == "__main__":
    main()
