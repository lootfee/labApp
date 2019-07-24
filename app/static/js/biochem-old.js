function clearData() {
	
	var dta = document.getElementsByClassName("data");
	var outputData = document.getElementsByClassName("outputData");
	
	for (var i = 0; i < dta.length; i++ )
		{dta[i].value = "";}
	for (var i = 0; i < outputData.length; i++ )
		{outputData[i].value = document.getElementsByClassName("outputData").value;}
}

function N(id, places) { 

	return +(Math.round(id + "e+" + places)  + "e-" + places);
	
  }
  
function calclp()
{
  var chol = document.getElementById("cholesterol").value;
  var hdl = document.getElementById("hdl").value;
  var ldl = document.getElementById("ldl").value;
  var trig = document.getElementById("trig").value;
  var vldl = (trig/5);
  if (trig == "")
  {vldl = "";}
  document.getElementById("vldl").value = vldl;
  var ldlc = (chol-hdl-vldl);
  ldlc = N(ldlc, 2);
  if (vldl == "")
  {ldlc = "";}
  document.getElementById("ldlc").value = ldlc;
  var cholhdl = (chol/hdl); 
  cholhdl = N(cholhdl, 2);
  if (chol == "")
  {cholhdl = "";}
  document.getElementById("cholhdl").innerHTML = cholhdl;
    
  if (ldl == "")
  {hdlldl = (hdl/ldlc);}
  else 
  {hdlldl = (hdl/ldl);}
     
  if (ldl == "")
  {ldlhdl = (ldlc/hdl);}
  else 
  {ldlhdl = (ldl/hdl);}
  
  hdlldl = N(hdlldl, 2);
  document.getElementById("hdlldl").innerHTML = hdlldl;
  ldlhdl = N(ldlhdl, 2);
  document.getElementById("ldlhdl").innerHTML = ldlhdl;
  
}


function calcuac(){
  var uvol = document.getElementById("uvol").value;
  var ucrea = document.getElementById("ucrea").value;
  var ualb = document.getElementById("ualb").value;
  var acr = document.getElementById("acr").value;
  var i = 1;
  
  var calAcr = (ualb / (ucrea*10))*1000;
  calAcr = N(calAcr, 2)
  
  if (ualb.length<i)
  {acr = "" + " alb/g creatinine";}
  else if (ucrea.length<i)
  {acr = "" + " alb/g creatinine";}
  else 
  {acr = calAcr + " alb/g creatinine";}
  document.getElementById("acr").value = acr;
  
  var u24alb = (ualb/1000) * uvol;
  u24alb = N(u24alb, 2);
  document.getElementById("24ualb").value = u24alb;
  var u24crea = (ucrea / 100) * uvol;
  u24crea = N(u24crea, 2);
  document.getElementById("24ucrea").value = u24crea;
    
}

function calcuca(){
  var uvolca = document.getElementById("uvol").value;
  var ucal = document.getElementById("ucal").value;
  var u24cal = (ucal / 100) * uvolca;
  u24cal = N(u24cal, 2);
  document.getElementById("24ucal").innerHTML = u24cal;
}

function calcuphos(){
  var uvol = document.getElementById("uvol").value;
  var uphos = document.getElementById("uphos").value;
  var u24phos = (uphos / 100) * uvol;
  u24phos = N(u24phos, 2);
  document.getElementById("24uphos").innerHTML = u24phos;
}

function calcuurea(){
  var uvol = document.getElementById("uvol").value;
  var uurea = document.getElementById("uurea").value;
  var u24urea = (uurea / 100) * uvol;
  u24urea = N(u24urea, 2);
  document.getElementById("24uurea").innerHTML = u24urea;
}

function calcumag(){
  var uvol = document.getElementById("uvol").value;
  var umag = document.getElementById("umag").value;
  var u24mag = (umag / 100) * uvol;
  u24mag = N(u24mag, 2);
  document.getElementById("24umag").innerHTML = u24mag;
}

function calcuuric(){
  var uvol = document.getElementById("uvol").value;
  var uuric = document.getElementById("uuric").value;
  var u24uric = (uuric / 100) * uvol;
  u24uric = N(u24uric, 2);
  document.getElementById("24uuric").innerHTML = u24uric;
}

function calcusod(){
  var uvol = document.getElementById("uvol").value;
  var usod = document.getElementById("usod").value;
  var u24sod = (usod / 100) * uvol;
  u24sod = N(u24sod, 2);
  document.getElementById("24usod").innerHTML = u24sod;
}

function calcupot(){
  var uvol = document.getElementById("uvol").value;
  var upot = document.getElementById("upot").value;
  var u24pot = (upot / 100) * uvol;
  u24pot = N(u24pot, 2);
  document.getElementById("24upot").innerHTML = u24pot;
}

function calcuchlo(){
  var uvol = document.getElementById("uvol").value;
  var uchlo = document.getElementById("uchlo").value;
  var u24chlo = (uchlo / 100) * uvol;
  u24chlo = N(u24chlo, 2);
  document.getElementById("24uchlo").innerHTML = u24chlo;
}

function calcutp(){
  var uvol = document.getElementById("uvol").value;
  var utp = document.getElementById("utp").value;
  var u24tp = (utp / 100) * uvol;
  u24tp = N(u24tp, 2);
  document.getElementById("24utp").innerHTML = u24tp;
}