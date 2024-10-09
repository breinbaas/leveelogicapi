### as root

* ```adduser breinbaas```
* ```usermod -aG sudo breinbaas```
* ```rsync --archive --chown=breinbaas:breinbaas ~/.ssh /home/breinbaas```

### as breinbaas

* ```sudo apt update```
* ```sudo apt upgrade```
* ```sudo apt install python3-venv sqlite3 net-tools```
* ```ssh-keygen```
* copy pub key to github
* ```git clone git@github.com:breinbaas/leveelogicapi.git```
* change into directory
* ```python3 -m venv .venv```
* ```source .venv/bin/activate```
* ```python3 -m pip install -r requirements.txt```
* create the .env file with SECRET_KEY, ALGORITHM, USER, PASSWORD
* ```bash release.sh```

(OUDE IP 159.89.13.116)



