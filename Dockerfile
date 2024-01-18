FROM python:3.8

ENV SMTP_DEBUG 0
ENV REFRESH_SECONDS 300
ENV SIGN_OF_LIFE_AFTER_REFRESHES 120

RUN pip install selenium requests pandas
WORKDIR /app
COPY check_grades.py .
ENTRYPOINT ["python", "check_grades.py"]
