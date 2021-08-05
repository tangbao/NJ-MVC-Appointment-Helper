# NJ MVC Appointment Helper

An UNOFFICIAL Telegram bot that helps you find the most recent available appointment place for you.

If it could help you, please give me a star. Appreciated.

For now, I am working on the persistence of the bot - make everything, including the job queue of the bot persistent 
after restarting the bot. So please remember to go back and check for updates.

I really hope this COVID-19 pandemic can end soon so that everything can go back to normal. Hope this bot can help you 
a little.

Stay safe.

## Demo

[@njmvc_bot](https://t.me/njmvc_bot)

Note that you can only use `/check` function of this demo bot. Only authorized users can use `/subscribe`. I do not make
it fully public because I cannot afford too much cloud resources.

### **Privacy Disclaimer**

The logger of the bot may record your Telegram username and all the messages you send to the bot. Your Telegram user 
id will be used to verify if you are an authorized user or not. All the data collected by the bot will only be used for 
debug and will not be used for any analytics or shared/sold to a third party.

If you do not agree with this privacy policy, please do not use the bot, and consider 
[building your own bot](#build-your-own).

Privacy disclaimer updated 2021 Jul 28.

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

An example of a running subscription

![/subscription Running](/media/active_sub.png)

`/mysub`

![/mysub](/media/mysub.png)

## Build Your Own

> Use at your own risk. There is NO WARRANTY.

### Preparations

- Apply for a Telegram bot from [@BotFather](https://t.me/botfather). 
  See [official instructions](https://core.telegram.org/bots/#6-botfather). 
  Remember to get the API token.
- Get your (or other authorized users') user id from [@userinfobot](https://t.me/userinfobot).

### Configuration & Deployment

> In the current version, the bot is not persistent. It means that everything will lose after you restart the bot. You 
> have to create the subscriptions again.

- `git clone https://github.com/tangbao/NJ-MVC-Appointment-Helper.git`
- [Optional but recommended] Create and activate your virtual env, like Anaconda.
- `pip install -r requirements.txt`
- Under `secrets` folder,
    - Create `token.secret`, and put your token inside.
    - Create `authorized_users.secret`, and put the ids of authorized users inside, one per line, if you want only the 
      authorized users can use the subscription function. If you hope everyone can use it, set `REQUIRE_AUTH` in 
      `config.py` (located under project root) as `False`.
- If you want to change the maximum number of subscriptions a user can create, change `JOB_LIMIT` in `config.py`.
- Run `bot.py` and start using!

### Resources

The bot is using [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot), please refer to its 
documentation for more detailed information about docs, deployment, and so on.

## Development Plan (NO GUARANTEE)
- Make the bot persistent - subscription still exists after the bot restarts.
- Improve user experience and logger info.
- Automatically submit an appointment (I guess I will never do this).

## Questions, Bugs, and Contributions

You can open an issue or email me (i AT tbis DOT me) directly. PR is welcome.

## License

The project is published under the [WTFPL – Do What the Fuck You Want to Public License](http://www.wtfpl.net/).
