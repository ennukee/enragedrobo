# enragedrobo
### A Discord bot using discord.py

This is my personal bot for my Discord server(s). It is an improved version of an older project, [Priestism Bot](https://github.com/enragednuke/priestism_bot).

####Requirements:

 * Python 3.4.3+
 * discord.py (async branch rewrite)
 * Riot Games API key


####Setup:

A massive improvement over Priestism Bot, you should be able to run your own instance of this bot with relative ease. 

**Please note**, however, that you need to know your discord ID. You can get this through other means, or you can remove the `@checks.is_owner()` line in `modules/botconfig.py` then run the command `;evalc ctx.message.author.id` to reveal your ID. Remember to put that line back though, as this command is very abusable if the public is capable of accessing it.

There are three `.example` files provided for the 3 json files you need to modify. Just remove the `.example` and edit them as necessary.

The files you do need to modify are as following:

#### data/admins.json
```py
{
  "YOUR DISCORD ID HERE": 1
}
```

#### data/login.json
```py
{
  "email": "YOUR EMAIL HERE",
  "password": "YOUR PASSWORD HERE"
}
```

#### data/apikeys.json
```py
{
  "LoL": "YOUR RIOT GAMES API KEY HERE"
}
```

#### utils/BotConstants.py
```py
def __init__(self):
  self.__ingame = False
  self.__gamechannel = None
  self.__gameserver = None
  self.__gamestarter = None
  self.id = 'YOUR BOTS ID GOES HERE'
```

#### checks.py
```py
def is_owner_check(message):
    return message.author.id == 'YOUR ID HERE'
```

