import argparse
import pathlib
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader
from helpers import EmailObject, helpers

PROJECT_ROOT = pathlib.Path(__file__).parent.resolve()
DATA_ROOT = PROJECT_ROOT / 'data'


def send_mail(obj: EmailObject, subject="Announcement") -> None:
    sender_email = "notify@dbconcepts.at"
    message = MIMEMultipart("alternative")

    message["From"] = sender_email
    message["To"] = ', '.join(obj.receivers)

    if obj.cc is None:
        recipients = obj.receivers
    else:
        message["Cc"] = ', '.join(obj.cc)
        recipients = obj.receivers + obj.cc

    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)

    if subject == "Maintenance":
        template = env.get_template("maintenance.jinja")
        text = template.render(systems=obj.system,
                               downtime=obj._downtime,
                               starttime=obj.start_time,
                               endtime=obj.end_time,
                               task=obj._task,
                               contact=obj._contact,
                               contact_no=obj._contact_no,
                               services=obj.services)

        message["Subject"] = f"Announcement: {subject} started on " \
                             f"{EmailObject.list_to_string(obj.system)} " \
                             f"Downtime: {obj._downtime} "

    elif subject == "Announcement":
        template = env.get_template("announcement.jinja")
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
                             f"{EmailObject.list_to_string(obj.system)}, " \
                             f"Approval required: {obj._approval}, " \
                             f"Downtime: {obj._downtime}, " \
                             f"Start Time: {obj.start_time} "

    elif subject == "Completed":
        template = env.get_template("completed.jinja")
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
                             f"{EmailObject.list_to_string(obj.system)} "

    elif subject == "Problem":
        template = env.get_template("problem.jinja")
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
                         f"{EmailObject.list_to_string(obj.system)} occured!"

    elif subject == "Reminder":
        template = env.get_template("announcement.jinja")
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
                             f"{EmailObject.list_to_string(obj.system)}, " \
                             f"Approval required: {obj._approval}, " \
                             f"Downtime: {obj._downtime}, " \
                             f"Start Time: {obj.start_time}, " \
                             f"Planned End Time: {obj.end_time}"

    part1 = MIMEText(text, "html")
    message.attach(part1)

    with smtplib.SMTP(host="localhost",port=25, timeout=5) as server:
        try:
            server.send_message(message, from_addr=sender_email,
                                to_addrs=recipients)
            print(f"Message type: {subject} for {obj.system} was sent")
        except smtplib.SMTPException as err:
            print("Error during send message happened")


def f_argparser():
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
    data = EmailObject.load_csv(file=args.file)

    today = datetime.today().replace(hour=0,
                                     minute=0,
                                     second=1,
                                     microsecond=0)

    midnight = datetime.today().replace(hour=23,
                                        minute=59,
                                        second=59,
                                        microsecond=0)

    for email in data:
        listToStr = ' '.join(map(str, email.system))
        if listToStr == args.system:
            send_mail(email, args.type)


if __name__ == "__main__":
    main()
