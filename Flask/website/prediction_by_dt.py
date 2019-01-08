# coding: utf-8

# Veri önişleme ve analizi için kullanılan kütüphane
import pandas as pd
# Tarih ve saat işlemler için kullanılacak kütüphaneler
from datetime import datetime as dt_parser
import datetime as dt_increaser
from dateutil.parser import parse

# 24 saat önce ve şimdiki tarih-zaman değerleri bulunur
def generate_dts():
    # 24 saat önceki tarih-zaman değeri bulunur
    before_24_hours = dt_parser.now() - dt_increaser.timedelta(minutes=(24*60)-1)
    before_24_hours = before_24_hours.strftime("%Y-%m-%d %H:%M")
    # Şimdiki tarih-zaman değeri bulunur
    and_now = dt_parser.now() - dt_increaser.timedelta(minutes=1)
    and_now = and_now.strftime("%Y-%m-%d %H:%M")
    return before_24_hours, and_now

# Ana metot
def main(datetime):
    try:
        before_24_hours, and_now = generate_dts()
        try:
            # Girilen değerin istenen tarih-saat formatına sahip olup olmadığı kontrol edilir
            date, time = datetime.split(" ")
            year, month, day = date.split("-")
            hour, minute = time.split(":")
            datetime = dt_increaser.datetime(int(year),int(month),int(day), int(hour), int(minute))
            datetime = datetime.strftime("%Y-%m-%d %H:%M")
            # Girilen değer ile 24 saat önceki değer kontrol edilir
            if (before_24_hours <= datetime <= and_now):
                # Veri seti okunur
                df = pd.read_csv('/home/burakcan/GraduateThesis/predicted_data.csv')
                values = df.loc[df["current_dt"] == datetime, ["current_val", "predicted_dt", "predicted_val"]].values
                # Girilen tarihle ilgili ölçülen bir değer yoksa
                if values.size == 0:
                    return "Unfound date-time"
                return {"current_val": float(values[0][0]), "predicted_dt": values[0][1], "predicted_val": values[0][2]}
            else:
                return "Invalid date-time"
        except:
            return "Invalid format"
    except:
        return "Unexcepted error"