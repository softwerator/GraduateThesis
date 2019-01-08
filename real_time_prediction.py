# coding: utf-8

# ARIMA modelini çağırmak için kullanılacak kütüphane
from statsmodels.tsa.arima_model import ARIMAResults
# Veri setini okumak için kullanılacak kütüphaneler
from pandas import Series, read_csv
# Tahmin değerlerini dosyaya kaydetmek için kullanılacak kütüphane
from pandas import DataFrame
# Tarih ve saat işlemler için kullanılacak kütüphaneler
from datetime import datetime as dt_parser
import datetime as dt_increaser
# Tahminlere ait CSV dosyasını açmak için kullanılacak kütüphane
import csv

# Günler arasındaki farkları tersine çevirmek için kullanılan metot
def inverse_difference(history, yhat, interval=1):
    return yhat + history[-interval]

#Test verisindeki indis değerlerini bulmak için kullanılan metot
def calculate_test_data_indexes(series):
    index_values = series.index.values
    index_values = DataFrame(index_values)
    return index_values

# Tahmin edilen ve ertesi güne ait değerlerin
# tarih ve zamanlarını bulmak için kullanılan metot
def calculate_datetimes(indexes):
    current_dt = str(indexes.iloc[-1][0])
    predicted_dt = dt_parser.strptime(current_dt, "%Y-%m-%d %H:%M:%S")
    predicted_dt = predicted_dt + dt_increaser.timedelta(days=1)
    predicted_dt = predicted_dt.strftime("%Y-%m-%d %H:%M:%S")
    return current_dt, predicted_dt

# Ana metot çalıştırılır
def main():
    # Zaman serisi okunur ve serideki değerler X değişkenine aktarılır
    series = Series.from_csv('/home/burakcan/GraduateThesis/monthly_data.csv', header=1)
    X = [x for x in series.values]
    # Tahminlerin olduğu veri seti okunur
    predicted_list = read_csv('/home/burakcan/GraduateThesis/predicted_data.csv', header=1)
    # Verinin 24 saat sonrasının tahmini için kullanılacak fark değeri
    days_in_year = 365
    # Model okunur ve tahmin edilir
    model = ARIMAResults.load('/home/burakcan/GraduateThesis/arima_model.pkl')
    forecast = model.predict(start=len(X))
    # Tahmin değerine ulaşılır
    inverted = inverse_difference(X, forecast[0], days_in_year)
    # Anlık zaman ve 24 saat sonrası hesaplanır
    test_data_indexes = calculate_test_data_indexes(series)
    current_dt, predicted_dt = calculate_datetimes(test_data_indexes)
    # Yeni verinin tahmin veri setinde olup olmadığı kontrol edilir
    if str(test_data_indexes.iloc[-1][0])[:-3] != predicted_list.iloc[-1][0]:
	# Tahmin veri seti açılır; yeni veri, dosyaya yazılır
        with open("/home/burakcan/GraduateThesis/predicted_data.csv", "a") as output_file:
            fieldnames = ["current_dt", "current_val", "predicted_dt", "predicted_val"]
            writer = csv.DictWriter(output_file, fieldnames=fieldnames)
	    if str(X[-1])[2:3] != '.':
                X[-1] = str(X[-1])[:2] + '.' + str(X[-1])[2:]
	    if str(X[-1])[6:7] == '.':
		X[-1] = str(X[-1])[:6] + str(X[-1])[7:]
	    if str(inverted)[2:3] != '.':
                inverted = str(inverted)[:2] + '.' + str(inverted)[2:]
	    if str(inverted)[6:7] == '.':
		inverted = str(inverted)[:6] + str(inverted)[7:]
            writer.writerow({"current_dt": current_dt[:-3], "current_val": X[-1], "predicted_dt": predicted_dt[:-3], "predicted_val": inverted})    
    
# Ana metodun çalıştırılmasına yönelik bir koşul kontrolü
if __name__ == "__main__":
    main()