#!/usr/bin/python3
from datetime import datetime, timedelta

def add_one_minute_to_current_time():
    current_time = datetime.now()
    one_minute = timedelta(minutes=1)
    new_time = current_time + one_minute
    return new_time

# Example usage:
new_time = add_one_minute_to_current_time().strftime("%Y-%m-%dT%H:%M")
print(new_time)
print(add_one_minute_to_current_time().strftime("%Y-%m-%dT%H:%M"))
#print(datetime.now() + datetime(minutes=1))
#print((datetime.now() + datetime(minutes=1)).strftime("%Y-%m-%dT%H:%M"))

min_end_time = (datetime.now() + timedelta(minutes=2)).strftime("%Y-%m-%dT%H:%M")
print(min_end_time)