# NJ MVC Appointment Helper

An UNOFFICIAL Telegram bot that helps you find the most recent available appointment place for you.

## Demo

[@njmvc_bot](https://t.me/njmvc_bot)

## Usage

//todo

## Run Your Own

### Preparations

- Apply for a Telegram bot from [@BotFather](https://t.me/botfather). See [official instructions](https://core.telegram.org/bots/#6-botfather).
  - Get the API token.
  - Open the inline mode for the bot in Bot Settings.
- Get your (or other authorized users') user id from [@userinfobot](https://t.me/userinfobot).

### Get the code

- `git clone https://github.com/tangbao/njmvc_appt_helper.git`
- [Optional but recommended] Create and activate your virtual env, like Anaconda.
- `pip install -r requirements.txt`
- Under `secrets` folder,
    - Create `token.secret`, and put your token inside.
    - Create `authorized_users.secret`, and put the ids of authorized users inside, one per line, if you want only the 
      authorized users can use the subscription function.
- Run `bot.py` and start using!

## Resources

The bot is using [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot), please refer to its 
documentation for more detailed information if you want to make modifications to the bot.

## License

The project is published under the [WTFPL – Do What the Fuck You Want to Public License](http://www.wtfpl.net/).