import datetime
from . import helpers as helpme
import pathlib
import csv


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
                    self._start_time = helpme.cd_to_datetime(value)

            if key == 'endtime':
                if not value:
                    self._end_time = datetime.min
                else:
                    self._end_time = helpme.cd_to_datetime(value)

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
    def services(self):
        items = self._services.split(';')
        return items

    def __str__(self):
        return (f" Affected Systems: {list_to_string(self._system)} - "
                f"Start Time: {helpme.datetime_to_str(self._start_time)}, "
                f"Approval required: {str(self._approval)}, "
                f"Downtime: {self._downtime}")

    def print(self):
        return (f"{self._system}, {self._contact}")

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
