from argparse import ArgumentParser

from bot import NJMVCBot

if __name__ == '__main__':
    parser = ArgumentParser(description='A third-party Telegram bot that helps you find '
                                        'the most recent available appointment place for you.')

    parser.add_argument('-l', '--log-file', type=str, default='njmvcbot.log',
                        help='The location of the log file. [default=njmvcbot.log]')
    parser.add_argument('-t', '--test', type=int, choices=[0, 1], default=0,
                        help='If 1, bot will enter test mode and use test token. '
                             '[default=0]')
    parser.add_argument('-a', '--auth', type=int, choices=[0, 1], default=1,
                        help='If 1, only authorized users can use /subscribe function. '
                             '[default=1]')
    parser.add_argument('-j', '--joblimit', type=int, default=3,
                        help='The maximum number of subscriptions a user can have. '
                             '[default=3]')
    parser.add_argument('-T', '--timeout', type=int, default=3,
                        help='If the MVC website does not response in {TIMEOUT} sec, return error. '
                             '[default=3]')
    parser.add_argument('-q', '--qintvl', type=int, default=120,
                        help='Check appointments every {QINTVL} sec. '
                             '[default=120]')

    args = parser.parse_args()

    bot = NJMVCBot(args)
