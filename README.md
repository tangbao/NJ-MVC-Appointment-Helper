# NJ MVC Appointment Helper

An UNOFFICIAL Telegram bot that helps you find the most recent available appointment place for you.

I really hope this COVID-19 pandemic can end soon so that everything can go back to normal. Hope this bot can help you 
a little.

Stay safe.

## Demo

[@njmvc_bot](https://t.me/njmvc_bot)

## Usage

`/check` Check the most recent available places for appointment.

`/subscribe` Receive a notification when a more recent time slot is available. Authorized users only. 
You can have at most three subscriptions.

`/mysub` Manage your subscriptions.

`/help` Show the help message.

## Examples

`/check`

![/check Part 1](/media/check1.png)

![/check Part 2](/media/check2.png)

`/subscribe`

![/subscription Part 1](/media/sub1.png)

![/subscription Part 2](/media/sub2.png)

`/mysub`

![/mysub](/media/mysub.png)

## Run Your Own

> Use at your own risk. There is NO WARRANTY.

### Preparations

- Apply for a Telegram bot from [@BotFather](https://t.me/botfather). 
  See [official instructions](https://core.telegram.org/bots/#6-botfather). 
  Remember to get the API token.
- Get your (or other authorized users') user id from [@userinfobot](https://t.me/userinfobot).

### Configuration & Deployment

- `git clone https://github.com/tangbao/njmvc_appt_helper.git`
- [Optional but recommended] Create and activate your virtual env, like Anaconda.
- `pip install -r requirements.txt`
- Under `secrets` folder,
    - Create `token.secret`, and put your token inside.
    - Create `authorized_users.secret`, and put the ids of authorized users inside, one per line, if you want only the 
      authorized users can use the subscription function. If you hope everyone can use it, set `REQUIRE_AUTH` in 
      `config.py` as `False`.
- Run `bot.py` and start using!

### Resources

The bot is using [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot), please refer to its 
documentation for more detailed information about docs, deployment, and so on.

### Questions, Bugs, and Contributions

You can open an issue or email me (i AT tbis DOT me) directly. PR is welcome.

## License

The project is published under the [WTFPL – Do What the Fuck You Want to Public License](http://www.wtfpl.net/).