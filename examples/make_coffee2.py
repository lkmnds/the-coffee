#!/usr/bin/env python3

import sys
import logging
import libcoffee

logger = logging.getLogger('example_client')

def main(args):
    try:
        coffee_ip = args[1]
    except:
        coffee_ip = '0.0.0.0'

    coffee_machine = libcoffee.connect(coffee_ip)

    user = input('user: ')
    password = input('password: ')

    try:
        coffee_machine.auth(user, password)
    except Exception as err:
        logger.error('Error authenticating to the coffee machine', exc_info=True)
        return

    # Authenticated, make a coffee
    coffee = coffee_machine.get_drink('coffee')
    while cofee.get_state().ready:
        print('Waiting for coffee to be ready...')
        time.sleep(1)

    print("Coffee ready!")

if __name__ == '__main__':
    sys.exit(main(sys.argv))
