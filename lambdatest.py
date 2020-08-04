from __future__ import with_statement
from datetime import datetime, timedelta
import time
import os
import yaml
import mysql.connector


def block(ip,ssh_block):
    block_cmd='iptables -A INPUT -s '+ip+' -p tcp --destination-port 22 -j DROP'
    unblock_cmd='echo "iptables -D INPUT -s '+ip+' -p tcp --destination-port 22 -j DROP" | at -m now + '+str(ssh_block)+' minute'
    print(block_cmd)
    print(unblock_cmd)
    os.system(block_cmd)
    os.system(unblock_cmd)
    mycursor = mydb.cursor()
    sql = "INSERT INTO  blocked_ip (`ipaddress`, `status`) VALUES (%s, %s);"
    val=(ip,'BLOCKED')
    mycursor.execute(sql, val)
    mydb.commit()


def password_fail(line):
    message_info = line.split('Failed password for')
    info = message_info[1]
    if info.find(' invalid user ') == 0:
        info1 = info[14:]
    else:
        info1 = info.strip(' ')
    info = info1.split(' ')
    information = {
        'user': info[0],
        'ip': info[2],
        'status': 'FAILED',
        }
    mycursor = mydb.cursor()
    sql = "INSERT INTO security (`username`,`ipaddress`, `status`) VALUES (%s, %s, %s);"
    val=(info[0],info[2],'FAILED')
    mycursor.execute(sql, val)
    mydb.commit()
    ip.append(info[2])
    print (information)
    return information


def success(line):
    message_info = line.split('Accepted')
    info = message_info[1]
    if info.find(' publickey for ') == 0:
        info1 = info[15:]
    elif info.find(' password for ') == 0:
        info1 = info[14:]
    info = info1.split(' ')
    information = {
        'user': info[0],
        'ip': info[2],
        'status': 'SUCCESS',
        }
    mycursor = mydb.cursor()
    sql = "INSERT INTO security (`username`,`ipaddress`, `status`) VALUES (%s, %s, %s);"
    val=(info[0],info[2],'SUCCESS')
    mycursor.execute(sql, val)
    mydb.commit()
    print (information)
    return information



file = open('config.yml', 'r')
cfg = yaml.load(file, Loader=yaml.FullLoader)

mydb = mysql.connector.connect(
  host=cfg['databases']['host'],
  user=cfg['databases']['username'],
  passwd=cfg['databases']['password'],
  database=cfg['databases']['database']
)



while True:
    time.sleep(120)
    if cfg['system_monitoring']==True:
        import system_monitoring
    before = timedelta(minutes=cfg['ssh_security']['frequency'])
    now = datetime.now().replace(microsecond=0, year=1900)
    before = (now-before)
    with open('/var/log/auth.log', 'r') as f:
        ip = []
        fail_attempts = []
        success_attempts = []
        for line in f:
            if datetime.strptime(line[0:15], '%b %d %X') >= before:
                if 'Failed password for' in line:
                    fail_attempts.append(password_fail(line))
                elif 'Accepted ' in line:
                    success_attempts.append(success(line))



    ssh_block = cfg['ssh_security']['block_min']
    attackers_ip = set(ip)
    attackers_ip = list(attackers_ip)
    for item in attackers_ip:
        if (ip.count(item)) >= cfg['ssh_security']['threshold']:
            if item not in cfg['ssh_security']['exception']:
                block(item,ssh_block)
