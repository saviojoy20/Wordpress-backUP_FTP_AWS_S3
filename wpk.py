
import os
import subprocess
import sys
import pysftp
import boto
import boto.s3
from boto.s3.key import Key
import shutil
import argparse
import tarfile
import datetime
import subprocess
import re
import logging
import configparser




# parsing wordpress configuration file 

def parsing_wpconfig(install_location):
    """
    - This function takes wordpress installation directory as argument.
    - Parse wp-config.php and retrive all database information for backup.
    - return {'database':database,'user':user, 'password':password, 'host':host}
    """

    try:

        cret_log_or_print2scren("Parsing wp-config.php File of {}".format(install_location))

        config_path = os.path.normpath(install_location + '/wp-config.php')
        with open(config_path) as fh:
            content = fh.read()
        regex_db = r'define\(\s*?\'DB_NAME\'\s*?,\s*?\'(?P<DB>.*?)\'\s*?\);'
        regex_user = r'define\(\s*?\'DB_USER\'\s*?,\s*?\'(?P<USER>.*?)\'\s*?\);'
        regex_pass = r'define\(\s*?\'DB_PASSWORD\'\s*?,\s*?\'(?P<PASSWORD>.*?)\'\s*?\);'
        regex_host = r'define\(\s*?\'DB_HOST\'\s*?,\s*?\'(?P<HOST>.*?)\'\s*?\);'
        databse = re.search(regex_db, content).group('DB')
        user = re.search(regex_user, content).group('USER')
        password = re.search(regex_pass, content).group('PASSWORD')
        host = re.search(regex_host, content).group('HOST')
        cret_log_or_print2scren('Completed parsing configuration file')
        return {'database': databse,
                'user': user,
                'password': password,
                'host': host
                }

    except FileNotFoundError:
        print('Falied')
        print('File Not Found,', config_path)
        sys.exit(1)

    except PermissionError:
        print('Falied')
        print('Unable To read Permission Denied,', config_path)
        sys.exit(1)

    except AttributeError:
        print('Falied')
        print('Parsing Error wp-config.php seems to be corrupt,')
        sys.exit(1)



# function to take SQLdump, This function takes 

def take_sqldump(db_details,BACKUP_DIRECTORY):
    """
    - This function takes parsing_wpconfig as argument.
    - Create database backup using db_details dictionary.
    """
    cret_log_or_print2scren("Creating database dump")

    try:
        USER = db_details['user']
        PASSWORD = db_details['password']
        HOST = db_details['host']
        DATABASE = db_details['database']

        DUMPNAME = os.path.normpath(os.path.join(BACKUP_DIRECTORY,db_details['database'] + '.sql'))
 
        cret_log_or_print2scren("mysqldump  -u {} -p{} -h {} {}  > {} 2> /dev/null".format(USER, "******", HOST, DATABASE, DUMPNAME))
        cmd = "mysqldump  -u {} -p{} -h {} {}  > {} 2> /dev/null".format(USER, PASSWORD, HOST, DATABASE, DUMPNAME)
      
        subprocess.check_output(cmd, shell=True)

        cret_log_or_print2scren('Completed creating mysqldump')

        return DUMPNAME

    except subprocess.CalledProcessError:
        print('Failed')
        print(': MysqlDump Failed.')
        sys.exit(1)
    except:
        print('Failed')
        print(': Unknown Error Occurred.')
        sys.exit(1)

# fuction to upload to SFTP server

def sftp_upload(archive_path,SFTP_HOST,SFTP_USER,SFTP_PASSWD,SFTP_DIR,SFTP_PORT):
    """
    - Upload archive to sftp server.
    """
    cret_log_or_print2scren("uploading to sftp server")
    try:
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        cret_log_or_print2scren("Archive path : {}, SFTP_Host : {}, SFTP_User : {}, SFTP_Diroctory : {}, SFTP_Port {} ".format(archive_path,SFTP_HOST,SFTP_USER,SFTP_DIR,SFTP_PORT))
        with pysftp.Connection(SFTP_HOST, username=SFTP_USER, password=SFTP_PASSWD, port=int(SFTP_PORT),
                               cnopts=cnopts) as sftp:
            if not sftp.exists(SFTP_DIR):
                sftp.makedirs(SFTP_DIR)
            sftp.cwd(SFTP_DIR)
            sftp.put(archive_path)
            sftp.close()
        cret_log_or_print2scren('Completed uploading to SFTP server')
    except PermissionError:
        print('Failed')
        print(': Permission Denied Error From Server.')
        sys.exit(1)


# function to upload to AWS S3

def create_s3bucket(bucket_name,local_file,object_name):

  conn = boto.connect_s3()
  bucket = conn.create_bucket(bucket_name,location=boto.s3.connection.Location.DEFAULT)
  printcret_log_or_print2scren("Uploading {} to Amazon S3 bucket {} ".format(local_file, bucket_name))
  def percent_cb(complete, total):
     sys.stdout.write('.')
     sys.stdout.flush()

  k = Key(bucket)
  k.key = object_name
  k.set_contents_from_filename(local_file,cb=percent_cb, num_cb=10)

# Fuction to create archive

def make_archive(wordpress_path, dumpfile_path,BACKUP_DIRECTORY):
    """
    - This function takes wordpress install path & sqlfile dump path as args.
    - create an gzip arive under BACKUP_DIRECTORY.
    """
    try:
        cret_log_or_print2scren("Making archive with wordpress location {} and database dump {} in {}".format(wordpress_path,dumpfile_path,BACKUP_DIRECTORY))

        time_tag = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        dir_name = os.path.basename(wordpress_path.rstrip('/'))
        archive_name = os.path.normpath(BACKUP_DIRECTORY+'/'+dir_name+'-'+time_tag+'.tar.gz')

        with tarfile.open(archive_name, "w:gz") as tar:
            tar.add(wordpress_path)
            tar.add(dumpfile_path, arcname="sql.dump")
        print('Completed generating archive')
        return archive_name

    except FileNotFoundError:
        print('Falied')
        print(': File Not Found,', tar_name)
        sys.exit(1)

    except PermissionError:
        print('Falied')
        print(': PermissionError Denied While Copying.')
        sys.exit(1)

    except:
        print(': Unknown error occurred while taring directory :', location)
        sys.exit(1)

# function to create backup directory

def cret_log_or_print2scren(log_line):

    if switch_t:

         logging.basicConfig(filename="wordpress_backup.log",format='%(asctime)s  %(message)s', filemode='a') 
  
         #Creating an object 
         logger=logging.getLogger() 
  
         #Setting the threshold of logger to DEBUG 
         logger.setLevel(logging.DEBUG) 
  
          #Test messages 
         logger.debug(log_line) 
    else:
        print(log_line)


def make_backupdir(location):

    if not os.path.exists(location):
        os.makedirs(location)


# main function starts

def main():
    # Parsing arguments, Wordpress installation directory and switches
    parser = argparse.ArgumentParser()

    parser.add_argument('-p', dest='path', required=True, help='Path to wordpress.')
    parser.add_argument("-l", dest='local_backup', default='/tmp/wpbackup',
                        help='Only creates local backup.')
    parser.add_argument("-f", '--ftp', dest='swih_f', action="store_true", help=" uploads to ftp server")
    parser.add_argument("-s", '--aws_s3', dest='swih_s', action="store_true", help="uploads to s3 ")
    parser.add_argument("-t", '--track', dest='swih_t', action="store_true", help="enables logging")
    arguments = parser.parse_args()

    # saving parsed arguments to variables

    install_dir = arguments.path
    BACKUP_DIRECTORY = arguments.local_backup
    switch_f = arguments.swih_f
    switch_s = arguments.swih_s
    global switch_t
    switch_t = arguments.swih_t
    # print("valu of t is")
    # print(switch_t)
    
    # checking wordpress directory exists or not 
    if os.path.exists(install_dir):

        # Creating backup directory for storing  backup files

        make_backupdir(BACKUP_DIRECTORY)
        database_info = parsing_wpconfig(install_dir)

        # database_info = {'database': databse,'user': user,'password': password,'host': host }
        
        dump_location = take_sqldump(database_info,BACKUP_DIRECTORY)

        # dump_location = name of dump file creaed

        archive_path = make_archive(install_dir, dump_location,BACKUP_DIRECTORY)

        # getting server details from config.ini file

        parser = configparser.ConfigParser()
        parser.read('config.ini')

        # uploads to FTP server if the -f switch is given
        
        if switch_f:

            # SFTP credentials are taken from config.ini file and enviornmental variables


            SFTP_HOST = parser.get('SFTP_Details', 'SFTP_HOST')
            SFTP_USER = parser.get('SFTP_Details', 'SFTP_USER')
            SFTP_DIR =  parser.get('SFTP_Details', 'SFTP_DIR')
            SFTP_PORT = parser.get('SFTP_Details', 'SFTP_PORT')
            SFTP_PASSWD = os.environ['SFTP_PASSWD']
            
            # calling sftp function to upload to sftp server

            sftp_upload(archive_path,SFTP_HOST,SFTP_USER,SFTP_PASSWD,SFTP_DIR,SFTP_PORT)

        # uploads to AWS_s3 if the -s switch is given, credentials are taken from environmental variables
        if switch_s:

            #Bucket name is taken from config.ini file

            BUCKT_NAME = parser.get('S3_Details', 'BUCKT_NAME')
            base = os.path.basename(archive_path)
            a = create_s3bucket(BUCKT_NAME, archive_path, base)
    else:
        print('')
        print('Error: Path Not Found'.format(install_dir))
        print('')

if __name__ == '__main__':
    main()



