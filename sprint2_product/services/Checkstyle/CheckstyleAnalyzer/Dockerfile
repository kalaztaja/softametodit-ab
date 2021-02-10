FROM openjdk:slim

ADD https://github.com/checkstyle/checkstyle/releases/download/checkstyle-8.30/checkstyle-8.30-all.jar /app/checkstyle.jar
COPY ./sun_checks.xml /app/sun_checks.xml
CMD java -jar /app/checkstyle.jar -c /app/sun_checks.xml /usr/src/ -o /usr/out/checkstyle.xml -f xml
