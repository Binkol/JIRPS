## Before startup info

Make sure Docker and docker-compose are installed.

There are two versions on two branches.

1. **main** branch - version with RabbitMQ.

2. **noRabbitMq** branch - version without RabbitMQ.

**main** branch might require two builds if web service doesn't start after first startup (read bellow)

---

## Start Guide

Clone repo, enter foler with docker-compose.yml and simply run *"docker-compose up -d --build"*. After that you need to initialize database. Make sure web service is up and running and execute *"docker-compose exec web python manage.py create_db"*.
After that you should be good to go. In case of **main** branch if web service did not start after first try just *"docker-compose up -d --build"* it once again and then initialize database. If web service is down after database 
initialization just build it once again (yeah, I know...)

If all services are up and running you should be able to access site under 127.0.0.1:5000

If there are any problems with **main** branch just go for **noRabbitMq** version.

---

## Game Guide

1. Insert your name
2. Join into room and wait for other palyer to join to same room. (If running two clients from same machine you need to join to a room before logging in a new player in new tab otherwise user will get overwritten)
3. By pressing ROCK/PAPER/SCISSORS you are telling other player you are ready
4. When both players are ready outcome is printed, points assigned and after that you can choose R/P/S again.
5. If you are already in game and want to see your today's stats you need to quit/logout and log in under same name.
6. If you quit game, you have to create new room. You cannot rejoin room.


---