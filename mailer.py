import argparse
import csv
import pathlib
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import helpers
from enum import Enum
from jinja2 import Environment, FileSystemLoader

PROJECT_ROOT = pathlib.Path(__file__).parent.resolve()
DATA_ROOT = PROJECT_ROOT / 'data'


class EmailObject:
    """Email Object is the core information from the announcement.csv"""

    def __init__(self, **kwargs):

        for key, value in kwargs.items():

            if key == 'system':
                system_list = value.split(';')
                self._system = system_list

            if key == 'services':
                self._services = value

            if key == 'starttime':
                if not value:
                    self._start_time = datetime.min
                else:
                    self._start_time = helpers.cd_to_datetime(value)

            if key == 'endtime':
                if not value:
                    self._end_time = datetime.min
                else:
                    self._end_time = helpers.cd_to_datetime(value)

            if key == 'downtime':
                if value == 'Y':
                    self._downtime = 'YES'
                else:
                    self._downtime = 'NO'

            if key == 'approval':
                if value == 'Y':
                    self._approval = 'YES'
                else:
                    self._approval = 'NO'

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

            if key == 'contact':
                self._contact = value

            if key == 'contact_no':
                self._contact_no = value

    @property
    def receivers(self) -> list[str]:
        return self._receivers

    @property
    def cc(self) -> list[str]:
        return self._cc

    @property
    def system(self):
        return self._system

    @property
    def services(self) -> str:
        out = '<h3>Affected Services:</h3>'
        items = self._services.split(";")
        for item in items:
            out += item + "<br>"
        return out

    def __str__(self):
        return (f" Affected Systems: {list_to_string(self._system)} - "
                f"Start Time: {helpers.datetime_to_str(self._start_time)}, "
                f"Approval required: {str(self._approval)}, "
                f"Downtime: {self._downtime}")

    @property
    def start_time(self):
        return self._start_time

    @property
    def end_time(self):
        return self._end_time


def load_csv(file):
    """Returns a list of EmailObject Objects"""

    infile = pathlib.Path(file)
    out = list()

    with open(infile, 'r') as _io:
        data = csv.DictReader(_io)
        for row in data:
            o_email = EmailObject(system=row['system'],
                                  services=row['services'],
                                  starttime=row['starttime'],
                                  endtime=row['endtime'],
                                  downtime=row['downtime'],
                                  approval=row['approval'],
                                  receivers=row['receiver'],
                                  cc=row['cc'],
                                  task=row['task'],
                                  contact=row['contact'],
                                  contact_no=row['contact_no']
                                  )
            out.append(o_email)
    return out


def list_to_string(i_list):
    return ' '.join([str(elem) for elem in i_list])


def send_mail(obj: EmailObject, subject="Announcement") -> None:
    sender_email = "notify@dbconcepts.at"
    message = MIMEMultipart("alternative")

    message["From"] = "notify@dbconcepts.at"
    message["To"] = ', '.join(obj.receivers)

    if obj.cc is None:
        recipients = obj.receivers
    else:
        message["Cc"] = ', '.join(obj.cc)
        recipients = obj.receivers + obj.cc

    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)

    if subject == "Maintenance":
        template = env.get_template("maintenance.html")
        text = template.render(systems=obj.system,
                                 downtime=obj._downtime,
                                 starttime=obj.start_time,
                                 endtime=obj.end_time,
                                 task=obj._task,
                                 contact=obj._contact,
                                 contact_no=obj._contact_no,
                                 services=obj.services)

        message["Subject"] = f"Announcement: {subject} started on " \
                             f"{list_to_string(obj.system)} " \
                             f"Downtime: {obj._downtime} "

    elif subject == "Announcement":
        template = env.get_template("announcement.html")
        text = template.render(systems=obj.system,
                                 downtime=obj._downtime,
                                 starttime=obj.start_time,
                                 endtime=obj.end_time,
                                 task=obj._task,
                                 contact=obj._contact,
                                 contact_no=obj._contact_no,
                                 services=obj.services)

        message["Subject"] = f"{subject}: " \
                             f"Upcoming maintenance on systems: " \
                             f"{list_to_string(obj.system)}, " \
                             f"Approval required: {obj._approval}, " \
                             f"Downtime: {obj._downtime}, " \
                             f"Start Time: {obj.start_time} "

    elif subject == "Completed":
        template = env.get_template("completed.html")
        text = template.render(systems=obj.system,
                                 downtime=obj._downtime,
                                 starttime=obj.start_time,
                                 endtime=obj.end_time,
                                 task=obj._task,
                                 contact=obj._contact,
                                 contact_no=obj._contact_no,
                                 services=obj.services)

        message["Subject"] = f"Announcement: Maintenance " \
                             f"{subject.lower()} on " \
                             f"systems: " \
                             f"{list_to_string(obj.system)} "

    elif subject == "Problem":
        template = env.get_template("problem.html")
        text = template.render(systems=obj.system,
                                 downtime=obj._downtime,
                                 starttime=obj.start_time,
                                 endtime=obj.end_time,
                                 task=obj._task,
                                 contact=obj._contact,
                                 contact_no=obj._contact_no,
                                 services=obj.services)

        message["Subject"] = f"Announcement: {subject} during " \
                             f"maintenance on systems: " \
                         f"{list_to_string(obj.system)} occured!"

    elif subject == "Reminder":
        template = env.get_template("announcement.html")
        text = template.render(systems=obj.system,
                                 downtime=obj._downtime,
                                 starttime=obj.start_time,
                                 endtime=obj.end_time,
                                 task=obj._task,
                                 contact=obj._contact,
                                 contact_no=obj._contact_no,
                                 services=obj.services)

        message["Subject"] = f"{subject}: " \
                             f"Upcoming maintenance on systems: " \
                             f"{list_to_string(obj.system)}, " \
                             f"Approval required: {obj._approval}, " \
                             f"Downtime: {obj._downtime}, " \
                             f"Start Time: {obj.start_time}, " \
                             f"Planned End Time: {obj.end_time}"

    part1 = MIMEText(text, "html")
    message.attach(part1)

    with smtplib.SMTP("localhost") as server:
        try:
            server.send_message(message, from_addr=sender_email,
                                to_addrs=recipients)
        except smtplib.SMTPException as err:
            print("Error during send message happened")


def f_argparser() -> object:
    parser = argparse.ArgumentParser(description="Send Emails to customers")
    parser.add_argument('--file', default=(DATA_ROOT / 'announcement.csv'),
                        type=pathlib.Path, help="Path to file to be processed")
    parser.add_argument('--type', type=str, default="Announcement",
                        help="Type of subject")
    parser.add_argument('--system', type=str, help="System")
    args = parser.parse_args()

    return args


def main():
    args = f_argparser()
    data = load_csv(file=args.file)

    today = datetime.today().replace(hour=0,
                                     minute=0,
                                     second=1,
                                     microsecond=0)

    midnight = datetime.today().replace(hour=23,
                                        minute=59,
                                        second=59,
                                        microsecond=0)

    for email in data:
        if today < email.start_time < midnight:
            if args.system == list_to_string(email.system):
                send_mail(email, args.type)
                print("mail sent")
            else:
                send_mail(email)


if __name__ == "__main__":
    main()
