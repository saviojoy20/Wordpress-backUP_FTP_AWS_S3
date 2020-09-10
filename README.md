# Wordpress-backUP_FTP_AWS_S3

A Python script to backup wordpress, the backup file can be saved locally, to an FTP server or AWS S3.

+ Detects database and wordpress files
+ Creates a .gz file with wordpress contents and database
+ Push it to FTP server or AWS S3, or can be saved locally
+ Can enable logging for the tool and a log file  "wordpress_backup.log" will be created in the PWD

#SETUP

pip3 install -r  requirements.txt

The FTP, AWS details should be configured in config.ini

[SFTP_Details]

SFTP_HOST = ip/domain_name
SFTP_USER = user_name
SFTP_DIR = dir_name
SFTP_PORT = 22

[S3_Details]

BUCKT_NAME = bucketname


FTP password and AWS API Keys should be added as environmental variables

#Usage

python3 wpk.py [-h] -p PATH [-l LOCAL_BACKUP] [-f] [-s] [-t]

  -h, --help       show this help message and exit
  -p PATH          Path to wordpress.
  -l LOCAL_BACKUP  Only creates local backup.
  -f, --ftp        uploads to ftp server
  -s, --aws_s3     uploads to s3
  -t, --track      enables logging


Defaults, the backup file will be saved in /tmp/wpbackup/

Eg

$ python3 wpk.py  -p /home/user/public_html/ -f -t -s 



