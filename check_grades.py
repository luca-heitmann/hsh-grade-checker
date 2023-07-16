import requests
from lxml import html
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

def getGrades(user, passwd):
    with requests.Session() as s:
        res = s.post('https://icms.hs-hannover.de/qisserver/rds?state=user&type=1&category=auth.login&startpage=portal.vm',
                     headers={'Content-Type': 'application/x-www-form-urlencoded'},
                     data=f"asdf={user}&fdsa={passwd}%21&submit=%C2%A0Ok%C2%A0",
                     allow_redirects=False)

        sessionIdCookie = res.headers.get("Set-Cookie").split(";")[0]
        s.headers.update({'Cookie': sessionIdCookie})

        if 'Anmeldung fehlgeschlagen' in res.text:
            raise Exception("Anmeldung fehlgeschlagen")

        res = s.get("https://icms.hs-hannover.de/qisserver/rds?state=change&type=1&moduleParameter=studyPOSMenu&nextdir=change&next=menu.vm&subdir=applications&xml=menu&purge=y&navigationPosition=functions%2CstudyPOSMenu&breadcrumb=studyPOSMenu&topitem=functions&subitem=studyPOSMenu")

        tree = html.fromstring(res.content)
        notenspiegelUrl = tree.xpath('//a[text() = "Notenspiegel"]/@href')[0]

        res = s.get(notenspiegelUrl)
        tree = html.fromstring(res.content)
        leistungenUrl = tree.xpath('//a[@title = "Leistungen für Abschluss 84 Bachelor anzeigen"]/@href')[0]

        res = s.get(leistungenUrl)
        tree = html.fromstring(res.content)

        noten = pd.read_html(res.content, decimal=",", thousands=".", header=1)[1]
        noten = noten.dropna(subset=['Prüfungsdatum'])
        noten['Prüfungsdatum'] = pd.to_datetime(noten['Prüfungsdatum'], format = '%d%m%Y')
        noten = noten.astype({'Prüfungsnr.': 'int64'})
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
