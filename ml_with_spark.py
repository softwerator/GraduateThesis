# coding: utf-8

# Büyük veri analizi için kullanılan kütüphaneler
from pyspark import sql, SparkConf, SparkContext
# Veri önişleme ve analizi için kullanılan kütüphane
import pandas as pd
# Matematiksel işlemler için kullanılan kütüphane
import numpy as np
# Zaman serilerine dayalı regresyon için kullanılan kütüphane
from statsmodels.tsa.arima_model import ARIMA
# Tarih ve saat işlemleri için kullanılan kütüphaneler
from datetime import datetime as dt_parser
import datetime as dt_increaser

# Ondalıklı sayı çevrimi için kullanılan metot
def add_doc_on_value(value):
    if value[2:3] != '.':
        value = value[:2] + '.' + value[2:]
    return value

# Günler arasındaki farkları hesaplamak için kullanılan metot
def difference(dataset, interval=1):
    diff = list()
    for i in range(interval, len(dataset)):
        value = dataset[i] - dataset[i - interval]
        diff.append(value)
    return np.array(diff)

# Günler arasındaki farkları tersine çevirmek için kullanılan metot
def inverse_difference(history, yhat, interval=1):
    return yhat + history[-interval]

# 24 saat önceki tarih-zamanı hesaplayan metot
def before_24_hours():
    dt = dt_parser.now() - dt_increaser.timedelta(minutes=(24*60)-1)
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

# Ana metot çarılır
def main():
    # Spark içeriği oluşturulur ve veri seti okunur
    conf = SparkConf().setAppName("temperature_prediction")
    sc = SparkContext(conf=conf)
    sqlContext = sql.SQLContext(sc)
    df = sqlContext.read.csv("/home/burakcan/GraduateThesis/monthly_data.csv", header='true')

    # Spark veri çerçevesi, Pandas nesnesine çevrilir
    series = df.toPandas()
    # Veri setinin indisleri olarak zaman sütunundaki değerler atanır
    series.set_index(['time'], inplace=True)
    # Zaman serisindeki değerler alınır, test verisi seçilir, başlangıç-bitiş değerleri atanır
    X = [float(add_doc_on_value(str(x)[3:-2])) for x in series.values]

    # Günler arasındaki farklar bulunur
    days_in_year = 365
    differenced = difference(X, days_in_year)

    # Zaman serisi için model oluşturulur, eğitilir ve kaydedilir
    model = ARIMA(differenced, order=(7,0,1))
    model_fit = model.fit(disp=0)
    model_fit.save('/home/burakcan/GraduateThesis/arima_model.pkl')

# Ana metodun çalıştırılmasına yönelik bir koşul kontrolü
if __name__ == "__main__":
    main()