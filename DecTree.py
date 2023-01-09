import yfinance as yf
import datetime
import json
##
import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import matplotlib.pyplot as plt
# Package untuk mengevaluasi model ML dengan train/test split
from sklearn.model_selection import train_test_split
# Salah satu algoritma untuk machine learning
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_percentage_error
from sklearn.metrics import mean_absolute_error
from sklearn.tree import DecisionTreeRegressor


def dateInputValidation(date_string):
    date_format = '%Y-%m-%d'
    # using try-except blocks for handling the exceptions
    try:
        # formatting the date using strptime() function
        dateObject = datetime.datetime.strptime(date_string, date_format)
        return 200

        # If the date validation goes wrong
    except ValueError:
        # printing the appropriate text if ValueError occurs
        return 400


def setPrediction(request, symbol, tgl_awal, tgl_akhir):
    status = 200
    data = yf.download(symbol.upper(),
                       start=tgl_awal,
                       end=tgl_akhir,
                       progress=False)
    data["Date"] = data.index
    data = data[["Date", "Open", "High",
                 "Low", "Close", "Adj Close", "Volume"]]
    data.reset_index(drop=True, inplace=True)
    data.isnull().sum()
    data.shape
    data_set = data.dropna()
    data_set.isnull().sum()
    required = ["Open", "High", "Low"]
    # Kolom yang dijadikan nilai utama atau
    # output dalam menganalisis crypto
    output_label = "Close"
    # Set ke variabel
    x = data_set[required]
    y = data_set[output_label]
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, random_state=0)
    decTree = DecisionTreeRegressor()
    model = decTree.fit(x_train, y_train)
    model2 = decTree.fit(x_test, y_test)
    #
    # future_set_awal = data_set.tail(x_test.shape[0])
    # future_set = future_set_awal.iloc[::-1]
    future_set = data_set.tail(x_test.shape[0])
    y_pred = decTree.predict(future_set[required])
    data_pred = pd.DataFrame(y_pred, columns=['harga'])
    data_actual = pd.DataFrame(np.array(data[[output_label]].tail(x_test.shape[0])), columns=['harga'])
    
    data_to_pred_json = data_pred.to_json(orient='records')
    data_to_actual_json = data_actual.to_json(orient='records')
    data_decode_pred_json = json.loads(data_to_pred_json)
    data_decode_actual_json = json.loads(data_to_actual_json)
    #
    dataAwal = np.array(data_set[output_label].head(y_train.shape[0]))
    dataAwal = np.append(dataAwal, y_pred)
    data_harga = pd.DataFrame(dataAwal, columns=['data'])
    #
    dataAktual = np.array(data_set[output_label].head(y_train.shape[0]))
    dataAktual = np.append(dataAktual, future_set[output_label])
    data_aktual = pd.DataFrame(dataAktual, columns=['data'])
    valid = data_harga[y_train.shape[0]:]
    aktual = data_aktual[y_train.shape[0]:]
    dataTrend = data_harga[y_train.shape[0]:]
    data_to_pred_2_json = valid.to_json(orient='table')
    data_decode_pred_2_json = json.loads(data_to_pred_2_json)
    dataTrend["rolling_mean"] = dataTrend["data"].rolling(window=len(dataTrend.index)).mean()
    trend = "Stabil"
    if dataTrend["data"].iloc[-1] > dataTrend["rolling_mean"].iloc[-1]:
        trend = "Naik"
    elif dataTrend["data"].iloc[-1] < dataTrend["rolling_mean"].iloc[-1]:
        trend = "Turun"
    # print(dataTrend)
    #
    setPlot(symbol, data_set, aktual, valid, tgl_awal, tgl_akhir)

    data = scoreData(y_test, y_pred)

    return json.dumps({
        "model": "Decision Tree Regression",
        "symbol": symbol,
        "score": {
            "accuracyTestSet": decTree.score(x_test, y_test),
            "rmse": data['rmse'],
            "rmspe": data['rmspe'],
            "mape": data['mape'],
            "mae": data['mae'],
            "accuracyTrainSet": decTree.score(x_train, y_train),
        },
        "images": request.url_root + 'static/images/' + (symbol.upper() + '_' + tgl_awal + '_sd_' + tgl_akhir) + '.png',
        "prediksiData": data_decode_pred_json,
        "aktualData": data_decode_actual_json,
        "dataHari": data_decode_pred_2_json['data'],
        "status": status,
        "trend": trend
    })


def scoreData(y_test, y_pred):
    # Nilai RMSE (Root mean square error)
    rmse = float(format(np.sqrt(mean_squared_error(y_test, y_pred)), '.2f'))
    # Nilai RMSE (Root mean square percentage error)
    rmspe = float(format((np.sqrt(np.mean(np.square((y_test - y_pred) / y_test)))) * 100, '.2f'))
    # Nilai MAPE (Mean Absolute Percentage Error)
    mape = float(format(mean_absolute_percentage_error(y_test, y_pred) * 100, '.2f'))
    # Nilai MAE (Mean Absolute Error)
    mae = float(format(mean_absolute_error(y_test, y_pred), '.2f'))

    return {
        "rmse": rmse,
        "rmspe": rmspe,
        "mape": mape,
        "mae": mae
    }


def setPlot(symbol, data_set, aktual, valid, tgl_awal, tgl_akhir):
    plt.figure(figsize=(12, 5))
    plt.plot(data_set['Close'], label="Data Close Harga")
    plt.plot(aktual, label="Data Uji Harga")
    plt.plot(valid, label="Data Prediksi Harga")
    plt.title("Decision Tree Regresi Prediksi Harga " + symbol.upper())
    plt.ylabel('Harga')
    plt.xlabel('Hari')
    plt.legend(loc='best', fancybox=True, shadow=True)
    plt.grid(True)
    plt.tight_layout(pad=0.05)
    plt.savefig('./static/images/' + (symbol.upper() + '_' +
                tgl_awal + '_sd_' + tgl_akhir) + '.png')
