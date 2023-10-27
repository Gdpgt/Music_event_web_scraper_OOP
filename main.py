import requests
import selectorlib
import smtplib, ssl
import os
import time
import sqlite3


URL = "http://programmer100.pythonanywhere.com/tours/"


class Event:
    def scrape(self, url):
        """Scrapes the page source from the URL"""
        response = requests.get(url)
        source = response.text
        return source

    def extract(self, source):
        """Extracts the value from the page source, thanks to the ID I wrote
        in extract.yaml, and its key I created"""
        extractor = selectorlib.Extractor.from_yaml_file("extract.yaml")
        value = extractor.extract(source)["tours"]
        return value


class Email:
    def send(self, message):
        host = "smtp.gmail.com"
        port = 465

        username = os.getenv('MY_EMAIL_ADDRESS')
        password = os.getenv('PASSWORD_Company')

        receiver = os.getenv('MY_EMAIL_ADDRESS')
        my_context = ssl.create_default_context()

        with smtplib.SMTP_SSL(host, port, context=my_context) as server:
            server.login(username, password)
            server.sendmail(username, receiver, message)
        print("Email was sent!")


class Database:
    def __init__(self, database_path):
        self.connection = sqlite3.connect(database_path)

    def store(self, extracted):
        # Transforms the str "x, y, z" into the list [x,y,z]
        # because the input data is a str that looks like "band, city, date"
        # : "Lions of the IDE, Clone City, 6.5.2088"
        row = [item.strip() for item in extracted.split(',')]
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO events VALUES(?,?,?)", row)
        # This is obligatory to save permanently changes made to the DB
        self.connection.commit()

    def query(self, extracted):
        row = [item.strip() for item in extracted.split(',')]
        band, city, date = row
        cursor = self.connection.cursor()
        # Makes a query to check if what's been scraped is already in the DB
        cursor.execute("SELECT * FROM events WHERE band=? AND city=? "
                       "AND date=?", (band, city, date))
        rows = cursor.fetchall()
        print(rows)
        return rows


if __name__ == "__main__":
    while True:
        event = Event()
        scraped = event.scrape(URL)
        extracted = event.extract(scraped)
        print(extracted)

        if extracted != "No upcoming tours":
            database = Database(database_path='data.db')
            row = database.query(extracted)
            if not row:
                database.store(extracted)
                email = Email()
                email.send(message=f"""Subject: New tour !
{extracted}
""")
        time.sleep(3)
