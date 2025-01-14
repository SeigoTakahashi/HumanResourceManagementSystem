// 初期設定
document.addEventListener("DOMContentLoaded", function () {
    // 定期券代用検索の場合
    document.getElementById("detailSetting").classList.add("custom-hidden");
    document.getElementById("detailSettingButton").classList.add("custom-hidden");
    document.getElementById("searchTypeDiv").classList.add("custom-hidden");
    document.getElementById("swapButton").classList.add("custom-hidden");
    document.getElementById("viaArea").classList.add("custom-hidden");

    // 次の4月1日に設定
    let now = new Date()
    let targetMonth = 3 // 4月は3(0-based)
    let year = now.getMonth() > targetMonth ? now.getFullYear() + 1 : now.getFullYear()
    let month = "04"
    let day = "01"
    document.getElementById("yearSelect").value = year
    document.getElementById("monthSelect").value = month
    document.getElementById("daySelect").value = day
    document.getElementById("hourSelect").value = "00"
    document.getElementById("minuteSelect").value = "00"


    // 経路検索モーダルの開閉イベント
    document.getElementById("searchRouteModalOpen")?.addEventListener("click", async function () {
        // 交通手段を設定
        courseType = "train";
        // モーダルタイトルを設定
        document.getElementById("routeSearchModalTitle").innerHTML = "<i class='fa fa-train me-2' aria-hidden='true'></i><u>経路検索</u>";

        // 経路検索結果をクリア
        document.getElementById('result').classList.add("custom-hidden");

        // マップエリアをクリア
        const mapArea = document.getElementById('mapArea');
        mapArea.classList.add("custom-hidden");

        // 地図データを完全にクリア
        if (map) {
            // データレイヤーをクリア
            if (map.data) {
                map.data.forEach(feature => map.data.remove(feature));
            }
        }
        // 経路選択ボタンをクリア
        document.getElementById("routeSelectArea").classList.add("custom-hidden");

        // 到着駅を固定
        document.getElementById("arrivalInput").value = "東陽町";
        document.getElementById("arrivalCode").value = "22830";
        document.getElementById("arrivalInput").readOnly = true;

        // 出発駅を取得
        if (document.getElementById("address").value) {
            let nearestStation = await getNearestStation("train");
            document.getElementById("departureInput").value = nearestStation.name;
            document.getElementById("departureCode").value = nearestStation.code;
        }

        // 経路検索モーダルを表示
        $('#routeSearchModal').modal('show');

    });

    // バス経路検索モーダルの開閉イベント
    document.getElementById("searchBusRouteModalOpen")?.addEventListener("click", async function () {
        // 交通手段を設定
        courseType = "bus";
        // モーダルタイトルを設定
        document.getElementById("routeSearchModalTitle").innerHTML = "<i class='fa fa-bus me-2' aria-hidden='true'></i><u>バス経路検索</u>";

        // 経路検索結果をクリア
        document.getElementById('result').classList.add("custom-hidden");

        // マップエリアをクリア
        const mapArea = document.getElementById('mapArea');
        mapArea.classList.add("custom-hidden");

        // 地図データを完全にクリア
        if (map) {
            // データレイヤーをクリア
            if (map.data) {
                map.data.forEach(feature => map.data.remove(feature));
            }
            // 地図を再初期化
            initMap();
        }

        // 経路選択ボタンをクリア
        document.getElementById("routeSelectArea").classList.add("custom-hidden");

        // 出発バス停を取得
        if (document.getElementById("address").value) {
            let nearestBusStop = await getNearestStation("bus");
            document.getElementById("departureInput").value = nearestBusStop.name;
            document.getElementById("departureCode").value = nearestBusStop.code;
        }

        // 到着駅を取得
        if (document.getElementById("address").value) {
            let nearestStation = await getNearestStation("train");
            document.getElementById("arrivalInput").value = nearestStation.name;
            document.getElementById("arrivalCode").value = nearestStation.code;
            document.getElementById("arrivalInput").readOnly = false;
        }

        // 経路検索モーダルを表示
        $('#routeSearchModal').modal('show');
    });


    // モーダルが閉じられたときにマップエリアを非表示にする
    $('#routeSearchModal').on('hidden.bs.modal', function () {
        document.getElementById('mapArea').classList.add("custom-hidden");
        // 経路探索後にフラグをリセット
        isInitialLoad = true;
    });

    // 経路検索ボタンのクリックイベント
    document.getElementById("searchButton")?.addEventListener("click", async function () {
        const mapArea = document.getElementById('mapArea');
        mapArea.classList.remove("custom-hidden");
        // 地図データを完全にクリア
        if (map) {
            // データレイヤーをクリア
            if (map.data) {
                map.data.forEach(feature => map.data.remove(feature));
            }
            // 地図を再初期化
            initMap();
        }

        document.getElementById("routeSelectArea").classList.remove("custom-hidden");

        await searchTeikiRoute();
        await navitimeCreateGeojson();
    });

    // 経路選択ボタンのクリックイベント
    document.getElementById("selectRouteBtn")?.addEventListener("click", function () {
        let displayRoute = "";
        const resultSetAll = resultApp.getResultAll().ResultSet;
        const resultSet = resultApp.getResult().ResultSet;
        const route = resultApp.getResult().ResultSet.Course.Route;
        const price = resultApp.getResult().ResultSet.Course.Price;
        const line = route.Line;
        const points = route.Point;
        displayRoute += points[0].Station.Name;
        for (let i = 1; i < points.length; i++) {
            displayRoute += " -- (" + line[i - 1].Name + ") -- " + points[i].Station.Name;
        }
        if (courseType === "bus") {
            document.getElementById("busRouteInputArea").classList.remove("custom-hidden");
            document.getElementById("busRoute").value = displayRoute;
            document.getElementById("busRouteJson").value = JSON.stringify(resultSet);
        } else {
            document.getElementById("routeInputArea").classList.remove("custom-hidden");
            document.getElementById("commuteRoute").value = displayRoute;
            document.getElementById("routeJson").value = JSON.stringify(resultSet);
            console.log(resultSetAll);
            document.getElementById("economicRouteJson").value = JSON.stringify(resultSetAll.Course[0]);
        }

        // 定期券料金のサマリーを取得
        const teiki1Summary = price.find(p => p.kind === "Teiki1Summary");
        const teiki3Summary = price.find(p => p.kind === "Teiki3Summary");
        const teiki6Summary = price.find(p => p.kind === "Teiki6Summary");

        // 料金情報を表示
        // 料金情報のHTML要素を作成
        const priceInfoDiv = document.createElement('div');
        priceInfoDiv.classList.add('mb-3');

        const priceLabel = document.createElement('label');
        priceLabel.textContent = '定期券料金:';
        priceInfoDiv.appendChild(priceLabel);

        const teiki1Label = document.createElement('label');
        teiki1Label.innerHTML = `1ヶ月: <u>${Number(teiki1Summary.Oneway).toLocaleString()}円</u>`;
        priceInfoDiv.appendChild(teiki1Label);

        const teiki3Label = document.createElement('label');
        teiki3Label.innerHTML = `3ヶ月: <u>${Number(teiki3Summary.Oneway).toLocaleString()}円</u>`;
        priceInfoDiv.appendChild(teiki3Label);

        const teiki6Label = document.createElement('label');
        teiki6Label.innerHTML = `6ヶ月: <u>${Number(teiki6Summary.Oneway).toLocaleString()}円</u>`;
        priceInfoDiv.appendChild(teiki6Label);

        if (courseType === "bus") {
            document.getElementById("busPriceArea").innerHTML = "";
            document.getElementById("busPriceArea").appendChild(priceInfoDiv);
        } else {
            document.getElementById("trainPriceArea").innerHTML = "";
            document.getElementById("trainPriceArea").appendChild(priceInfoDiv);
        }

        let commutingExpenses = Number(document.getElementById("commutingExpenses").value);
        document.getElementById("commutingExpenses").value = commutingExpenses + Number(teiki6Summary.Oneway);


        $('#routeSearchModal').modal('hide');
        // マップエリアを非表示にする
        document.getElementById('mapArea').classList.add("custom-hidden");
        // 経路結果エリアを非表示にする
        document.getElementById('result').classList.add("custom-hidden");
        // 経路選択エリアを非表示にする
        document.getElementById('routeSelectArea').classList.add("custom-hidden");
    });

    // 交通手段ラジオボタンの変更イベントリスナー
    document.querySelectorAll('input[name="transportation_type"]').forEach(radio => {
        radio.addEventListener('change', function () {
            const busRouteInputAreaDiv = document.getElementById('busRouteInputAreaDiv');

            if (this.value === 'bus') {
                // バスが選択された場合
                busRouteInputAreaDiv.classList.remove("custom-hidden");
            } else {
                // バス以外が選択された場合
                busRouteInputAreaDiv.classList.add("custom-hidden");
            }
        });
    });

    document.getElementById("isBicycleCommute")?.addEventListener("change", function () {
        if (this.checked) {
            document.getElementById("train_input_area").classList.add("custom-hidden");
        } else {
            document.getElementById("train_input_area").classList.remove("custom-hidden");
        }
    });
});