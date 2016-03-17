# enragedrobo
### A Discord bot using discord.py

This is my personal bot for my Discord server(s). It is an improved version of an older project, [Priestism Bot](https://github.com/enragednuke/priestism_bot).

####Requirements:

 * Python 3.4.3+
 * discord.py (async branch rewrite)
 * Riot Games API key

####What it can do and where to find it

|File|Feature|
|---|---|
|`modules/trivia.py`|Trivia! (Only League of Legends by request for now, but will expand into the future)|
|`modules/botconfig.py`|Evaluate python code in the Discord server via `evalc`|
|`modules/botconfig.py`|Custom commands that can be customized to be evaluated as code, or specified whether or not to be outputted to the server via `addcmd <name> <is_code> <output_to_chat> <content>`|
|`bot2.py`|View larger versions of the default small avatars via `avatar`|
|`bot2_music.py`|Music queue|
|`???`|Much, much more to be added! (especially porting old functionality from my previous project)|

####Some things to note:

 * The music bot is rougher looking than the main bot. This is because it was built on a code base that used an older version of discord.py, so it won't look nearly as nice nor use the new commands interface.
 * Lots of things are not 100% completed or safeguarded against exceptions. There are thousands of lines of code to be added, fear not.
 * Not all the code is 100% efficient and I know this. I'm no python prodigy, but I try to make my code as efficient as I can think to make it. If you know how to make certain blocks drastically more efficient without massively elongating the code itself, feel free to fork the repo and push a pull request with your changes.

##Setup

A massive improvement over Priestism Bot, you should be able to run your own instance of this bot with relative ease. 

**Please note**: You need to know your discord ID. You can get this through other means, or you can remove the `@checks.is_owner()` line above `async def evalc(...)` in `modules/botconfig.py` then run the command `;evalc ctx.message.author.id` in Discord to reveal your ID. Remember to put that line back though, as this command is very abusable if the public is capable of accessing it.

There are three `.example` files provided for the 3 json files you need to modify. Just remove the `.example` and edit them as necessary. 

Make sure your bot is already connected to your server before trying to use it (it obviously won't work if it can't see your commands!)

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

