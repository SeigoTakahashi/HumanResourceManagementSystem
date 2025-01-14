document.addEventListener('DOMContentLoaded', function () {
    // 通勤経路
    const openCommuteRouteModalBtn = document.getElementById('openCommuteRouteModalBtn');
    const commuteRouteCopyList = document.getElementById('commuteRouteCopyList');
    const commuteRouteElement = document.getElementById('commute_route');
    let commuteRoute = '';
    if (commuteRouteElement) {
        commuteRoute = commuteRouteElement.value;
    }
    

    // バス経路
    const openBusRouteModalBtn = document.getElementById('openBusRouteModalBtn');
    const busRouteCopyList = document.getElementById('busRouteCopyList');
    const busRouteElement = document.getElementById('bus_route');
    let busRoute = '';
    if (busRouteElement) {
        busRoute = busRouteElement.value;
    }

    const clipboard = new ClipboardJS('.copy-btn');

    // Clipboard.jsの初期化
    clipboard.on('success', function (e) {
        navigator.clipboard.writeText(e.text);
        Swal.fire({
            text:"クリップボードにコピーしました", 
            timer: 3000,
            showConfirmButton: false,
            position: 'bottom',
        });
    }).on('error', function (e) {
        Swal.fire({
            text:"クリップボードにコピーに失敗しました", 
            timer: 3000,
            showConfirmButton: false,
            position: 'bottom',
        });
    });

    // 通勤経路コピーモーダルボタンのクリックイベント
    openCommuteRouteModalBtn?.addEventListener('click', function () {
        // 通勤経路のデータを取得してハイフンで区切る
        const commuteRoutes = commuteRoute.split(' -- ');
        
        // モーダルに通勤経路のコピーリストを表示
        commuteRouteCopyList.innerHTML = commuteRoutes.map(route => `
            <div class="d-flex justify-content-between mb-2">
                <span>${route.trim()}</span>
                <button class="btn btn-outline-primary btn-sm copy-btn" data-clipboard-text="${route.trim()}">Copy</button>
            </div>
        `).join('');
        
        // モーダルを表示
        $('#commuteRouteModal').modal('show');
        
        
    });

    
    // バス経路コピーモーダルボタンのクリックイベント
    openBusRouteModalBtn?.addEventListener('click', function () {
        // バス経路のデータを取得してハイフンで区切る
        const busRoutes = busRoute.split(' -- ');
        
        // モーダルにバス経路のコピーリストを表示
        busRouteCopyList.innerHTML = busRoutes.map(route => `
            <div class="d-flex justify-content-between mb-2">
                <span>${route.trim()}</span>
                <button class="btn btn-outline-primary btn-sm copy-btn" data-clipboard-text="${route.trim()}">Copy</button>
            </div>
        `).join('');
        
        // モーダルを表示
        $('#busRouteModal').modal('show');
        
    });

    
    
});