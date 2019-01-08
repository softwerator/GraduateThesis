# coding: utf-8

# Tarih ve saat işlemler için kullanılacak kütüphaneler
from datetime import datetime as dt_parser
import datetime as dt_increaser
# Veri önişleme ve analizi için kullanılan kütüphane
import pandas as pd

# Tarihleri gün, hafta ve ay bazından karşılaştırmak için kullanılan metot
def compare_dt(value):
    if value == 1:
        datetime = generate_dt(dt_parser.now() - dt_increaser.timedelta(minutes=(24*60)-1))
    elif value == 2:
        datetime = generate_dt(dt_parser.now() - dt_increaser.timedelta(minutes=(7*24*60)-1))
    elif value == 3:
        datetime = generate_dt(dt_parser.now() - dt_increaser.timedelta(minutes=(30*24*60)-1))
    return datetime
        
# İstenilen tarih-saat biçimini oluşturmak için kullanılan kütüphane
def generate_dt(dt):
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

# Ana metot
def main():
    # Veri seti okunur
    df = pd.read_csv('/home/burakcan/GraduateThesis/predicted_data.csv')
    # Anlık tarih-zaman değerleri bir değişkene atanır
    current_dts = df.current_dt.values
    # Gün, hafta ve ay bazından toplam oran ve adet
    # verilerini hesaplamak için değişkenler yaratılır
    daily_per, weekly_per, monthly_per = 0, 0, 0
    daily_count, weekly_count, monthly_count = 0, 0, 0
    # Veri setindeki tüm veriler kontrol edilir
    for index, row in df.iterrows():
        # İlgili satırdaki tahmin edilen tarih-saat değeri,
        # herhangi bir anlık tarih-zaman sütununda yer alıyorsa;
        if row["predicted_dt"] in current_dts:
            # İlgili anlık tarih-zaman sütununun olduğu satırdaki ilk 2 sütunluk değeri alır
            current_side = df.loc[row["predicted_dt"] == current_dts, ["current_dt", "current_val"]].values
            # İki oranı birbirine oranlar
            if float(row["predicted_val"]) < float(current_side[0][1]):
                percentage = float(row["predicted_val"]) / float(current_side[0][1])
            else:
                percentage = float(current_side[0][1]) / float(row["predicted_val"])
            # Gün, hafta ve ay bakımından toplam oran ve adet değişkenleri hesaplanır
            if row["predicted_dt"] >= compare_dt(1):
                daily_count += 1
                daily_per += percentage
            if row["predicted_dt"] >= compare_dt(2):
                weekly_count += 1
                weekly_per += percentage
            if row["predicted_dt"] >= compare_dt(3):
                monthly_count += 1
                monthly_per += percentage
    # Periyot bazında değerlerin işlenip işlenilmediği kontrol edilir
    if daily_count == 0: daily_per = 0
    else: daily_per = (daily_per/daily_count) * 100
    if weekly_count == 0: weekly_per = 0
    else: weekly_per = (weekly_per/weekly_count) * 100
    if monthly_count == 0: monthly_per = 0
    else: monthly_per = (monthly_per/monthly_count) * 100
    # İşlemlerin sonunda elde edilen değerler işlenip gönderilir
    return [{"type": "daily", "mean_per": daily_per, "count": daily_count},
            {"type": "weekly", "mean_per": weekly_per, "count": weekly_count},
            {"type": "monthly", "mean_per": monthly_per, "count": monthly_count}]

# Ana metodun çalıştırılmasına yönelik bir koşul kontrolü
if __name__ == "__main__":
    main()
