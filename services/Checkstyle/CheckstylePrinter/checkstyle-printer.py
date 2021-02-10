import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError
import logging
import csv
import time


CHECKSTYLE_XML = "/usr/in/checkstyle.xml"
CHECKSTYLE_CSV = "/usr/out/checkstyle.csv"

ANALYZER_POLLING_TIMEOUT_S = 600 # 10 min
ANALYZER_POLLING_WAIT_S = 5

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

logger = logging.getLogger("CheckstyleAnalyzer")
# For some reason info level is not shown, so everything is at least in
# warning. Doesn't matter though since only the text is logged
logger.setLevel(logging.INFO)

def checkstyle_to_csv_matrix():
    csv_matrix = []
    csv_matrix.append(HEADER_ROW)

    # Checkstyle has latency in writing file contents, so we need to do polling here
    max_polls = ANALYZER_POLLING_TIMEOUT_S // ANALYZER_POLLING_WAIT_S
    for i in range(max_polls):
        try:
            root = ET.parse(CHECKSTYLE_XML).getroot()
        except ParseError:
            logger.warning(f"Could not parse {CHECKSTYLE_XML} yet, trying again.")
            time.sleep(ANALYZER_POLLING_WAIT_S)

    for source in root:
        component = source.attrib["name"]
        for issue in source:
            attrib = issue.attrib
            csv_matrix.append(["","","","","",component, map_severity_to_sonar(attrib["severity"]), attrib["line"], "", "", "", attrib["message"], "", "", ""])
    return csv_matrix

def map_severity_to_sonar(severity):
    if severity == "error":
        return "MAJOR"
    else:
        # In case of warnigns and infos
        return "MINOR"

def write_csv_matrix(csv_matrix):
    logger.warning("Writing checkstyle results to CSV")
    with open(CHECKSTYLE_CSV, 'w+') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerows(csv_matrix)
    logger.warning(f"Analysis file written to {CHECKSTYLE_CSV}")

def main():
    csv_matrix = checkstyle_to_csv_matrix()
    write_csv_matrix(csv_matrix)

if __name__ == "__main__":
    main()