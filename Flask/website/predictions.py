# coding: utf-8

# Tahminlere ait CSV dosyasını açmak için kullanılacak kütüphane
import csv
# Tarih ve saat işlemler için kullanılacak kütüphaneler
from datetime import datetime as dt_parser
import datetime as dt_increaser

# 3 saat öncesinin tarih-zamanını biçimleyen metot
def calculate_datetime(hour):
    dt = dt_parser.now() - dt_increaser.timedelta(minutes=(60*hour)-1)
    dt = dt.strftime("%Y-%m-%d %H:%M")
    return dt

# Ana metot
def main():
    with open("/home/burakcan/GraduateThesis/predicted_data.csv") as myfile:
	predictions_list = []
        data = csv.DictReader(myfile, delimiter=',')
        three_hours_ago = calculate_datetime(3)
    	for row in data:
            if row["current_dt"] >= three_hours_ago:
                predictions_list.append({'current_dt':row["current_dt"], 'current_val':float(row["current_val"]), 
                    'predicted_dt':row["predicted_dt"], 'predicted_val':float(row["predicted_val"])})
    return predictions_list

# Ana metodun çalıştırılmasına yönelik bir koşul kontrolü
if __name__ == "__main__":
    main()
