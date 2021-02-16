import argparse
import csv
import pathlib
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import helpers

PROJECT_ROOT = pathlib.Path(__file__).parent.resolve()
DATA_ROOT = PROJECT_ROOT / 'data'


class EmailObject:
    """Email Object is the core information from the announcement.csv"""
    def __init__(self, **kwargs):

        for key, value in kwargs.items():

            if key == 'dbname':
                self._dbname = value

            if key == 'services':
                self._services = value

            if key == 'time':
                if not value:
                    self._time = datetime.min
                else:
                    self._time = helpers.cd_to_datetime(value)

            if key == 'approval':
                if value == 'Y':
                    self._approval = True
                else:
                    self._approval = False

            if key == 'receivers':
                if not value:
                    self._receivers = None
                else:
                    mylist: list = value.split(';')
                    self._receivers = mylist

            if key == 'cc':
                if value:
                    mylist = value.split(';')
                    self._cc = mylist
                else:
                    self._cc = None

            if key == 'task':
                self._task = value

    @property
    def receivers(self) -> list[str]:
        return self._receivers

    @property
    def cc(self) -> list[str]:
        return self._cc

    @property
    def database(self):
        return self._dbname

    @property
    def services(self) -> str:
        out = '<h3>Betroffene Services:</h3>'
        items = self._services.split(";")
        for item in items:
            out += item + "<br>"
        return out

    def __str__(self):
        return (f"{helpers.datetime_to_str(self._time)} / {self._task} on {self._dbname} - "
                f"Approval required: {str(self._approval)}")

    @property
    def time(self):
        return self._time


def load_csv(file):
    """Returns a list of EmailObject Objects"""

    infile = pathlib.Path(file)
    out = list()

    with open(infile, 'r') as _io:
        data = csv.DictReader(_io)
        for row in data:
            o_email = EmailObject(dbname=row['dbname'], services=row['services'], time=row['time'],
                                  approval=row['approval'], receivers=row['receiver'], cc=row['cc'],
                                  task=row['task']
                                  )
            out.append(o_email)
    return out


def send_mail(obj: EmailObject, subject="Announcement") -> None:

    from jinja2 import Environment, FileSystemLoader

    sender_email = "noone@example.com"
    message = MIMEMultipart("alternative")

    message["From"] = "notify@dbconcepts.at"
    message["Subject"] = "[" + subject + "] " + str(obj)
    message["To"] = ', '.join(obj.receivers)

    if obj.cc is not None:
        message["Cc"] = ', '.join(obj.cc)
        recipients = obj.receivers + obj.cc
    else:
        recipients = obj.receivers

    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)

    template = env.get_template("announcement.html")
    output = template.render()

    if subject == "Maintenance":
        text = (f"<br>Sehr geehrte Damen und Herren,<br>"
                f"Auf dem Datenbank System wird die Wartung jetzt durchgeführt. <br>"
                f"Die Datenbank <b>{obj.database}</b> wird in den Wartungsarbeiten geswitcht.<br>"
                f"Wir erwarten keine Unterbrechungen der Dienste! <br>"
                f"{obj.services}<br>"
                f"Ihr DBConcepts,<br>"
                f"Wir sind nur einen Anruf entfernt: +43 1 890 89 990")

    if subject == "Announcement":
        text = output

    if subject == "Finished":
        text = (f"<br>Sehr geehrte Damen und Herren,<br>"
                f"Auf dem Datenbank System <b>{obj.database}</b> wurde die Wartung durchgeführt. <br>"
                f"Bitte um Kontrolle der Dienste, bei Fragen und Problemen rufen Sie uns bitte an! <br><br>"
                f"Ihr DBConcepts,<br>"
                f"Wir sind nur einen Anruf entfernt: +43 1 890 89 990")

    if subject == "Problem":
        text = (f"<br>Sehr geehrte Damen und Herren,<br>"
                f"Auf dem Datenbank System <b>{obj.database}</b> haben wir derzeit ein unerwartetes Problem. <br>"
                f"Wir arbeiten daran mit Druck! <br><br>"
                f"Ihr DBConcepts,<br>"
                f"Wir sind nur einen Anruf entfernt: +43 1 890 89 990")

    if subject == "Reminder":
        text = (f"<br>Sehr geehrte Damen und Herren,<br>"
                f"Auf dem Datenbank System <b>{obj.database}</b> sollte bald eine Wartung durchgeführt werden. <br>"
                f"Wenn es ein System ist, dass eine Freigabe benötigt werden wir auf den Anruf warten. <br><br>"
                f"Ihr DBConcepts,<br>"
                f"Wir sind nur einen Anruf entfernt: +43 1 890 89 990")

    part1 = MIMEText(text, "html")
    message.attach(part1)

    with smtplib.SMTP("localhost") as server:
        server.send_message(message, from_addr=sender_email, to_addrs=recipients)
        print("mail sent")


def main():
    parser = argparse.ArgumentParser(description="Send Emails to customers")
    parser.add_argument('--file', default=(DATA_ROOT / 'announcement.csv'),
                        type=pathlib.Path, help="Path to file to be processed")
    parser.add_argument('--type', type=str, default="Announcement", help="Type of subject")
    parser.add_argument('--db', type=str, help="Database")
    args = parser.parse_args()

    if 'file' in args:
        data = load_csv(file=args.file)

    today = datetime.today()
    midnight = datetime.today()
    midnight = midnight.replace(hour=23, minute=59, second=59, microsecond=0)

    for email in data:
        # loop through the email database and check
        if args.db == email.database:
            if args.type == "Announcement":
                print(args.type, email)
                send_mail(email)
            else:
                print(args.type, email)
                send_mail(email, subject=args.type)

        if not args.db:
            if today < email.time < midnight:
                if args.type == "Announcement":
                    send_mail(email)
                    print(args.type, email)
                else:
                    send_mail(email, args.type)
                    print(args.type, email)


if __name__ == "__main__":
    main()
