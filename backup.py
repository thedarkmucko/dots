import os
import argparse
import subprocess
import time
import smtplib
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from configparser import SafeConfigParser
from typing import NewType

currentdatetime = time.strftime("%Y-%m-%d_%H%M%S")
currentdate = time.strftime("%Y%m%d")

gmail_user = "dbgenie001@gmail.com"
gmail_password = "oracleoracle"

recipients = ['peter.sorger@db-genie.com']

config_path = Path('../config/')
logfile_path = Path('../log/')

def typeConvert(input):
    if input == 0:
        return "inc0"
    elif input == 1:
        return "inc1"
    elif input == 2:
        return "arch"

def parse_config(sid): 
    config_file_name = 'rman-' + sid + '.conf' 
    conf_file = config_path / config_file_name
    
    if not conf_file.exists():
        print("config file for " + sid + "does not exist! Exiting...")
        exit(1)
    
    config = SafeConfigParser()
    config.read(conf_file)
    oracle_sid = config.get('db', 'sid')
    backup_base_path = config.get('db', 'backup_base')
    oracle_home_path = config.get('db', 'oracle_home')

    my_dict = {}
    my_dict["sid"] = oracle_sid
    my_dict["backup_path"] = backup_base_path
    my_dict["oh"] = oracle_home_path
    return my_dict

def send_mail(hostname, sid, subject, text):
    sender_email = "noone@example.com"
    message = MIMEMultipart("alternative")
    message["Subject"] = hostname + ": " + subject + ' - ' + sid
    message["From"] = sender_email
    message["To"] = ", ".join(recipients)

    part1 = MIMEText(text, "html")
    message.attach(part1)
    # send your email
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(gmail_user, gmail_password)
        server.sendmail(sender_email, recipients, message.as_string())

def make_directory(sid, path):
    my_path = path + "/" + sid + "/" + currentdate
    full_path = Path(my_path)
    Path.mkdir(full_path,parents=True,exist_ok=True)
    return str(full_path)

def backup_db(sid, type):
    config = parse_config(sid)
    newType = typeConvert(type)

    logfile = logfile_path / 'backup_{0}_{1}_{2}.log'.format(sid, currentdatetime, newType)    
    
    out_dir = make_directory(sid, config["backup_path"])

    cmdfile = generate_cmdfile(
        config["sid"], type, str(out_dir) + '/%d_%I_%U')
    cmd_file = Path(cmdfile)
    
    rmanCMD = config["oh"] + '/bin/rman target / cmdfile=\'' + \
        str(cmd_file.absolute()) + '\' log=\'' + str(logfile.absolute()) +'\''
        
    os.putenv('NLS_DATE_FORMAT', 'DD-MM-YYYY HH24:MI:SS')
    os.putenv('ORACLE_SID', config["sid"])
    os.putenv('ORACLE_HOME', config["oh"])
    os.putenv('LD_LIBRARY_PATH', config["oh"] + '/lib')

    try:
        output = subprocess.check_output(rmanCMD, shell=True)
    except:
        check = check_for_errors(str(logfile))
        if check:
            import socket
            hostname = socket.gethostname()
            out_text = ("<h1>Backup had errors</h1>"
                        "<p>Please check logfile {0}</p>").format(logfile)
            send_mail(hostname, sid, "ERROR", out_text)

def check_for_errors(file):
    with open(file) as f:
        if 'RMAN-' in f.read():
            return True

def write_config(file, rman_command):
    f = open(file, "w")
    f.write(rman_command)
    f.close()

def generate_cmdfile(sid, type, backup_string):
    switch = {
        0: "Incremental Backup Level 0",
        1: "Incremental Backup Level 1",
        2: "Archivelog Backup"
    }
    rman_string = None
    if type in switch:
        if type == 0:
            # generate rman config based on these information
            rman_string = ("run { \n"
                           "allocate channel ch1 device type disk format=\"" + backup_string + "\" ; \n"
                           "backup check logical incremental level 0 database ; \n"
                           "delete obsolete; \n"
                           "} "
                           )
        if type == 1:
            rman_string = ("run { \n"
                           "allocate channel ch1 device type disk format=\"" + backup_string + "\" ; \n"
                           "backup check logical incremental level 1 database ; \n" 
                           "} "
                           )
        if type == 2:
            rman_string = ("run { \n"
                           "allocate channel ch1 device type disk format=\"" + backup_string + "\" ; \n"
                           "backup check logical archivelog all ; \n"
                           "} "
                           )

    cmdfile = config_path / 'backup_{0}_{1}.conf'.format(sid, type)
    write_config(str(cmdfile), rman_string)
    return str(cmdfile)


# main function
if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("sid", action="store", help="ORACLE_SID")
    parser.add_argument("backup_type", action="store",
                        help="Backup Type: inc0, inc1, arch")

    args = parser.parse_args()

    backups = {
        0: "inc0",
        1: "inc1",
        2: "arch"
    }
    btype = None
    if args.backup_type == "inc0":
        btype = 0
    elif args.backup_type == "inc1":
        btype = 1
    elif args.backup_type == "arch":
        btype = 2

    backup_db(args.sid, btype)

