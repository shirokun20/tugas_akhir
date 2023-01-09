from flask import Flask, redirect, url_for, request, jsonify, render_template
# Model Decission Tree
from DecTree import dateInputValidation, setPrediction
#
from datetime import datetime as dt
import yfinance as yf
import json
app = Flask(__name__, static_url_path='/static')

menus = [{
    "name": "Regresi",
    "isActive": "",
    "link": ""
}, {
    "name": "Tentang Aplikasi",
    "isActive": "",
    "link": ""
}]


@app.route('/')
def index():
    menus[0]['isActive'] = 'active'
    menus[0]['link'] = request.url_root
    menus[1]['isActive'] = ''
    menus[1]['link'] = request.url_root + 'tentang-aplikasi'
    sysmbols = [
        {
            "label": "Bitcoin USD",
            "value": "BTC-USD"
        }, {
            "label": "Etherium USD",
            "value": "ETH-USD"
        }, {
            "label": "DOGE USD",
            "value": "DOGE-USD"
        }, {
            "label": "XRP USD",
            "value": "XRP-USD"
        }, {
            "label": "BNB USD",
            "value": "BNB-USD"
        }
    ]
    return render_template('index.html', menus=menus, sysmbols=sysmbols, len=len(sysmbols))


@app.route('/tentang-aplikasi')
def tentangAplikasi():
    menus[0]['isActive'] = ''
    menus[0]['link'] = request.url_root
    menus[1]['isActive'] = 'active'
    menus[1]['link'] = request.url_root + 'tentang-aplikasi'
    return render_template('tentang-aplikasi.html', menus=menus)


@app.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404


@app.post('/prediction')
def prediction():
    message = []
    status = 200
    if (request.method == "POST"):
        symbol = request.form.get('symbol')
        tgl_awal = request.form.get('tgl_awal')
        tgl_akhir = request.form.get('tgl_akhir')
        if (len(symbol) == 0):
            status = 400
            message.append("Simbol harus diisi!!")
        if (len(tgl_awal) == 0):
            status = 400
            message.append("Tanggal Awal harus diisi")
        if (len(tgl_akhir) == 0):
            status = 400
            message.append("Tanggal Akhir harus diisi")
        
        if (len(tgl_awal) and len(tgl_akhir)):
            if (dateInputValidation(tgl_awal) == 400 and len(tgl_awal) > 0):
                status = 400
                message.append("Tanggal Awal tidak valid")
            elif (dateInputValidation(tgl_akhir) == 400 and len(tgl_akhir) > 0):
                status = 400
                message.append("Tanggal Akhir tidak valid")
            else:
                date_format = '%Y-%m-%d'
                a = dt.strptime(tgl_awal, date_format)
                b = dt.strptime(tgl_akhir, date_format)
                dateToday = dt.today().strftime(date_format)
                dateToday = dt.strptime(dateToday, date_format)
                print(dateToday)
                # dateToday = dt.strptime(dateToday, date_format)
                c = dateToday
                delta = b - a
                if a > b:
                    status = 400
                    message.append(
                        "Tanggal Awal tidak boleh lebih besar dari Tanggal Akhir")
                elif b > c:
                    status = 400
                    message.append(
                        "Tanggal Akhir tidak boleh lebih dari Tanggal Hari Ini")
                elif a > c:
                    status = 400
                    message.append(
                        "Tanggal Awal tidak boleh lebih dari Tanggal Hari Ini")
                elif delta.days > 91: 
                    status = 400
                    message.append(
                        "Prediksi harus kurang dari 91 hari!")
                elif delta.days < 10: 
                    status = 400
                    message.append(
                        "Prediksi harus lebih dari 10 hari!")

    if (status == 200):
        data = yf.download(symbol.upper(),
                           start=tgl_awal,
                           end=tgl_akhir,
                           progress=False)
        if (data.empty):
            status = 400
            message.append("Data dengan symbol " +
                           symbol.upper() + " tidak ditemukan!")
            return app.response_class(
                response=json.dumps({
                    "message": message,
                    "status": status,
                }),
                status=status,
                mimetype='application/json'
            )
        else:
            response = setPrediction(request, symbol, tgl_awal, tgl_akhir)
            return app.response_class(
                response=response,
                status=200,
                mimetype='application/json'
            )
    else:
        return app.response_class(
            response=json.dumps({
                "message": message,
                "status": status,
            }),
            status=status,
            mimetype='application/json'
        )


if __name__ == '__main__':
    app.debug = True
    app.run()
