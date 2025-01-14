const googlemapKey = "AIzaSyCglk4ny3wrgqG3MJSOstihm3IdmkonWBY";
// const navitimeKey = "8413f244e9msh96e01721d5e8eb2p140ca8jsnd06d06623047";
const navitimeKey = "0a82fd92c2msh87b55dff90321ffp159b6ajsnc597536ba1ab";
let map;

// マップの初期化
function initMap() {
    if(document.getElementById("mapArea")) {
        map = new google.maps.Map(document.getElementById("mapArea"), {
            zoom: 7,
            center: new google.maps.LatLng(36, 138),
            mapTypeId: google.maps.MapTypeId.ROADMAP
        });
    }
}

// Google Map Load
function loadGoogleMapsScript() {
    const script = document.createElement("script");
    script.src = `https://maps.googleapis.com/maps/api/js?key=${googlemapKey}&callback=initMap`;
    script.defer = true;
    document.head.appendChild(script);
}
loadGoogleMapsScript();

// NAVITIME APIを使用し、geoJSONを生成する関数
async function navitimeCreateGeojson() {
    try {
        // マップを初期化
        if (map) {
            if (map.data) {
                map.data.forEach(function (feature) {
                    map.data.remove(feature);
                });
            }
        }
        console.log(resultApp.getResult());
        if(!resultApp.getResult()){ 
            return;
        }

        let course = resultApp.getResult().ResultSet.Course;
        const route = course.Route;

        // Point 情報から coordinates 配列を作成
        const via = route.Point.map(point => [{
            "lat": point.GeoPoint.lati_d,
            "lon": point.GeoPoint.longi_d,
        }]);

        let url = "https://navitime-route-totalnavi.p.rapidapi.com/route_transit?"

        // パラメータの設定
        const start = via[0];
        const goal = via[via.length - 1];
        const viaPoints = via.slice(1, -1);
        const start_time = new Date().toISOString();

        url += `start={"lat":${start[0].lat},"lon":${start[0].lon}}`;
        url += `&goal={"lat":${goal[0].lat},"lon":${goal[0].lon}}`;

        if (viaPoints.length > 0) {
            url += `&via=[${viaPoints.map(point => `{"lat":${point[0].lat},"lon":${point[0].lon}}`).join(',')}]`;
        }

        const formattedStartTime = start_time.substring(0, 19);
        url += `&start_time=${formattedStartTime}&shape=true`;

        const options = {
            method: 'GET',
            headers: {
                'x-rapidapi-key': navitimeKey,
                'x-rapidapi-host': 'navitime-route-totalnavi.p.rapidapi.com'
            }
        };

        const response = await fetch(url, options);
        const data = await response.json();

        console.log(data);
        // マップ表示
        initMap();
        map.data.addGeoJson(data.items[0].shapes);

        // スタイル設定
        map.data.setStyle(function (feature) {
            const inline = feature.getProperty('inline');
            return {
                strokeColor: inline.color,
                strokeWeight: inline.width,
                strokeOpacity: inline.opacity,
                strokeLineCap: inline.strokelinecap,
                strokeLineJoin: inline.strokelinejoin,
            };
        });

        // 地図の範囲を設定
        const bbox = data.items[0].shapes.bbox;
        if (bbox && bbox.length === 4) {
            const bounds = new google.maps.LatLngBounds(
                new google.maps.LatLng(bbox[1], bbox[0]),
                new google.maps.LatLng(bbox[3], bbox[2])
            );
            map.fitBounds(bounds);

        }

    } catch (error) {
        console.error('エラーが発生しました:', error);
        document.getElementById('result').innerHTML = '<p>経路情報の取得に失敗しました。</p>';
    }
}
