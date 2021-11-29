import time
import requests

if __name__ == '__main__':
    while True:
        # time.sleep(10)
        try:
            exec(open('C:\ВТОРОЙ\PROJECTS\БОТ\English\y.version\main.py').read())
        except requests.exceptions.ConnectionError:
            r.status_code = "Connection refused"
            continue