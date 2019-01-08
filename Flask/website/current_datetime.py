# coding: utf-8

# Tarih ve saat işlemler için kullanılacak kütüphaneler
from datetime import datetime as dt_parser
import datetime as dt_increaser

# Ana metot
def main():
    dt = dt_parser.now()
    if len(str(dt.day)) == 1: firstpattern = '0'
    else: firstpattern = ''
    if len(str(dt.month)) == 1: secondpattern = '-0'
    else: secondpattern = '-'
    if len(str(dt.hour)) == 1: thirdpattern = ' 0'
    else: thirdpattern = ' '
    if len(str(dt.minute)) == 1: fourthpattern = ':0'
    else: fourthpattern = ':'
    time = firstpattern + str(dt.day) + secondpattern + str(dt.month) + '-' + str(dt.year) \
           + thirdpattern + str(dt.hour) + fourthpattern + str(dt.minute)
    return time

# Ana metodun çalıştırılmasına yönelik bir koşul kontrolü
if __name__ == "__main__":
    main()
