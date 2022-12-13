## FAST

### restart server after api changes

```sudo systemctl daemon-reload && sudo systemctl restart gunicorn && sudo systemctl restart nginx```

## MONGODB

```systemctl start mongod.service```

```mongosh```

```use cpts```

```show collections```

```db.cpt_collection.drop()```

```exit```


## INITIAL DO SETUP

### Setup as a service

[Source](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-22-04)

#### Create a socket 

```sudo nano /etc/systemd/system/gunicorn.socket```

Add the following lines;

```
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```

#### Create systemd service file

```sudo nano /etc/systemd/system/gunicorn.service```

Add the following lines;

```
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=breinbaas
Group=www-data
WorkingDirectory=/home/breinbaas/app
ExecStart=gunicorn server.app:app -w 4 -k uvicorn.workers.UvicornWorker

[Install]
WantedBy=multi-user.targetUnit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target
```

#### start and enable gunicorn

```
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket
```

#### check status

```sudo systemctl status gunicorn.socket```

### Start stop service

#### From gunicorn 

Command to check if you can start the service;

```gunicorn -w 4 -k uvicorn.workers.UvicornWorker server.api:app```

#### From service

**After changing the service, reload the daemon to reread the service definition and restart the Gunicorn process by typing:**

```sudo systemctl daemon-reload```

```sudo systemctl restart gunicorn```

### Debugging 

Find errors using;

```sudo journalctl -u gunicorn```

Check functionality;

```curl --unix-socket /run/gunicorn.sock localhost```

### NGINX setup

#### create nginx server block

```sudo nano /etc/nginx/sites-available/leveelogicapi```

Add the following content;

```
server {
    listen 80;
    # server_name 159.89.13.116; see below comment 1
    server_name api.leveelogic.com; see below comment 2

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /home/breinbaas/app;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
```

* comment 1, this will work as long as you have **not** set google domains to point to the DO IP address
* comment 2, as soon as Google domains uses api.leveelogic.com as a referer to the DO IP address this will work, if not you will see the NGINX welcome message!

Add to available sites;

```sudo ln -s /etc/nginx/sites-available/leveelogicapi /etc/nginx/sites-enabled```

Check with nginx;

```sudo nginx -t```

Update;

```sudo systemctl restart nginx```

### Update domains

* Goto [Goole Domains](https://domains.google.com/) 
* Goto DNS | Manage custom records
* Add a new record like api.leveelogic.com pointing to the IP address of the DO droplet.
