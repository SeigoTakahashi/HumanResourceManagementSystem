document.addEventListener('DOMContentLoaded', function() {
    // 次の4月1日に設定
    let now = new Date()
    let targetMonth = 3 // 4月は3(0-based)
    let year = now.getMonth() > targetMonth ? now.getFullYear() + 1 : now.getFullYear()
    let month = "04"
    let day = "01"
    document.getElementById("applicationDate").value = year + "-" + month + "-" + day

    // 社員番号をユーザーIDで設定
    const userId = document.getElementById("userId").value
    document.getElementById("employeeNumber").value = userId

    // 所属部署を設定（内定者だったら新入社員）
    const employee_type = document.getElementById("employee_type").value
    if (employee_type === "内定者") {
        document.getElementById("affiliation").value = "新入社員"
    } 

    // 支給額計を非表示にする
    document.getElementById("amountArea").style.display = "none"
});