var pageNo = document.getElementsByClassName("page_no");
var d_amount = document.getElementById("data_amount");

var amount = d_amount.textContent;
console.log(amount);

amount = Number(amount);
amount = Math.trunc(amount / 10) + 1;
console.log(amount)
console.log(pageNo[1].textContent)

for(var i = 0; i < 5; i++){
    if (Number(pageNo[i].textContent) > amount){
        pageNo[i].style.display = 'none';
    }
}