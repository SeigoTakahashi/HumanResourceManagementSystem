document.addEventListener('DOMContentLoaded', function() {
    // メッセージアイテムのクリックイベント
    const messageItems = document.querySelectorAll('.message-item');
    
    messageItems.forEach(item => {
        item.addEventListener('click', function() {
            const messageId = this.dataset.messageId;
            const sender = this.querySelector('h5').textContent;
            const timestamp = this.querySelector('small').textContent;
            const content = this.querySelector('p').textContent;

            // モーダルに情報をセット
            document.getElementById('modalMessageSender').textContent = `送信者: ${sender}`;
            document.getElementById('modalMessageTimestamp').textContent = `日時: ${timestamp}`;
            document.getElementById('modalMessageContent').textContent = content;

            // 未読の場合、既読にする
            if (this.classList.contains('unread-message')) {
                fetch(`/message/mark_as_read/${messageId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCSRFToken(),
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        this.classList.remove('unread-message');
                        const badge = this.querySelector('.badge');
                        if (badge) badge.remove();
                    }
                });
            }

            // モーダル表示
            $('#messageDetailModal').modal('show');
        });
    });
});

// CSRFトークンをクッキーから取得する関数
function getCSRFToken() {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
    return cookieValue || '';
}