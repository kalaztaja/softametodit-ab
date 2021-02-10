FROM rawdee/pmd:latest
ENTRYPOINT pmd -d ../usr/src/ -f csv -R rulesets/java/quickstart.xml -auxclasspath commons-collections.jar:derby.jar > ../usr/out/pmdReport.csv