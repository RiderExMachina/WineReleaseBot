#! /usr/bin/env python3
## Relays information to both `print` and logfile.
import logging, datetime

logging.basicConfig(filename=f"/var/log/wrb/wrb-{datetime.datetime.now().strftime('%B-%d-%Y')}.log", encoding='utf-8', level=logging.INFO)

if __name__ == "relay":
    def relay(msg):
        print(msg)
        logging.info(msg)
