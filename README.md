# ECTC_tournament_manager
Docker version of https://github.com/ashish-b10/tournament_manager

# Prerequisites
Have Docker installed -

Linux: https://runnable.com/docker/install-docker-on-linux

Mac OS: https://runnable.com/docker/install-docker-on-macos 

Windows 10: https://runnable.com/docker/install-docker-on-windows-10

# Steps to start up the website
1) Clone this repository
```git clone https://github.com/ashleywang1/ECTC_tournament_manager.git```


2) In your computer, you should now have a directory called ECTC_tournament_manager. cd into that directory.
```cd ECTC_tournament_manager```
Also, run this command:
```git submodule init; git submodule update```

3) Build your docker image
```docker-compose build```

4) Start up your docker image (basically, a virtual machine)
```docker-compose up```

5) Go to localhost on your browser.

6) In a new terminal, in the ECTC_tournament_manager directory, run the following commands:

```docker exec -it ectc_tournament_manager_web_1 /bin/sh```

```cd /data/web/server```

```python3 manage.py createsuperuser```

Create a temporary superuser account. Use this account to log in.

7) Click on 'Settings', and then click on 'Set Import Registration Credentials', and load in the Google Drive credentials. (Ask Ashish for these keys, and do not upload them into this repository!)

# Developing

We use git submodules in order to pull in the tournament manager code from https://github.com/ashish-b10/tournament_manager. As a result, it is possible to add your commits to the tournament_manager repository. Just make sure you are in the web/server directory when you run any git commands.
