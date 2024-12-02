'use strict';

var switchButton = document.querySelector('.switch-button');
var switchBtnRight = document.querySelector('.switch-button-case.right');
var switchBtnLeft = document.querySelector('.switch-button-case.left');
var activeSwitch = document.querySelector('.active');
var numDraws = document.getElementById('numDraws');//決定要抽幾抽的表單

//抓轉蛋機外觀元素，用來調整轉蛋機的外觀
var st3 = document.getElementsByClassName('st3');
var st4 = document.getElementsByClassName('st4');
var st5 = document.getElementsByClassName('st5');
var st6 = document.getElementsByClassName('st6');
function changeMachine(color3,color4,color5,color6){
	for (var i = 0; i < st3.length; i++) {
		st3[i].style.fill = color3;
	}
	for (var i = 0; i < st4.length; i++) {
		st4[i].style.fill = color4;
	}
	for (var i = 0; i < st5.length; i++) {
		st5[i].style.fill = color5;
	}
	for (var i = 0; i < st6.length; i++) {
		st6[i].style.fill = color6;
	}
}
function switchLeft(){//左邊，單抽
	switchBtnRight.classList.remove('active-case');
	switchBtnLeft.classList.add('active-case');
	activeSwitch.style.left= '0%';
	numDraws.value=1;
	changeMachine('#1e90ff', '#00bfff', '#87cefa', '#4682b4');
}

function switchRight(){//右邊，10連
	switchBtnRight.classList.add('active-case');
	switchBtnLeft.classList.remove('active-case');
	activeSwitch.style.left = '50%';
	numDraws.value=10;
	changeMachine('#FF0000', '#FF4500', '#B22222', '#8B0000');
	achine('#FFD700', '#FFA500', '#FF6347', '#d76a1d');// Suspected Redundant Code
}

switchBtnLeft.addEventListener('click', function(){
	switchLeft();
}, false);

switchBtnRight.addEventListener('click', function(){
	switchRight();
}, false);

