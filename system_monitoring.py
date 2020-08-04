import yaml
import mysql.connector
import psutil
file = open('config.yml', 'r')
cfg = yaml.load(file, Loader=yaml.FullLoader)

mydb = mysql.connector.connect(
  host=cfg['databases']['host'],
  user=cfg['databases']['username'],
  passwd=cfg['databases']['password'],
  database=cfg['databases']['database']
)


import shutil
import subprocess
import os

data = {}

#DISK DATA

total, used, free = shutil.disk_usage("/")

data['disk'] = dict(
    {
        'total_disk': ("{:.2f}".format(total / 1024 ** 3, 1)),
        'used_disk': ("{:.2f}".format(used / 1024 ** 3, 1)),
        'free_disk': ("{:.2f}".format(free / 1024 ** 3, 1))
    }
)

mycursor = mydb.cursor()
sql = "INSERT INTO disk (`attributes`, `value`) VALUES (%s, %s);"
val=('total_disk',data['disk']['total_disk'])
mycursor.execute(sql, val)
sql = "INSERT INTO disk (`attributes`, `value`) VALUES (%s, %s);"
val=('used_disk',data['disk']['used_disk'])
mycursor.execute(sql, val)
sql = "INSERT INTO disk (`attributes`, `value`) VALUES (%s, %s);"
val=('free_disk',data['disk']['free_disk'])
mycursor.execute(sql, val)
mydb.commit()
#memory

linux_filepath = "/proc/meminfo"
meminfo = dict(
    (i.split()[0].rstrip(":"), int(i.split()[1]))
    for i in open(linux_filepath).readlines()
)

meminfo["memory_total_gb"] = meminfo["MemTotal"] / (2 ** 20)
meminfo["memory_free_gb"] = meminfo["MemFree"] / (2 ** 20)
meminfo["memory_available_gb"] = meminfo["MemAvailable"] / (2 ** 20)

data['memory'] = dict(
    {
        'total_memory': ("{:.2f}".format(meminfo["memory_total_gb"])),
        'used_memory': ("{:.2f}".format(meminfo["memory_total_gb"]-meminfo["memory_available_gb"])),
        'available_memory':("{:.2f}".format(meminfo["memory_available_gb"]))
    }
)
mycursor = mydb.cursor()
sql = "INSERT INTO memory (`attributes`, `value`) VALUES (%s, %s);"
val=('total_memory',data['memory']['total_memory'])
mycursor.execute(sql, val)
sql = "INSERT INTO memory (`attributes`, `value`) VALUES (%s, %s);"
val=('used_memory',data['memory']['used_memory'])
mycursor.execute(sql, val)
sql = "INSERT INTO memory (`attributes`, `value`) VALUES (%s, %s);"
val=('available_memory',data['memory']['available_memory'])
mycursor.execute(sql, val)
mydb.commit()


#cpu monitoring

cpu_usage=psutil.cpu_percent()
cpu_percent=cpu_usage*100
total_cpu=psutil.cpu_count()
mycursor = mydb.cursor()
sql = "INSERT INTO cpu (`attributes`, `value`) VALUES (%s, %s);"
val=('cpu_percent',cpu_usage)
mycursor.execute(sql, val)
mydb.commit()


