# NJ MVC Appointment Helper

An UNOFFCIAL Telegram bot that helps you find the most recent available appointment place for you.

## Demo

[@njmvc_appt_bot](https://t.me/njmvc_appt_bot)

## Run Your Own

### Preparations

- Apply for a Telegram bot and get the API token from [@BotFather](https://t.me/botfather).
- Get your (or other authorized users') user id from [@userinfobot](https://t.me/userinfobot).

### Get the code

- `git clone https://github.com/tangbao/njmvc_appt_helper.git`
- [Optional but recommended] Create and activate your virtual env, like Anaconda.
- `pip install -r requirements.txt`
- Create a folder called `secrets` under the root of this project. Under `secrets`,
    - Create `token.secret`, and put your token inside.
    - Create `authorized_users.secret`, and put the ids of authorized users inside, one per line.
- Run `bot.py` and start using!

## Make Modifications

### More information

The bot is using [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot), please refer to its 
documentation for more detailed information.

## License

The project is published under the [WTFPL – Do What the Fuck You Want to Public License](http://www.wtfpl.net/).