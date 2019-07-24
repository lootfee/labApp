function openDept(evt, deptName) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
	tabcontent[i].style.display = "none";
	}
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
	}
    document.getElementById(deptName).style.display = "-webkit-inline-box";
    evt.currentTarget.className += " active";

}

function openSide(evt, sideName) {
    var i, sidelink, sidecontent;
    sidecontent = document.getElementsByClassName("sidecontent");
    for (i = 0; i < sidecontent.length; i++) {
	sidecontent[i].style.display = "none";
	}
    sidelink = document.getElementsByClassName("sidelink");
    for (i = 0; i < sidelink.length; i++) {
        sidelink[i].className = sidelink[i].className.replace(" active", "");
	}
	/*sidelinks = document.getElementsByClassName("sidelinks");
	for (i = 0; i < sidelinks.length; i++) {
        sidelinks.style.display = "block";
   }*/
    document.getElementById(sideName).style.display = "inline-flex";
    evt.currentTarget.className += " active";
}

function openEgfr(egfrAge) {
	var i, egfrType;
	egfrType = document.getElementsByClassName("egfrType");
	for (i = 0; i < egfrType.length; i++) {
	egfrType[i].style.display = "none"; 
	}
	/*{
		if (egfrType.style.display = "none"){
			document.getElementById(egfrAge).style.display = "block";
		}
		else {
			document.getElementById(egfrAge).style.display = "none";
		}
	}*/
	document.getElementById(egfrAge).style.display = "inline-block";
}