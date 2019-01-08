# coding: utf-8

# Tahminlere ait CSV dosyasını açmak için kullanılacak kütüphane
import csv
# Tarih ve saat işlemler için kullanılacak kütüphaneler
from datetime import datetime as dt_parser
import datetime as dt_increaser

# Verileri işlemek ve elde edilen sonuçları döndürmek için kullanılan metot
def get_results(data):
    monthlylist, weeklylist, dailylist, hourlylist = [], [], [], []
    # Belirli zaman dilimlerine göre tarih-saat
    # değerleri oluşturulup değişkenlere atanır
    weekly_dt, daily_dt, hourly_dt, now_dt = generate_dt_by_periods()
    for row in data:
        instant_dt = generate_instant_dt(row["time"])
	if row["temp"][2:3] != '.':
	    row["temp"] = row["temp"][:2] + '.' + row["temp"][2:]
	# Belirli zaman dilimlerine göre veriler ilgili listelere eklenir
        monthlylist.append(float(row["temp"]))
        if weekly_dt <= instant_dt <= now_dt:
            weeklylist.append(float(row["temp"]))
        if daily_dt <= instant_dt <= now_dt:
            dailylist.append(float(row["temp"]))
        if hourly_dt <= instant_dt <= now_dt:
            hourlylist.append(float(row["temp"]))
    return [{'type': 'hourly', 'avg': sum(hourlylist) / float(len(hourlylist)), 'highest': max(hourlylist), 'lowest': min(hourlylist), 'count': len(hourlylist)},
	    {'type': 'daily', 'avg': sum(dailylist) / float(len(dailylist)), 'highest': max(dailylist), 'lowest': min(dailylist), 'count': len(dailylist)},
            {'type': 'weekly', 'avg': sum(weeklylist) / float(len(weeklylist)), 'highest': max(weeklylist), 'lowest': min(weeklylist), 'count': len(weeklylist)},
            {'type': 'monthly', 'avg': sum(monthlylist) / float(len(monthlylist)), 'highest': max(monthlylist), 'lowest': min(monthlylist), 'count': len(monthlylist)}]

# Belirli zaman dilimlerine göre başlangıç tarih-zaman değerlerini oluşturmak için kullanılan metot
def generate_dt_by_periods():
    now = dt_parser.now()
    weekly_dt = now - dt_increaser.timedelta(minutes=(7*24*60)-1)
    weekly_dt = dt_parser(weekly_dt.year, weekly_dt.month, weekly_dt.day, weekly_dt.hour, weekly_dt.minute)
    daily_dt = now - dt_increaser.timedelta(minutes=(24*60)-1)
    daily_dt = dt_parser(daily_dt.year, daily_dt.month, daily_dt.day, daily_dt.hour, daily_dt.minute)
    hourly_dt = now - dt_increaser.timedelta(minutes=59)
    hourly_dt = dt_parser(hourly_dt.year, hourly_dt.month, hourly_dt.day, hourly_dt.hour, hourly_dt.minute)
    now_dt = dt_parser(now.year, now.month, now.day, now.hour, now.minute)
    return weekly_dt, daily_dt, hourly_dt, now_dt

# Anlık verideki tarih-zaman değerini işlemek için kullanılan metot
def generate_instant_dt(time):
    # Gelen her bir verideki tarih-zaman kolonu parçalanır
    parsed_date = parse_dt(time, 1)
    parsed_time = parse_dt(time, 2)
    # Parçalanmış iki değişken kendi içinde yine parçalanır
    instant_day = int(parsed_date[2])
    instant_month = int(parsed_date[1])
    instant_year = int(parsed_date[0])
    instant_hour = int(parsed_time[0])
    instant_minute = int(parsed_time[1])
    # İstenen tarih-zaman formatına çevrilir
    instant_dt = dt_parser(instant_year, instant_month, instant_day, instant_hour, instant_minute)
    return instant_dt

# Tarih-zaman değerini ayırmak için kullanılan metot
def parse_dt(dt, code):
    date_time = dt.split(" ")
    if code == 1:
    	result = date_time[0].split("-")
    elif code == 2:
	result = date_time[1].split(":")
    return result

# Ana metot çalıştırılır
def main():
    with open("/home/burakcan/GraduateThesis/monthly_data.csv") as myfile:
        data = csv.DictReader(myfile, delimiter=',')
        results = get_results(data)
    return results

# Ana metodun çalıştırılmasına yönelik bir koşul kontrolü
if __name__ == "__main__":
    main()