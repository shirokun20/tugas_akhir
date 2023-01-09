var dForm = $('#form'),
    btnPrediksi = $('#btnPrediksi'),
    cAlertMsg = $('#alertMsg'),
    cDataCardBody = $('#dataCardBody'),
    cTanggal = $('#tanggal'),
    cCard = $('#card'),
    tglA = $('[name="tgl_awal"]'),
    tglB = $('[name="tgl_akhir"]'),
    url = location.href,
    dataActualLast = 0,
    dataPredLast = 0

dForm.on({
    submit: () => {
        setBtn('Tunggu Sebentar!!', 'danger')
        cAlertMsg
            .slideUp('slow')
        cCard
            .slideUp('slow')
        cDataCardBody
            .html("")
        getData()
        return false;
    }
})

var clearBtn = () => {
    setTimeout(() => setBtn('Prediksi'), 2000)
}

var parseDate = (value) => {
    var myDate = new Date(value)
    var date = myDate.getDate()
    var month = myDate.getMonth()
    var year = myDate.getFullYear()
    return `${date}/${month}/${year}`
}

var getData = () => {
    $.ajax({
        url: url + '/prediction',
        type: "POST",
        dataType: "JSON",
        data: dForm.serialize()
    }).done((response) => {
        var { images, symbol, score, prediksiData, aktualData, trend, dataHari } = response
        setBtn('Yeah Berhasil!!', 'success')
        var output = ""
        output += "<div>"
        output += `<a href="${images}" target="_blank">`
        output += `<img src="${images}" class="img-responsive" width="100%">`
        output += "</a>"
        output += "</div>"
        output += "<hr>"
        output += `<table width="100%">`
        output += `<tr>`
        output += `<th>`
        output += `Simbol: ${symbol}`
        output += `</th>`
        output += `<th style="text-align:center !important">`
        output += `Trend: ${trend}`
        output += `</th>`
        output += `<th style="text-align:center !important">`
        output += `RMSE: ${score.rmse}`
        output += `</th>`
        output += `<th style="text-align:right !important">`
        output += `MAPE: ${score.mape}%`
        output += `</th>`
        output += `</tr>`
        output += `</table>`
        output += "<hr>"
        output += `<div class="row">`
        output += `<div class="col-md-6">`
        output += `<table class="table table-bordered" width="100%">`
        output += `<thead>`
        output += `<tr>`
        output += `<th style="text-align:center !important">`
        output += `Hari`
        output += `</th>`
        output += `<th style="text-align:center !important">`
        output += `Harga Prediksi`
        output += `</th>`
        output += `<th style="text-align:center !important">`
        output += `Harga Aktual`
        output += `</th>`
        output += `</tr>`
        output += `</thead>`
        output += `<tbody>`
        for (let index = 0; index < prediksiData.length; index++) {
            output += `<tr>`
                output += `<td>`
                output += parseInt(dataHari[index].index) + 1
                output += `</td>`
                output += `<td>`
                output += prediksiData[index].harga
                output += `</td>`
                output += `<td>`
                output += aktualData[index].harga
                output += `</td>`
            output += `</tr>`
            if (index + 1 == prediksiData) {
                dataActualLast = aktualData[index].harga
                dataPredLast = prediksiData[index].harga
            }
        }
        output += `</tbody>`
        output += `</table>`
        output += `</div>`
        output += `<div class="col-md-6">`
        output += `<h2 class="mb-4">`
        output += "Disclaimer"
        output += "</h2>"
        output += "<p>"
        output += "Aplikasi ini dibuat sebagai alat bantu untuk memutuskan beli dan jual crypto ataupun hold untuk jangka waktu tertentu, dengan murni dari hitungan nilai kuantitatif dan machine learning"
        output += "</p>"
        output += `</div>`
        output += `</div>`
        cDataCardBody
            .html(output)
        cTanggal
            .text(`${parseDate(tglA.val())} - ${parseDate(tglB.val())}`)
        cCard
            .slideDown('slow')
        clearBtn()
    }).fail((e) => {
        var { responseJSON } = e
        if (responseJSON.status == 400) {
            setTimeout(() => {
                setBtn('Yah ada error!!', 'warning')
                var text = ""
                var index = 1
                responseJSON.message.map((value) => {
                    text += `${value}`
                    text += responseJSON.message.length != index ? "<br>" : ""
                    index++
                })
                console.log(text)
                cAlertMsg
                    .slideDown('slow')
                    .html(text)
                clearBtn()
            }, 1000)
        }
    })

}

const setBtn = (text, type) => {
    btnPrediksi
        .val(text)
        .prop("class", `btn btn-${type ?? 'primary'}`)
}