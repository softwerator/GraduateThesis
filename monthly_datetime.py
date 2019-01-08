from datetime import datetime as dt_parser
import datetime as dt_increaser

def get():
    datetime = generate(dt_parser.now() - dt_increaser.timedelta(minutes=(30*24*60)-1))
    return datetime

def generate(dt):
    if len(str(dt.day)) == 1: firstpattern = '-0'
    else: firstpattern = '-'
    if len(str(dt.month)) == 1: secondpattern = '-0'
    else: secondpattern = '-'
    if len(str(dt.hour)) == 1: thirdpattern = ' 0'
    else: thirdpattern = ' '
    if len(str(dt.minute)) == 1: fourthpattern = ':0'
    else: fourthpattern = ':'
    time = str(dt.year) + secondpattern + str(dt.month) + firstpattern + str(dt.day) + thirdpattern + str(dt.hour) + fourthpattern + str(dt.minute)
    return time
