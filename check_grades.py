from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import os.path
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time

username = os.getenv('ICMS_USERNAME')
password = os.getenv('ICMS_PASSWORD')
smtp_server = os.getenv('SMTP_SERVER')
port = int(os.getenv('SMTP_PORT'))
from_address = os.getenv('SMTP_FROM')
to_address = os.getenv('SMTP_TO')
smtp_username = os.getenv('SMTP_USERNAME')
smtp_password = os.getenv('SMTP_PASSWORD')
smtp_debug = int(os.getenv('SMTP_DEBUG'))
refresh_seconds = int(os.getenv('REFRESH_SECONDS'))
sign_of_life_after_refreshes = int(os.getenv('SIGN_OF_LIFE_AFTER_REFRESHES'))
prev_noten_name = "noten.csv"
selenium_remote = os.getenv('SELENIUM_REMOTE')

def getGrades(user, passwd):
    print("Trying to scrape grades")

    with webdriver.Remote(options = webdriver.ChromeOptions(), command_executor=selenium_remote) as driver: 
        driver.implicitly_wait(30)
        driver.get("https://campusmanagement.hs-hannover.de/qisserver/pages/cs/sys/portal/hisinoneStartPage.faces")
        # Login
        driver.find_element(By.ID, "asdf").send_keys(user)
        driver.find_element(By.ID, "fdsa").send_keys(passwd)
        driver.find_element(By.ID, "loginForm:login").click()
        # Navigate to ICMS
        driver.find_element(By.CLASS_NAME, "tile_one").click()
        iframe = driver.find_element(By.TAG_NAME, "iframe")
        driver.switch_to.frame(iframe)
        # Navigate to grade overview
        driver.find_element(By.XPATH, "//a[text() = 'Prüfungen']").click()
        driver.find_element(By.XPATH, "//a[text() = 'Notenspiegel']").click()
        driver.find_element(By.XPATH, "//a[@title = 'Leistungen für Abschluss 84 Bachelor anzeigen']").click()
        # Parse grade overview
        noten = pd.read_html(driver.page_source, decimal=",", thousands=".", header=1)[1]
        noten['Prüfungsdatum'] = pd.to_datetime(noten['Prüfungsdatum'], format = '%d%m%Y')
        noten.to_csv("noten.csv")
        print("Found grades: ", noten)
        return noten

def checkChanges(notenNeu):
    if os.path.isfile(prev_noten_name):
        return not pd.read_csv(prev_noten_name, index_col=0, parse_dates=['Prüfungsdatum']).equals(notenNeu)
    else:
        return True

def storeGrades(notenNeu):
    notenNeu.to_csv(prev_noten_name)

def sendMail(subject, payload):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_address
    msg['To'] = to_address
    msg.add_header('Content-Type','text/html')
    msg.attach(MIMEText(payload, 'html'))

    try:
        server = smtplib.SMTP(smtp_server, port)
        server.set_debuglevel(smtp_debug)
        server.starttls(context=ssl.create_default_context())
        server.connect(smtp_server, port)
        server.login(smtp_username, smtp_password)
        server.sendmail(msg['From'], [msg['To']], msg.as_string())
    except Exception as e:
        print(e)
    finally:
        server.quit()

counter = 0

while (True):
    noten = getGrades(username, password)
    
    if counter == 0:
        print("Sende sign of life")
        sendMail("Notentool Sign Of Life", noten.to_html())
        counter = sign_of_life_after_refreshes

    if checkChanges(noten):
        print(f"Neue Note gefunden")
        sendMail("Neue Note gefunden!", noten.to_html())
    else:
        print("Keine neuen Noten")

    storeGrades(noten)
    counter -= 1
    time.sleep(refresh_seconds)
