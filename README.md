# Feed me Mensa UL  

A quick-and-dirty script to scrape the daily menu of Leipzig University Mensa and send it to a telegram channel. The script is currently dockerized and running as a cronjob on a server, executed daily at 10.30 am. 

Check out the telegram channel: <https://t.me/feed_me_mensa_ul>

## Add secrets to env file

For security reasons secrets are secret *-*. For testing and developing add your own bot credentials. And put in root folder in .env file.

```
BOT_TOKEN=  
CHANNEL_ID=  
MAINTAINER_TOKEN=  
MAINTAINER_CHATID=
MACHINE_NAME=
```



## Running the docker container
If you have added secrets to .env file, you can build an run the docker container. 

```
docker image build -t feed-me-mensa-ul:latest . 
docker container run --env-file ./.env feed-me-mensa-ul:latest
```



## Setting up cronjob  

Add new cronjob.

```
crontab -e
```

Add execution everyday at 10.30 am.  
```
30 10 * * * docker container run --env-file /path/to/.env feed-me-mensa-ul:latest
```

## Possible Enhancements
* Write tests ;)  
* Mensa am Sportforum, Cafeteria etc  
* Add discord, slack, mattermost, signal etc.  