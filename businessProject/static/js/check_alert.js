document.addEventListener('DOMContentLoaded', function () {
    const actionForm = document.getElementById('actionForm');
    const actionButtons = document.querySelectorAll('.action-button');
    const action = document.getElementById('action');

    // 各ボタンにイベントを設定
    actionButtons.forEach(button => {
        button.addEventListener('click', function () {
            if (this.value === 'approve') {
                Swal.fire({
                    title: "確認",
                    text: "この申請を承認しますか？",
                    icon: "warning",
                    showCancelButton: true,
                    confirmButtonColor: "#007BFF",
                }).then((result) => {
                    if (result.isConfirmed) {
                        Swal.fire({
                            text:"承認しました", 
                            confirmButtonColor: "#007BFF",
                            icon: "success",

                        }).then((result) => {
                            if (result.isConfirmed) {
                                action.value = this.value;
                                actionForm.submit();
                            }
                        }); 
                    } 
                });  
            } else {
                Swal.fire({
                    title: "確認",
                    text: "この申請を差し戻しますか？",
                    icon: "warning",
                    showCancelButton: true,
                    confirmButtonColor: "#007BFF",
                }).then((result) => {
                    if (result.isConfirmed) {
                        Swal.fire({
                            text:"差し戻しました", 
                            confirmButtonColor: "#007BFF",
                            icon: "success",

                        }).then((result) => {
                            if (result.isConfirmed) {
                                action.value = this.value;
                                actionForm.submit();
                            }
                        });
                    }
                }); 
            }
            
        });
    });

});