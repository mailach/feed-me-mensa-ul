# Feed me Mensa UL   

```
docker image build -t feed-me-mensa-ul:latest . 
docker container run --env-file ./.env feed-me-mensa-ul:latest
```

.env file needs to have following variables ste:  
```
BOT_TOKEN=  
CHANNEL_ID=  
MAINTAINER_TOKEN=  
MAINTAINER_CHATID=  
```

Set up cronjob  
```
crontab -e
```

and add execution everyday at 10.30:  
```
30 10 * * * docker container run --env-file /path/to/.env feed-me-mensa-ul:latest
```