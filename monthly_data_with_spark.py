# coding: utf-8

# Büyük veri analizi için kullanılan kütüphaneler
from pyspark import sql, SparkConf, SparkContext
# Çağırılan harici dosya
import monthly_datetime

# Ana metot
def main():
    conf = SparkConf().setAppName("special_values")
    sc = SparkContext(conf=conf)
    sqlContext = sql.SQLContext(sc)
    df = sqlContext.read.csv("/home/burakcan/GraduateThesis/temperature_data.csv", header='true')
    df = df.where(df["time"] >= monthly_datetime.get())
    df = df.toPandas()
    df.to_csv("/home/burakcan/GraduateThesis/monthly_data.csv", columns=['time', 'temp'], index=False)

# Ana metodun çalıştırılmasına yönelik bir koşul kontrolü
if __name__ == "__main__":
    main()