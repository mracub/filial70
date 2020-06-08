from datetime import datetime, date, time

if __name__ == "__main__":
    t = '2020-02-02'
    print(datetime.strftime(datetime.now(), "%Y-%m-%d_%H-%M-%S"))