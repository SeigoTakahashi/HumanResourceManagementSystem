// 駅名候補を検索する関数
function fetchSuggestions(name, suggestions, input, hiddenCode) {
    const url = `https://mixway.ekispert.jp/v1/json/station/light?key=${mixwayKey}&name=${encodeURIComponent(name)}`;

    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            displaySuggestions(data.ResultSet.Point, suggestions, input, hiddenCode);
        })
        .catch(error => {
            console.error("Error:", error);
        });
}

// 駅名候補を出力する関数
function displaySuggestions(points, suggestions, input, hiddenCode) {
    clearSuggestions(suggestions);
    suggestions.classList.remove("custom-hidden");
    points.forEach(point => {
        const item = document.createElement('div');
        item.classList.add('suggestion-item');
        item.textContent = point.Station.Name;
        item.addEventListener('click', () => {
            input.value = point.Station.Name;
            hiddenCode.value = point.Station.code;
            clearSuggestions(suggestions);
        });
        suggestions.appendChild(item);
    });
}

// 駅名候補をクリアする関数
function clearSuggestions(suggestions) {
    suggestions.innerHTML = '';
    suggestions.classList.add("custom-hidden");
}

// 詳細条件を作成する関数
async function createConditionDetail() {
    // リクエストパラメータの作成
    const params = [
        `plane=${document.getElementById("plane").checked ? "normal" : "never"}`,
        `shinkansen=${document.getElementById("shinkansen").checked ? "normal" : "never"}`,
        `sleeperTrain=${document.getElementById("sleeperTrain").checked ? "normal" : "never"}`,
        `limitedExpress=${document.getElementById("limitedExpress").checked ? "normal" : "never"}`,
        `highwayBus=${document.getElementById("highwayBus").checked ? "normal" : "never"}`,
        `connectionBus=${document.getElementById("connectionBus").checked ? "normal" : "never"}`,
        `localBus=${document.getElementById("localBus").checked ? "normal" : "never"}`,
        `ship=${document.getElementById("ship").checked ? "normal" : "never"}`,
        `liner=${document.getElementById("liner").checked ? "normal" : "never"}`,
        `transferTime=${document.getElementById("transferTime").value}`,
        `surchargeKind=${document.getElementById("surchargeKind").value}`,
        `ticketSystemType=ic`,
        `preferredTicketOrder=${document.getElementById("preferredTicketOrder").value}`,
        `nikukanteiki=true`,

    ];
    const queryString = params.join("&");
    const url = `https://mixway.ekispert.jp/v1/json/toolbox/course/condition?key=${mixwayKey}&${queryString}`;
    console.log("conditionURL:" + url);

    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`${response.status}: ${response.statusText}`);
        }
        const data = await response.json();
        return data.ResultSet.Condition;
    } catch (error) {
        console.error("Error:", error);
        return null;
    }
}

// 経路を出力する関数
async function getRoute(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const res = await response.json();
        try {
            resultApp.setResult(JSON.stringify(res));
        } catch (ex) {
            console.error(ex);
            if (!inputFlag) {
                document.getElementById("missAlert").classList.remove("custom-hidden");
            }
            console.log('予期しないエラーが発生しました');
            errorFlag = true;
        }
    } catch (err) {
        console.error(err);
        if (!inputFlag) {
            document.getElementById("missAlert").classList.remove("custom-hidden");
        }
        console.log('サーバに接続できないか、またはレスポンスが不正な形式でした');
        errorFlag = true;
    }
}

// 経由駅を増加させる関数
function showNextViaField(index) {
    document.getElementById(`via${index}InputGroup`).classList.remove("custom-hidden");
    document.querySelector(`#via${index}InputGroup .custom-plus-icon`).classList.add("custom-hidden");

    const nextIndex = index + 1;

    if (nextIndex <= 3) {
        document.getElementById(`via${nextIndex}InputGroup`).classList.remove("custom-hidden");
        document.querySelector(`#via${nextIndex}InputGroup .custom-plus-icon`).classList.add("custom-show");
    }
}

// 住所から最寄駅を取得
async function getNearestStation(type) {
    const address = document.getElementById("address").value;

    let url = `https://api.ekispert.jp/v1/json/address/station?key=${mixwayKey}&address=${address}&type=${type}`


    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const res = await response.json();

        try {
            let name = res.ResultSet.Point.Station.Name;
            let code = res.ResultSet.Point.Station.code;
            return { name: name, code: code };
        } catch (ex) {
            console.log('予期しないエラーが発生しました');
        }
    } catch (err) {
        console.error(err);
    }
}

// 定期券代用経路検索
async function searchTeikiRoute() {
    let url = `https://mixway.ekispert.jp/v1/json/search/course/extreme?key=${mixwayKey}`

    // リクエストパラメータの生成
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

    // searchType
    let searchType = "&searchType=plain"
    url += searchType

    // sort
    let sort = "&sort=price"
    url += sort

    // addChange
    url += "&addChange=true"

    // priceType
    resultApp.setPriceType(resultApp.PRICE_TEIKI);

    console.log("最終的なURL:", url);
    await getRoute(url);
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
    if (!errorFlag && !inputFlag) {
        document.getElementById("result").classList.remove("custom-hidden");
    }
}