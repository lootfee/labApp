function clearData() {
	
	var dta = document.getElementsByClassName("data");
	var inputUnits = document.getElementsByClassName("units");
	
	for (var i = 0; i < dta.length; i++ )
		{dta[i].value = "";}
	
	for (var i=0; i<inputUnits.length; i++)	
		{inputUnits[i].style.display = "none";}
}

function N(id, places) { 

	return +(Math.round(id + "e+" + places)  + "e-" + places);
	
 }
 
  
function displayUnits(testUnit) {
	var inputData = document.getElementsByClassName("inputData");
	var units = document.getElementById(testUnit);
	//var inputUnits = document.getElementsByClassName("inputUnits");
	var i = 0;	
	
	//var names = document.getElementById(testName);
	
	if (inputData.length>i)	
	{units.style.display = "inline-flex";}
	
	/*if (names == "")
	{document.getElementById(testUnit).style.display = "none";}*/
		
}
  
function calclp(){
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
  
	document.getElementById("vldlUnit").style.display = "inline-flex";
	document.getElementById("ldlcUnit").style.display = "inline-flex";
}


function calcUchem(){
		
	var uvol = document.getElementById("uvol").value;
	var acr = document.getElementById("acr").value;
	var ucrea = document.getElementById("ucrea").value;
	var ualb = document.getElementById("ualb").value;
	var ucal = document.getElementById("ucal").value;
	var uphos = document.getElementById("uphos").value;
	var umag = document.getElementById("umag").value;
	var uuric = document.getElementById("uuric").value;
	var utp = document.getElementById("utp").value;
	var uurea = document.getElementById("uurea").value;
    var usod = document.getElementById("usod").value;
	var upot = document.getElementById("upot").value;
	var uchlo = document.getElementById("uchlo").value;
	
	var u24alb = document.getElementById("24ualb").value;
	var u24crea = document.getElementById("24ucrea").value;
	var u24cal = document.getElementById("24ucal").value;
	var u24phos = document.getElementById("24uphos").value;
	var u24mag = document.getElementById("24umag").value;
	var u24uric = document.getElementById("24uuric").value;
	var u24tp = document.getElementById("24utp").value;
	var u24urea = document.getElementById("24uurea").value;
	var u24sod =  document.getElementById("24usod").value;
	var u24pot = document.getElementById("24upot").value;
	var u24chlo =  document.getElementById("24uchlo").value;
	var i = 1;

	var calAcr = (ualb / (ucrea*10))*1000;
	var calcU24alb = (ualb/1000) * uvol;
	var calcU24crea = (ucrea / 100) * uvol;
	var calcU24cal = (ucal / 100) * uvol;
	var calcU24phos = (uphos / 100) * uvol;
	var calcU24mag = (umag / 100) * uvol;
	var caclU24uric = (uuric / 100) * uvol;
	var calcU24tp = (utp / 100) * uvol;
	var calcU24urea = (uurea / 100) * uvol;
	var calcU24sod = (usod / 100) * uvol;
	var calcU24pot = (upot / 100) * uvol;
	var calcU24chlo = (uchlo / 100) * uvol;
	
	calAcr = N(calAcr, 2);
	calcU24alb = N(calcU24alb, 2);
	calcU24crea = N(calcU24crea, 2);
	calcU24cal = N(calcU24cal, 2);
	calcU24phos = N(calcU24phos, 2);
	calcU24mag = N(calcU24mag, 2);
	caclU24uric = N(caclU24uric, 2);
	calcU24tp = N(calcU24tp, 2);
	calcU24urea = N(calcU24urea, 2);
	calcU24sod = N(calcU24sod, 2);
	calcU24pot = N(calcU24pot, 2);
	calcU24chlo = N(calcU24chlo, 2);

	if (ualb.length<i || ucrea.length<i)
		{u24alb = " " + " mg/24 hrs", u24crea = " " + " mg/24 hrs", acr = " " + " alb/g creatinine";}
	else
		{u24alb = calcU24alb + " mg/24 hrs", u24crea = calcU24crea + " mg/24 hrs", acr = calAcr + " alb/g creatinine";}
	
	if (ualb.length<i || uvol.length<i)
		{u24alb = " " + " mg/24 hrs";}
	else
		{u24alb = calcU24alb + " mg/24 hrs", ualbUnit = "mg/dL";}
	
	if (ucrea.length<i || uvol.length<i)
		{u24crea = " " + " mg/24 hrs";}
	else
		{u24crea = calcU24crea + " mg/24 hrs";}
	
	if (ucal.length<i || uvol.length<i)
		{u24cal = " " + " mg/24 hrs";}
	else
		{u24cal = calcU24cal + " mg/24 hrs";}
	
	if (uphos.length<i || uvol.length<i)
		{u24phos = " " + " mg/24 hrs";}
	else
		{u24phos = calcU24phos + " mg/24 hrs";}
	
	if (umag.length<i || uvol.length<i)
		{u24mag = " " + " mg/24 hrs";}
	else
		{u24mag = calcU24mag + " mg/24 hrs";}
	
	if (uuric.length<i || uvol.length<i)
		{u24uric = " " + " mg/24 hrs";}
	else
		{u24uric = caclU24uric + " mg/24 hrs";}
	
	if (utp.length<i || uvol.length<i)
		{u24tp = " " + " mg/24 hrs";}
	else
		{u24tp = calcU24tp + " mg/24 hrs";}
	
	if (uurea.length<i || uvol.length<i)
		{u24urea = " " + " g/24 hrs";}
	else
		{u24urea = calcU24urea + " g/24 hrs";}
	
	if (usod.length<i || uvol.length<i)
		{u24sod = " " + " mmol/24 hrs";}
	else
		{u24sod = calcU24sod + " mmol/24 hrs";}
	
	if (usod.length<i || uvol.length<i)
		{u24pot = " " + " mmol/24 hrs";}
	else
		{u24pot = calcU24pot + " mmol/24 hrs";}
	
	if (uchlo.length<i || uvol.length<i)
		{u24chlo = " " + " mmol/24 hrs";}
	else
		{u24chlo = calcU24chlo + " mmol/24 hrs";}
	
 	document.getElementById("acr").value = acr;
	document.getElementById("24ualb").value = u24alb;
	document.getElementById("24ucrea").value = u24crea;
	document.getElementById("24ucal").value = u24cal;
	document.getElementById("24uphos").value = u24phos;
	document.getElementById("24umag").value = u24mag;
	document.getElementById("24uuric").value = u24uric;
	document.getElementById("24utp").value = u24tp;
	document.getElementById("24uurea").value = u24urea;
	document.getElementById("24usod").value = u24sod;
	document.getElementById("24upot").value = u24pot;
	document.getElementById("24uchlo").value = u24chlo;
	
}

function calcbsa(){
	var height = document.getElementById("height").value;
	var weight = document.getElementById("weight").value;
	var x = ((height * 30.48) * weight) / 3600;
	var xbsa = Math.sqrt(x);
	xbsa = N(xbsa, 2);

	if (height == "" || weight == "" )
	{bsa = "";}
	else 
	{bsa = xbsa + " m²"}

	document.getElementById("bsa").value = bsa;
}

function calccreaclear(){
	var uvol2 = document.getElementById("uvol2").value;
	var ucrea2 = document.getElementById("ucrea2").value;
	var screa2 = document.getElementById("screa2").value;
	var coltime = document.getElementById("coltime").value;
	var height = document.getElementById("height").value;
	var weight = document.getElementById("weight").value;
	var bsa = ((height * 30.48) * weight) / 3600;
	var calcCreaClear = ((ucrea2 * uvol2) / (screa2  * (coltime * 60)));
	var calcCorCreaClear = (((ucrea2 * uvol2) / (screa2  * (coltime * 60))) * (1.73/bsa));
	var i = 1;
	
	calcCreaClear = N(calcCreaClear, 1);
	calcCorCreaClear = N(calcCorCreaClear, 1);
	
	if (uvol2.length<i || ucrea2.length<i || screa2.length<i || coltime.length<i)
	{creaClear = "";}
	else
	{creaClear = calcCreaClear + " ml/min";}
	if (bsa == "" || uvol2.length<i || ucrea2.length<i || screa2.length<i || coltime.length<i)
	{corCreaClear = "";}
	else
	{corCreaClear = calcCorCreaClear + " ml/min/1.73 m²";}
	
	document.getElementById("creaclear").value = creaClear;
	document.getElementById("corcreaclear").value = corCreaClear;
  
}

function calcUreaToBun(){
	var surea = document.getElementById("surea").value;

	var calcBun = surea * 0.467;
	calcBun = N(calcBun, 2);
	bun = calcBun + " mg/dL";
	document.getElementById("bun").value = bun;
}

function calcTibc(){
	var siron = document.getElementById("siron").value;
	var suibc = document.getElementById("suibc").value;

	var calTibc = (+siron + +suibc);
	calTibc = N(calTibc, 2);
	
	if (siron == "" || suibc == "")
	{tibc = "";}
	else
	{tibc = calTibc + " µg/dL";}
	
	document.getElementById("tibcResult").value = tibc;
}

function calcTsat(){
  var siron = document.getElementById("siron2").value;
  var suibc = document.getElementById("suibc2").value;
  
  var calTsat = (siron / (+siron + +suibc)) * 100;
  calTsat = N(calTsat, 2);
  if (siron == "" || suibc == "")
    {tsat = "";}
  else
  {tsat = calTsat + " %"}
  document.getElementById("tsat").value = tsat;
}

function calcegfr(){
	var screa3 = document.getElementById("screa3").value;
	var age = document.getElementById("egfrAge").value;
	var genm = document.getElementById("genm").checked;
	var genf = document.getElementById("genf").checked;
	var raceb = document.getElementById("raceb").checked;
	var raceo = document.getElementById("raceo").checked;
	var agex = Math.pow(0.993, age);


	if (document.getElementById("genm").checked)
	{k = 0.9;}
	if (document.getElementById("genm").checked)
	{a = -0.411;}
	if (document.getElementById("genf").checked)
	{k = 0.7;}
	if (document.getElementById("genf").checked)
	{a = -0.329;}

	if (document.getElementById("raceb").checked)
	{r = 1.159;}
	if (document.getElementById("raceo").checked)
	{r = 1;}

	if (document.getElementById("genm").checked)
	{g = 1;}
	if (document.getElementById("genf").checked)
	{g = 1.018;}

	if (document.getElementById("genm").checked)
	{x = 0.91;}
	if (document.getElementById("genf").checked)
	{x = 0.71;}

	var e = screa3 / k;
	var f = Math.pow(e, a);
	var h = Math.pow(e, -1.209);

	xmin = 141 * f * agex * g * r;
	xmax = 141 * h * agex * g * r;

	//for (i=0; i < genm.length; i++) {
	   // if (genm[i].checked) {
			//{screax = screa3 / genm;}
	   // }
	 // }

	// for (i=0; i < genf.length; i++) {
	 //   if (genf[i].checked) {
		   // {screax = screa3 / genf;}
	   // }
	 // }
	if (screa3 < x )
	xmin = N(xmin, 0);
	min = xmin + " mL/min/1.73 m²"
	{document.getElementById("egfrAdultOutput").value = min;}
	
	if (screa3 > x )
	xmax = N(xmax, 0);
	max = xmax + " mL/min/1.73 m²"
	{document.getElementById("egfrAdultOutput").value = max;}
}

function calcEgfrP() {
	var screa3p = document.getElementById("screa3p").value;
	var hcm = document.getElementById("hcm").checked;
	var hmet = document.getElementById("hmet").checked;
	var hp = document.getElementById("heightPedia").value;
	
	if (document.getElementById("hcm").checked)
	{x = 0.413;}
	if (document.getElementById("hmet").checked)
	{x = 41.3;}

	xegfrP = x * (hp/screa3p);
	xegfrP = N(xegfrP, 0);
	egfrP = xegfrP + " mL/min/1.73 m²"
	{document.getElementById("egfrPediaOutput").value = egfrP;}
}


