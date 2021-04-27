# panix - **P**alo **A**lto **N**etwork **I**nterface e**X**ecutor
A flask framework for automating Palo Alto firewalls

## Setup
You will need a fresh install of Ubuntu Mate **Desktop** not server.
```
sudo apt-get install -y mongodb
sudo apt-get install -y python-dev
sudo apt-get install -y python-pip
```
This will get the DB and the mongo clients loaded. PIP will be used to install the rest of the requirements.

For each firewall you will need a CSV file like this:

![CSV File](/static/assets/spreadsheet.png)

- A = Management IP of the PA firewall
- B = Network assigned to subinterface
- C = Not used...don't ask :-)
- D = full subnet mask with slash and bits
- E = Vlan TAG
- F = Comment
- G = Zone


## Get the app:
```
git clone://https.github.com/xod442/panix.github
cd panix
pip install -r requirements.txt
```

## Launch the app:(from the panix folder)
```
python manage.py runserver
```
Point your web broswer to localhost:5001. You will see the login screen. You will need
the credentials to an **active** firewall. These credentials are stored in a mongo db and
dropped automatically when you log out of the application.

Upon successful login, it is highly recommended to look at the help section.

**Note:**
This application uses a mongo database.

# Install on CentOS 8 server (minimal)

##Install Mongo:
```
yum update
sudo vi /etc/yum/repos.d/mongo-org.repo
```
## Contents:
```
[mongodb-org-3.4]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/$releasever/mongodb-org/3.4/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-3.4.asc
```
## Save file

## Check file
```
yum repolist (should see it in the repos)
sudo yum install mongodb-org
sudo systemctl start mongod
```
# Test MONGO client:
```
mongo (enter)
>
```
CTRL+D to exit


## Add python-pip and Dev tools
```
sudo dnf install python2
sudo yum install python2-devel
sudo yum groupinstall 'development tools'
```
# Shut the firewall OFF:
```
service firewalld stop
```
Should be ready to clone github repo.
