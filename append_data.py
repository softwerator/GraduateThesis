# coding: utf-8

# Tahminlere ait CSV dosyasını açmak için kullanılacak kütüphane
import csv
# Ondalıklı sayı işlemleri için kullanılan kütüphane
from decimal import Decimal as dec
# Rastgele sayı işlemleri için kullanılan kütüphane
import random as rd
# Tarih-saat işlemleri için kullanılan kütüphane
import datetime as dt

# Sıcaklık verilerinin bir diziye eklendiği metot
def append_temperature_values(data):
    temps = []
    for i in data:
        if i[1][2:3] != '.':
            i[1] = i[1][:2] + '.' + i[1][2:]
        temps.append(i[1])
    temps.pop(0)
    return temps

# Sentetik değerin üretildiği metot
def generate_random_value(temps):
    min_temp = min(temps)
    min_temp = round(dec(min_temp), 0)
    max_temp = max(temps)
    max_temp = round(dec(max_temp), 0)
    digit = rd.randint(1,15)
    new_temp = round(rd.uniform(int(min_temp), int(max_temp)), digit)
    return new_temp

# İstenilen tarih-saat dönüşümünü sağlayan metot
def convert_now_dt():
    now_dt = dt.datetime.now()
    if len(str(now_dt.day)) == 1: firstpattern = '-0'
    else: firstpattern = '-'
    if len(str(now_dt.month)) == 1: secondpattern = '-0'
    else: secondpattern = '-'
    if len(str(now_dt.hour)) == 1: thirdpattern = ' 0'
    else: thirdpattern = ' '
    if len(str(now_dt.minute)) == 1: fourthpattern = ':0'
    else: fourthpattern = ':'
    now_dt = str(now_dt.year) + secondpattern + str(now_dt.month) + firstpattern + \
             str(now_dt.day) + thirdpattern + str(now_dt.hour) + fourthpattern + str(now_dt.minute)
    return now_dt

# Ana metot
def main():
    # Sıcaklık değerleri bir diziye eklenir
    with open("/home/burakcan/GraduateThesis/temperature_data.csv") as input_file:
        data = csv.reader(input_file, delimiter=',')
        temps = append_temperature_values(data)
            
    # Sentetik değer ve anlık tarih-saat üretilir
    new_temp = generate_random_value(temps)
    now_dt = convert_now_dt()

    # Oluşturulacak yeni satır veri setine eklenir
    with open("/home/burakcan/GraduateThesis/temperature_data.csv", "a") as output_file:
        fieldnames = ["time", "temp"]
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writerow({"time": now_dt, "temp": new_temp})

# Ana metodun çalıştırılmasına yönelik bir koşul kontrolü
if __name__ == "__main__":
    main()