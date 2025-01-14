const mixwayKey = "test_QMMh4JZJgnC";
let resultApp;
let errorFlag;
let inputFlag;
let isInitialLoad = true;

document.addEventListener("DOMContentLoaded", function () {
    // resultAppの生成
    if (document.getElementById('result')) {
        resultApp = new expGuiCourse(document.getElementById('result'));

        // タブ切り替えイベントのリスナーを追加
        resultApp.bind('change', async function (type, index) {
            // 確認書画面の場合のみ実行
            if (window.location.pathname.includes('confirmation')) {
                // 経済路線の推奨
                if (resultApp.getSelectNo() == 1) {
                    // 新しい要素を作成
                    var newElement = document.createElement('div');
                    newElement.id = 'recommend';
                    newElement.textContent = '※こちらの経路が推奨路線です。';
                    newElement.style.color = 'green';
                    newElement.style.textAlign = 'center';
                    newElement.style.marginTop = '10px';

                    // headerの後、bodyの前に新しい要素を挿入
                    var header = document.getElementById('result:result:header');
                    var body = document.getElementById('result:result:body');
                    header.parentNode.insertBefore(newElement, body);
                } else {
                    // 推奨路線テキストの削除
                    var recommend = document.getElementById('recommend');
                    if (recommend) {
                        recommend.parentNode.removeChild(recommend);
                    }
                };

                // 初回読み込み時はスキップ
                if (isInitialLoad) {
                    isInitialLoad = false;
                    return;
                }

                // マップエリアを表示
                const mapArea = document.getElementById('mapArea');
                if (mapArea && !mapArea.classList.contains("custom-hidden")) {
                    if (map) {
                        if (map.data) {
                            map.data.forEach(function (feature) {
                                map.data.remove(feature);
                            });
                        }
                    }
                    initMap();
                    await navitimeCreateGeojson();
                }
            }
        });
    }



    // 日付プルダウンの生成
    // 各要素の取得
    const yearSelect = document.getElementById('yearSelect');
    const monthSelect = document.getElementById('monthSelect');
    const daySelect = document.getElementById('daySelect');
    const hourSelect = document.getElementById('hourSelect');
    const minuteSelect = document.getElementById('minuteSelect');

    // 現在の日時を取得
    const now = new Date();
    const currentYear = now.getFullYear();
    const currentMonth = now.getMonth() + 1; // getMonth()は0から始まるため+1
    const currentDate = now.getDate();
    const currentHour = now.getHours();
    const currentMinute = now.getMinutes()

    // 年のプルダウンを生成
    for (let year = currentYear - 1; year <= currentYear + 1; year++) {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year + '年';
        if (yearSelect) {
            yearSelect.appendChild(option);
        }
    }
    if (yearSelect) {
        yearSelect.value = currentYear; // 現在の年を初期値に設定
    }
    

    // 月のプルダウンを生成
    for (let month = 1; month <= 12; month++) {
        const option = document.createElement('option');
        option.value = (month < 10 ? '0' : '') + month;
        option.textContent = month + '月';
        if (monthSelect) {
            monthSelect.appendChild(option);
        }
    }
    if (monthSelect) {
        monthSelect.value = (currentMonth < 10 ? '0' : '') + currentMonth; // 現在の月を初期値に設定
    }

    // 日のプルダウンを生成
    function updateDays() {
        if (!yearSelect || !monthSelect || !daySelect) {
            return;
        }
        const selectedYear = yearSelect.value;
        const selectedMonth = monthSelect.value;

        // 日数をクリア
        daySelect.innerHTML = '';

        // 選択された年と月に基づいて日数を計算
        const daysInMonth = new Date(selectedYear, selectedMonth, 0).getDate();
        for (let day = 1; day <= daysInMonth; day++) {
            const option = document.createElement('option');
            option.value = (day < 10 ? '0' : '') + day;
            option.textContent = day + '日';
            daySelect.appendChild(option);
        }
    }

    // 年と月が変更されたときに日を更新
    if (yearSelect) {
        yearSelect.addEventListener('change', updateDays);
    }
    if (monthSelect) {
        monthSelect.addEventListener('change', updateDays);
    }

    // 初回ロード時に日を更新
    updateDays();
    if (daySelect) {
        daySelect.value = (currentDate < 10 ? '0' : '') + currentDate; // 現在の日を初期値に設定
    }

    // 時のプルダウンを生成
    for (let hour = 0; hour < 24; hour++) {
        const option = document.createElement('option');
        option.value = (hour < 10 ? '0' : '') + hour;
        option.textContent = hour + '時';
        if (hourSelect) {
            hourSelect.appendChild(option);
        }
    }
    if (hourSelect) {
        hourSelect.value = (currentHour < 10 ? '0' : '') + currentHour; // 現在の時を初期値に設定
    }

    // 分のプルダウンを生成
    for (let minute = 0; minute < 60; minute++) {
        const option = document.createElement('option');
        option.value = (minute < 10 ? '0' : '') + minute;
        option.textContent = minute + '分';
        if (minuteSelect) {
            minuteSelect.appendChild(option);
        }
    }
    if (minuteSelect) {
        minuteSelect.value = (currentMinute < 10 ? '0' : '') + currentMinute; // 現在の分を初期値に設定
    }

    // 詳細設定の開閉イベント
    document.getElementById("detailSettingButton")?.addEventListener("click", () => {
        let detailSetting = document.getElementById("detailSetting")
        detailSetting.classList.toggle("detail-show");
    })

    // 出発・到着の入れ替えイベント
    document.getElementById("swapButton")?.addEventListener("click", () => {
        let departureInput = document.getElementById("departureInput")
        let arrivalInput = document.getElementById("arrivalInput")
        let departureValue = departureInput.value
        let arrivalValue = arrivalInput.value
        let departureCode = document.getElementById("departureCode").value
        let arrivalCode = document.getElementById("arrivalCode").value
        departureInput.value = arrivalValue
        arrivalInput.value = departureValue
        departureCode.value = arrivalCode
        arrivalCode.value = departureCode
    })

    // 駅名候補出力イベント
    document.querySelectorAll('.stationInput').forEach(input => {
        input.addEventListener('input', () => {
            const name = input.value.trim();
            const hiddenCode = input.parentNode.parentNode.querySelector('.hiddenInput');
            const suggestions = input.parentNode.parentNode.querySelector('.suggestions');

            if (name.length > 0) {
                fetchSuggestions(name, suggestions, input, hiddenCode);
            } else {
                clearSuggestions(suggestions);
            }
        });
    });


    // 経路検索イベント
    document.getElementById("searchButton")?.addEventListener("click", async () => {
        // 確認書の場合は処理を中断
        if (window.location.pathname.includes('confirmation')) {
            return;
        }

        errorFlag = false;
        inputFlag = false;
        let url = `https://mixway.ekispert.jp/v1/json/search/course/extreme?key=${mixwayKey}`

        // リクエストパラメータの作成
        // viaList
        let viaList = "&viaList="
        let departureCode = document.getElementById("departureCode").value
        let departureInput = document.getElementById("departureInput").value
        if (departureInput == "") {
            document.getElementById("departureAlert").classList.remove("custom-hidden");
            inputFlag = true;
        }
        viaList += departureCode
        if (document.getElementById("via1Code").value) {
            let via1Code = document.getElementById("via1Code").value
            viaList += ":" + via1Code
        }
        if (document.getElementById("via2Code").value) {
            let via2Code = document.getElementById("via2Code").value
            viaList += ":" + via2Code
        }
        if (document.getElementById("via3Code").value) {
            let via3Code = document.getElementById("via3Code").value
            viaList += ":" + via3Code
        }
        let arrivalCode = document.getElementById("arrivalCode").value
        let arrivalInput = document.getElementById("arrivalInput").value
        if (arrivalInput == "") {
            document.getElementById("arrivalAlert").classList.remove("custom-hidden");
            inputFlag = true;
        }
        viaList += ":" + arrivalCode
        url += viaList

        // date
        let date = "&date="
        let year = document.getElementById("yearSelect").value
        let month = document.getElementById("monthSelect").value
        let day = document.getElementById("daySelect").value
        date += year + month + day
        url += date

        //time
        let time = "&time="
        let hour = document.getElementById("hourSelect").value
        let minute = document.getElementById("minuteSelect").value
        time += hour + minute
        url += time

        // searchType
        let searchType = "&searchType=";
        let SelectSearchType = document.querySelector('input[name="searchType"]:checked').value;
        searchType += SelectSearchType
        url += searchType

        // priceType
        let priceType = document.getElementById("priceType").value
        if (priceType == "oneway") {
            resultApp.setPriceType(resultApp.PRICE_ONEWAY);
        } else if (priceType == "round") {
            resultApp.setPriceType(resultApp.PRICE_ROUND);
        } else if (priceType == "teiki") {
            resultApp.setPriceType(resultApp.PRICE_TEIKI);
        }

        // sort
        let sort = "&sort="
        let sortType = document.getElementById("sortType").value
        sort += sortType
        url += sort

        // addChange
        url += "&addChange=true"

        // conditionDetail
        let conditionDetail = "&conditionDetail="
        conditionDetail += await createConditionDetail();
        if (conditionDetail) {
            url += conditionDetail;
        } else {
            console.error("条件詳細が取得できませんでした。");
        }

        console.log("最終的なURL:", url);
        await getRoute(url);
        if (!errorFlag && !inputFlag) {
            document.getElementById("result").classList.remove("custom-hidden");
            document.getElementById("displayMapButtonDiv").classList.remove("custom-hidden");
        }
    })

    // 経路図表示イベント
    document.getElementById("displayMapButton")?.addEventListener("click", async function () {
        if (!resultApp.getViewCourseListFlag()) {
            $('#mapModal').modal("show");
            initMap();
            await navitimeCreateGeojson();
        }

    });

});





