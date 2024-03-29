google.charts.load('current', {'packages':['line', 'corechart']});
//google.charts.setOnLoadCallback(drawChart);


function corDate(unixDate){
	var incTime = document.getElementById('includeTime');
	var unCorDate = new Date((unixDate - (25567 + 2))*86400*1000);
	var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
	var year = unCorDate.getFullYear();
	var month = months[unCorDate.getMonth()];
	var day = unCorDate.getDate();
	var hr = unCorDate.getHours();
		if (unCorDate.getHours() < 10){
			hr = '0' + unCorDate.getHours();
			}
	var mins = unCorDate.getMinutes()
		if (unCorDate.getMinutes() < 10) {
			mins = '0' + unCorDate.getMinutes();
			}
	var dateTime = month + ' ' + day + ', ' + year + ' ' + hr + ':' + mins;
	var date = month + ' ' + day + ', ' + year + ' ';
		if (incTime.checked == true){
		   return dateTime;
		}
		else {
			return date;
		}
}

function handleFile(e) {
	var incDate = document.getElementById('includeDate');
	var lvl1 = document.getElementById('lvl1');
	var lvl2 = document.getElementById('lvl2');
	var lvl3 = document.getElementById('lvl3');
	var level1Container = document.getElementById('level1Container');
	var level2Container = document.getElementById('level2Container');
	var level3Container = document.getElementById('level3Container');
	var importResultContainer = document.getElementById('importResultContainer');
	
	document.getElementById("createImportChart").style.display = 'inline-block';
	document.getElementById("calculate").style.display = 'inline-block';
	
	var files = e.target.files, f = files[0];
	var reader = new FileReader();
	reader.onload = function(e) {
	var data = new Uint8Array(e.target.result);
	var wb = XLSX.read(data, {type: 'array'});

    wb.SheetNames.forEach(function(sheetName) {
		//var sCSV = XLS.utils.make_csv(wb.Sheets[sheetName]);   
		var data = XLS.utils.sheet_to_json(wb.Sheets[sheetName], {header:1, raw: true, defval: ''});   
		
		if ( lvl3.selected == true){
				if (incDate.checked === true){
					var rowHeader = "<input class='col-md-3 rowHeader' value='Date'><input class='col-md-1 rowHeader' value='Level 1'><input class='col-md-1 rowHeader' value='Level 2'><input class='col-md-1 rowHeader' value='Level 3'><input class='col-md-3 rowHeader' value='Date'><input class='col-md-1 rowHeader' value='Level 1'><input class='col-md-1 rowHeader' value='Level 2'><input class='col-md-1 rowHeader' value='Level 3'>";
				}
				else {
					var rowHeader = "<input class='col-md-1 rowHeader' value='Run No'><input class='col-md-1 rowHeader ' value='Level 1'><input class='col-md-1 rowHeader ' value='Level 2'><input class='col-md-1 rowHeader ' value='Level 3'><input class='col-md-1 rowHeader ' value='Run No'><input class='col-md-1 rowHeader ' value='Level 1'><input class='col-md-1 rowHeader ' value='Level 2'><input class='col-md-1 rowHeader ' value='Level 3'><input class='col-md-1 rowHeader' value='Run No'><input class='col-md-1 rowHeader' value='Level 1'><input class='col-md-1 rowHeader' value='Level 2'><input class='col-md-1 rowHeader' value='Level 3'>";
				}
				$("#my_file_output").append(rowHeader);
				$.each(data, function(indexR, valueR){
					if (incDate.checked === true){						
						var rows = "<input class='col-md-3 cDate '" + "value='" + corDate(data[indexR][0]) + "'>" + "<input class='col-md-1 qcImportData1 '" + "value='" + data[indexR][1] + "'>" + "<input class='col-md-1 qcImportData2 '" + "value='" + data[indexR][2] + "'>" + "<input class='col-md-1 qcImportData3 '" + "value='" + data[indexR][3] + "'>";
						
						$("#my_file_output").append(rows);
					}
					else if (incDate.checked === false){						
						var rows = "<input class='col-md-1 cDate '" + "value='" + (data[indexR][0]) + "'>" + "<input class='col-md-1 qcImportData1 '" + "value='" + data[indexR][1] + "'>" + "<input class='col-md-1 qcImportData2 '" + "value='" + data[indexR][2] + "'>" + "<input class='col-md-1 qcImportData3 '" + "value='" + data[indexR][3] + "'>";	
						
						$("#my_file_output").append(rows);
					}
				});		
			/*importResultContainer.style.display = 'block';
			level1Container.style.display = 'block';
			level2Container.style.display = 'block';
			level3Container.style.display = 'block';*/
			}
		else if ( lvl2.selected === true){
				if (incDate.checked === true){
					var rowHeader = "<input class='col-md-2 ' value='Date'><input class='col-md-1 ' value='Level 1'><input class='col-md-1 ' value='Level 2'><input class='col-md-2 ' value='Date'><input class='col-md-1 ' value='Level 1'><input class='col-md-1 ' value='Level 2'><input class='col-md-2' value='Date'><input class='col-md-1 ' value='Level 1'><input class='col-md-1 ' value='Level 2'>";
				}
				else {
					var rowHeader = "<input class='col-md-1 ' value='Run No'><input class='col-md-1 ' value='Level 1'><input class='col-md-1 ' value='Level 2'><input class='col-md-1 ' value='Run No'><input class='col-md-1 ' value='Level 1'><input class='col-md-1 ' value='Level 2'><input class='col-md-1 ' value='Run No'><input class='col-md-1 ' value='Level 1'><input class='col-md-1 ' value='Level 2'><input class='col-md-1 ' value='Run No'><input class='col-md-1 ' value='Level 1'><input class='col-md-1 ' value='Level 2'>";
				}
				$("#my_file_output").append(rowHeader);
				$.each(data, function(indexR, valueR){
					if (incDate.checked == true){						
						var rows = "<input class='col-md-2 cDate '" + "value='" + corDate(data[indexR][0]) + "'>" + "<input class='col-md-1 qcImportData1 '" + "value='" + data[indexR][1] + "'>" + "<input class='col-md-1 qcImportData2 '" + "value='" + data[indexR][2] + "'>";
						
						$("#my_file_output").append(rows);
					}
					else if (incDate.checked === false){
						var rows = "<input class='col-md-1 cDate '" + "value='" + (data[indexR][0]) + "'>" + "<input class='col-md-1 qcImportData1 '" + "value='" + data[indexR][1] + "'>" + "<input class='col-md-1 qcImportData2 '" + "value='" + data[indexR][2] + "'>";
						
						$("#my_file_output").append(rows);
					}
				});
			/*importResultContainer.style.display = 'block';
			level1Container.style.display = 'block';
			level2Container.style.display = 'block';*/
			}
		else if ( lvl1.selected === true ){
				if (incDate.checked === true){
					var rowHeader = "<input class='col-md-2 ' value='Date'><input class='col-md-1 ' value='Level 1'><input class='col-md-2 ' value='Date'><input class='col-md-1 ' value='Level 1'><input class='col-md-2 ' value='Date'><input class='col-md-1 ' value='Level 1'><input class='col-md-2 ' value='Date'><input class='col-md-1 ' value='Level 1'>";
				}
				else {
					var rowHeader = "<input class='col-md-1 ' value='Run No'><input class='col-md-1 ' value='Level 1'><input class='col-md-1 ' value='Run No'><input class='col-md-1 ' value='Level 1'><input class='col-md-1 ' value='Run No'><input class='col-md-1 ' value='Level 1'><input class='col-md-1 ' value='Run No'><input class='col-md-1 ' value='Level 1'><input class='col-md-1 ' value='Run No'><input class='col-md-1 ' value='Level 1'><input class='col-md-1 ' value='Run No'><input class='col-md-1 ' value='Level 1'>";
				}
				$("#my_file_output").append(rowHeader);
				$.each(data, function(indexR, valueR){
					if (incDate.checked == true){						
						var rows = "<input class='col-md-2 cDate '" + "value='" + corDate(data[indexR][0]) + "'>" + "<input class='col-md-1 qcImportData1 '" + "value='" + data[indexR][1] + "'>" ;
						
						$("#my_file_output").append(rows);
					}
					else if (incDate.checked === false){
						var rows = "<input class='col-md-1 cDate '" + "value='" + (data[indexR][0]) + "'>" + "<input class='col-md-1 qcImportData1 '" + "value='" + data[indexR][1] + "'>" ;
						
						$("#my_file_output").append(rows);
					}				
				});
			/*importResultContainer.style.display = 'block';
			level1Container.style.display = 'block';*/
			}
	});
  };
  reader.readAsArrayBuffer(f);
  
}
document.getElementById('my_file_input').addEventListener('change', handleFile, false);


function decimalPlaces(num) {
	let match = (''+num).match(/(?:\.(\d+))?(?:[eE]([+-]?\d+))?$/);
	if (!match) { return 0; }
	return Math.max(
	   0,
	   // Number of digits right of decimal point.
	   (match[1] ? match[1].length : 0)
	   // Adjust for scientific notation.
	   - (match[2] ? +match[2] : 0));
}

function N(id, places) { 
	return +(Math.round(id + "e+" + places)  + "e-" + places);
}

function calcStdev() {
	var mn = document.getElementById("cmean").value;
	var lvl1Mean = document.getElementById("lvl1Mean").value;
	var lvl2Mean = document.getElementById("lvl2Mean").value;
	var lvl3Mean = document.getElementById("lvl3Mean").value;
	var variance = document.getElementById("variance").value;
	var lvl1Variance = document.getElementById("lvl1Variance").value;
	var lvl2Variance = document.getElementById("lvl2Variance").value;
	var lvl3Variance = document.getElementById("lvl3Variance").value;
	var sd = document.getElementById("cstndev").value;
	var lvl1Stndev = document.getElementById("lvl1Stndev").value;
	var lvl2Stndev = document.getElementById("lvl2Stndev").value;
	var lvl3Stndev = document.getElementById("lvl3Stndev").value;
	var cv = document.getElementById("cv").value;
	var lvl1Cv = document.getElementById("lvl1Cv").value;
	var lvl2Cv = document.getElementById("lvl2Cv").value;
	var lvl2Cv = document.getElementById("lvl2Cv").value;
	var datas = document.getElementsByClassName('qc-data');
	var qcImportData1 = document.getElementsByClassName('qcImportData1');
	var qcImportData2 = document.getElementsByClassName('qcImportData2');
	var qcImportData3 = document.getElementsByClassName('qcImportData3');
	var total = 0;
	var total1 = 0;
	var total2 = 0;
	var total3 = 0;
	var totSqrd = 0;
	var totSqrd1 = 0;
	var totSqrd2 = 0;
	var totSqrd3 = 0;
	var dp = 0;
	var dp1 = 0;
	var dp2 = 0;
	var dp3 = 0;
	var x = 0;
	var x1 = 0;
	var x2 = 0;
	var x3 = 0;
	var y = 0;
	var y1 = 0;
	var y2 = 0;
	var y3 = 0;
	var dataLength = 0;
	var dataLength1 = 0;
	var dataLength2 = 0;
	var dataLength3 = 0;
	
	if (datas.length > 0) {
		for (var i = 0; i < datas.length; i++ ){
			if (datas[i].value != ''){
				dataLength += 1;
				total += parseFloat(datas[i].value);
				if (decimalPlaces(datas[i].value) > x){
					y = datas[i].value;
					x = decimalPlaces(y);
				}
			}
			
		}
		dp = x;
		mn = total / dataLength;
		
		for (var i=0; i< datas.length; i++){
			if (datas[i].value != ''){
				totSqrd += (parseFloat(datas[i].value) - mn) * (parseFloat(datas[i].value) - mn);
			}
		}
		
		variance = totSqrd / (dataLength - 1);
		sd = Math.sqrt(variance);
		cv = parseFloat(sd / mn) * 100;

		givenResultContainer.style.display = 'block';
		
		mn = N(mn, dp)
		document.getElementById("cmean").value = mn;
		variance = N(variance, dp+4);
		document.getElementById("variance").value = variance;
		sd = N(sd, dp);
		document.getElementById("cstndev").value = sd;
		cv = N(cv, 1);
		document.getElementById("cv").value = cv;
	}
	
	if (qcImportData1.length > 0) {
		for (var i = 0; i < qcImportData1.length; i++ ){
			if (qcImportData1[i].value != ''){
				dataLength1 += 1;
				total1 += parseFloat(qcImportData1[i].value);
				if (decimalPlaces(qcImportData1[i].value) > x1){
					y1 = qcImportData1[i].value;
					x1 = decimalPlaces(y1);
				}
			}
			
		}
		dp1 = x1;
		lvl1Mean = total1 / dataLength1;
		
		for (var i=0; i< qcImportData1.length; i++){
			if (qcImportData1[i].value != ''){
				totSqrd1 += (parseFloat(qcImportData1[i].value) - lvl1Mean) * (parseFloat(qcImportData1[i].value) - lvl1Mean);
			}
		}
		
		lvl1Variance = totSqrd1 / (dataLength1 - 1);
		lvl1Stndev = Math.sqrt(lvl1Variance);
		lvl1Cv = parseFloat(lvl1Stndev / lvl1Mean) * 100;

		importResultContainer.style.display = 'block';
		level1Container.style.display = 'block';

		lvl1Mean = N(lvl1Mean, dp1)
		document.getElementById("lvl1Mean").value = lvl1Mean;
		lvl1Variance = N(lvl1Variance, dp1+4);
		document.getElementById("lvl1Variance").value = lvl1Variance;
		lvl1Stndev = N(lvl1Stndev, dp1);
		document.getElementById("lvl1Stndev").value = lvl1Stndev;
		lvl1Cv = N(lvl1Cv, 1);
		document.getElementById("lvl1Cv").value = lvl1Cv;
	}
	
	if (qcImportData2.length > 0) {
		for (var i = 0; i < qcImportData2.length; i++ ){
			if (qcImportData2[i].value != ''){
				dataLength2 += 1;
				total2 += parseFloat(qcImportData2[i].value);
				if (decimalPlaces(qcImportData2[i].value) > x2){
					y2 = qcImportData2[i].value;
					x2 = decimalPlaces(y2);
				}
			}
		}
		dp2 = x2;
		lvl2Mean = total2 / dataLength2;
		
		for (var i=0; i< qcImportData2.length; i++){
			if (qcImportData2[i].value != ''){
				totSqrd2 += (parseFloat(qcImportData2[i].value) - lvl2Mean) * (parseFloat(qcImportData2[i].value) - lvl2Mean);
			}
		}
		
		lvl2Variance = totSqrd2 / (dataLength2 - 1);
		lvl2Stndev = Math.sqrt(lvl2Variance);
		lvl2Cv = parseFloat(lvl2Stndev / lvl2Mean) * 100;

		importResultContainer.style.display = 'block';
		level1Container.style.display = 'block';
		level2Container.style.display = 'block';

		lvl2Mean = N(lvl2Mean, dp2)
		document.getElementById("lvl2Mean").value = lvl2Mean;
		lvl2Variance = N(lvl2Variance, dp2+4);
		document.getElementById("lvl2Variance").value = lvl2Variance;
		lvl2Stndev = N(lvl2Stndev, dp2);
		document.getElementById("lvl2Stndev").value = lvl2Stndev;
		lvl2Cv = N(lvl2Cv, 1);
		document.getElementById("lvl2Cv").value = lvl2Cv;
	}
	
	if (qcImportData3.length > 0) {
		for (var i = 0; i < qcImportData3.length; i++ ){
			if (qcImportData3[i].value != ''){
				dataLength3 += 1;
				total3 += parseFloat(qcImportData3[i].value);
				if (decimalPlaces(qcImportData3[i].value) > x3){
					y3 = qcImportData3[i].value;
					x3 = decimalPlaces(y3);
				}
			}
			
		}
		dp3 = x3;
		lvl3Mean = total3 / dataLength3;
		
		for (var i=0; i< qcImportData3.length; i++){
			if (qcImportData3[i].value != ''){
				totSqrd3 += (parseFloat(qcImportData3[i].value) - lvl3Mean) * (parseFloat(qcImportData3[i].value) - lvl3Mean);
			}
		}
		
		lvl3Variance = totSqrd3 / (dataLength3 - 1);
		lvl3Stndev = Math.sqrt(lvl3Variance);
		lvl3Cv = parseFloat(lvl3Stndev / lvl3Mean) * 100;

		importResultContainer.style.display = 'block';
		level1Container.style.display = 'block';
		level2Container.style.display = 'block';
		level3Container.style.display = 'block';

		lvl3Mean = N(lvl3Mean, dp3)
		document.getElementById("lvl3Mean").value = lvl3Mean;
		lvl3Variance = N(lvl3Variance, dp3+4);
		document.getElementById("lvl3Variance").value = lvl3Variance;
		lvl3Stndev = N(lvl3Stndev, dp3);
		document.getElementById("lvl3Stndev").value = lvl3Stndev;
		lvl3Cv = N(lvl3Cv, 1);
		document.getElementById("lvl3Cv").value = lvl3Cv;
	}
	
}

function inputQC() {
	var qcEntry =  document.getElementById("qcEntry").value;
	var container = document.getElementById("qcDataContainer");
	var datas = document.getElementsByClassName('qc-data');
	
	if (qcEntry.length > 0){
	var divEl = document.createElement("div");
		divEl.className = "col-md-1";
	container.appendChild(divEl);
	var input = document.createElement("input");
		input.type = "text";
		input.className = "form-control qc-data";
		input.value = parseFloat(qcEntry);
	divEl.appendChild(input);
	}
	
	if (datas.length > 0){
		document.getElementById("calculate").style.display = 'inline-block';
		document.getElementById("createChart").style.display = 'inline-block';
	}
	else{
		document.getElementById("calculate").style.display = 'none';
		document.getElementById("createChart").style.display = 'none';
	}
	
	document.getElementById("qcEntry").value = "";
	document.getElementById("qcEntry").focus();
}

document.getElementById('qcEntry').addEventListener('keyup', function(event) {
	if (event.keyCode === 13){
		event.preventDefault();
		document.getElementById("submitQC").click();
	}
});

function clearData(){
	var container = document.getElementById("qcDataContainer");
	var chartContainer = document.getElementById("chartContainer");
	var  qcResult = document.getElementsByClassName("qc-result");
	var  calculate = document.getElementsByClassName("calculate");
	var my_file_output = document.getElementById("my_file_output");
	var importResultContainer = document.getElementById('importResultContainer');
	//var fileInputForm = document.getElementById('fileInputForm');
	
	while (container.hasChildNodes()) {   
		container.removeChild(container.firstChild);
	}
	
	while (chartContainer.hasChildNodes()) {   
		chartContainer.removeChild(chartContainer.firstChild);
	}
	
	while (my_file_output.hasChildNodes()) {   
		my_file_output.removeChild(my_file_output.firstChild);
	}
	/*while (importResultContainer.hasChildNodes()) {   
		importResultContainer.removeChild(importResultContainer.firstChild);
	}*/
	
	for (var i=0; i<qcResult.length; i++)	
		{qcResult[i].value = "";}
	
	document.getElementById("calculate").style.display = 'none';
	document.getElementById("importResultContainer").style.display = 'none';
	document.getElementById('fileInputForm').reset();
}

function drawChart() {
	// Create the data table.
	let ctx = document.getElementById('chartContainer');
	var ctxp = document.getElementById('chartContainer_print');
	let datas = document.getElementsByClassName('qc-data');
	let cmn = document.getElementById("cmean").value;
	let csd = document.getElementById("cstndev").value;
	let gmn = document.getElementById("gmean1").value;
	let gsd = document.getElementById("gstndev1").value;
	let gbtn = document.getElementById("gbtn").checked;
	let arr = [];
	
	var data = new google.visualization.DataTable();
	data.addColumn('string', "Run No");
	data.addColumn('number', "QC Result");
	data.addColumn({type: 'string', role: 'annotation'});
	
	for(let i=0; i<datas.length; i++){
		arr.push(datas[i].value);
		data.addRows([
			['', parseFloat(arr[i]), arr[i]]
		]);	
		
		
		if (gbtn == false) {
			var options = {
				//title: "LJ Chart",
				width: 1000,
				height: 400,
				series: {
					0: {targetAxisIndex: 0}
				},
				vAxes: {
					0: {title: '',
						baseline: cmn}
				},
				hAxis: {
					ticks: datas[i].value,
					/*title: '',
					gridlines: {
						count: null,
						color: 'blue'
					},*/
				},			
				vAxis: {
					ticks: [{v: +cmn + +(csd*3), f: '+3sd'}, {v: +cmn + +(csd*2), f: '+2sd'}, {v: +cmn + +csd, f: '+1sd'}, {v: cmn, f: 'mean'}, {v: cmn-csd, f: '-1sd'}, {v: cmn - (csd*2), f: '-2sd'}, {v: cmn - (csd*3), f: '-3sd'} ],
					viewWindow: {
							max: +cmn + +(csd*3),
							min: cmn - (csd*3),
						},
				},									
				pointSize: 10,
				logScale: false
			};
		}
		
		if (gbtn == true){
			var options = {
				//title: "LJ Chart",
				width: 1000,
				height: 400,
				series: {
					0: {targetAxisIndex: 0}
				},
				vAxes: {
					0: {title: '',
						baseline: gmn}
				},
				hAxis: {
					ticks: datas[i].value,
					/*title: '',
					gridlines: {
						count: null,
						color: 'blue'
					},*/
				},
				vAxis: {
					ticks: [{v: +gmn + +(gsd*3), f: '+3sd'}, {v: +gmn + +(gsd*2), f: '+2sd'}, {v: +gmn + +gsd, f: '+1sd'}, {v: gmn, f: 'mean'}, {v: gmn-gsd, f: '-1sd'}, {v: gmn - (gsd*2), f: '-2sd'}, {v: gmn - (gsd*3), f: '-3sd'} ],
					viewWindow: {
							max: +gmn + +(gsd*3),
							min: gmn - (gsd*3),
						},
				},								
				pointSize: 10,
				logScale: false
			};
		}
	}
	
	var chart = new google.visualization.LineChart(ctx);
	//var chart_print = new google.visualization.LineChart(ctxp);

    chart.draw(data, options);
	//chart_print.draw(data, options);
	
}

function drawChart2() {
	// Create the data table.
	var ctx = document.getElementById('chartContainer');
	var lvl1Mean = document.getElementById("lvl1Mean").value;
	var lvl2Mean = document.getElementById("lvl2Mean").value;
	var lvl3Mean = document.getElementById("lvl3Mean").value;
	var lvl1Stndev = document.getElementById("lvl1Stndev").value;
	var lvl2Stndev = document.getElementById("lvl2Stndev").value;
	var lvl3Stndev = document.getElementById("lvl3Stndev").value;
	var qcImportData1 = document.getElementsByClassName('qcImportData1');
	var qcImportData2 = document.getElementsByClassName('qcImportData2');
	var qcImportData3 = document.getElementsByClassName('qcImportData3');
	var cDate = document.getElementsByClassName('cDate');
	var gbtn = document.getElementById("gbtn").checked;
	var gmean1 = document.getElementById("gmean1").value;
	var gmean2 = document.getElementById("gmean2").value;
	var gmean3 = document.getElementById("gmean3").value;
	var gstndev1 = document.getElementById("gstndev1").value;
	var gstndev2 = document.getElementById("gstndev2").value;
	var gstndev3 = document.getElementById("gstndev3").value;
	var arr1 = [];
	var arr12 = [];
	var arr2 = [];
	var arr22 = [];
	var arr3 = [];
	var arr32 = [];
	var arrD = [];
		
	var p3sd1 = parseFloat(+lvl1Mean + +(lvl1Stndev*3));
	var p2sd1= parseFloat(+lvl1Mean + +(lvl1Stndev*2));
	var p1sd1 = parseFloat(+lvl1Mean + +lvl1Stndev);
	var n1sd1 = parseFloat(lvl1Mean - lvl1Stndev);
	var n2sd1 = parseFloat(lvl1Mean - lvl1Stndev*2);
	var n3sd1 = parseFloat(lvl1Mean - lvl1Stndev*3);
	
	var p3sd2 = parseFloat(+lvl2Mean + +(lvl2Stndev*3));
	var p2sd2 = parseFloat(+lvl2Mean + +(lvl2Stndev*2));
	var p1sd2 = parseFloat(+lvl2Mean + +lvl2Stndev);
	var n1sd2 = parseFloat(lvl2Mean - lvl2Stndev);
	var n2sd2 = parseFloat(lvl2Mean - lvl2Stndev*2);
	var n3sd2 = parseFloat(lvl2Mean - lvl2Stndev*3);
	
	var p3sd3 = parseFloat(+lvl3Mean + +(lvl3Stndev*3));
	var p2sd3 = parseFloat(+lvl3Mean + +(lvl3Stndev*2));
	var p1sd3 = parseFloat(+lvl3Mean + +lvl3Stndev);
	var n1sd3 = parseFloat(lvl3Mean - lvl3Stndev);
	var n2sd3 = parseFloat(lvl3Mean - lvl3Stndev*2);
	var n3sd3 = parseFloat(lvl3Mean - lvl3Stndev*3);
	
	var data = new google.visualization.DataTable();
	data.addColumn('string', "Run Date");
	data.addColumn('number', "Lvl 1");
	data.addColumn({type: 'string', role: 'annotation'});
	data.addColumn('number', "Lvl 2");
	data.addColumn({type: 'string', role: 'annotation'});
	data.addColumn('number', "Lvl 3");
	data.addColumn({type: 'string', role: 'annotation'});
	
	for (var i=0;i<cDate.length;i++){
		
		if (cDate.length > 0){
			arrD.push(cDate[i].value.toString());
		}
		if (qcImportData1.length > 0){
			arr1.push(qcImportData1[i].value);
		}
		if (qcImportData2.length > 0){
			arr2.push(qcImportData2[i].value);
		}
		if (qcImportData3.length > 0){
			arr3.push(qcImportData3[i].value);
		}
		data.addRows([
			[(arrD[i]), parseFloat(arr1[i]), arr1[i], parseFloat(arr2[i]), arr2[i], parseFloat(arr3[i]), arr3[i]]
		]);	
	}
		
		if (gbtn == false) {
			var options = {
				title: '',
				width: 1000,
				height: 400,
				interpolateNulls: true,
				series: {
					0: {targetAxisIndex: 0},
					1: {targetAxisIndex: 1},
					2: {targetAxisIndex: 2}
				},
				vAxes: {
					0: {title: '',
						baseline: lvl1Mean,
						ticks: [{v: p3sd1, f: '+3sd'}, {v: p2sd1, f: '+2sd'}, {v: p1sd1, f: '+1sd'}, {v: lvl1Mean, f: 'mean'}, {v: n1sd1, f: '-1sd'}, {v: n2sd1, f: '-2sd'}, {v: n3sd1, f: '-3sd'}],
						/*minValue: n3sd1,
						maxValue: p3sd1,*/
						//viewWindowMode: 'maximized',
						viewWindow: {
							max: p3sd1,
							min: n3sd1
						}
					},
					1: {title: '',
						baseline: lvl2Mean,
						ticks: [{v: p3sd2, f: ''}, {v: p2sd2, f: ''}, {v: p1sd2, f: ''}, {v: lvl2Mean, f: ''}, {v: n1sd2, f: ''}, {v: n2sd2, f: ''}, {v: n3sd2, f: ''}],
						/*minValue: n3sd2,
						maxValue: p3sd2,*/
						//viewWindowMode: 'maximized',
						viewWindow: {
							max: p3sd2,
							min: n3sd2,
						}
					},
					2: {title: '',
						baseline: lvl3Mean,
						ticks: [{v: p3sd3, f: ''}, {v: p2sd3, f: ''}, {v: p1sd3, f: ''}, {v: lvl3Mean, f: ''}, {v: n1sd3, f: ''}, {v: n2sd3, f: ''}, {v: n3sd3, f: ''}],
						/*minValue: n3sd3,
						maxValue: p3sd3,*/
						//viewWindowMode: 'maximized',
						viewWindow: {
							max: p3sd3,
							min: n3sd3,
						}
					}
				},
				chartArea:{
					top: '10%',
					width:'80%',
					height:'75%'
				},
				hAxis: {
					ticks: arrD[i],
					textStyle: {
						fontSize: 9
					},
				},			
				/*vAxis: {
					viewWindowMode: 'maximized',
				},	*/					
				pointSize: 5,
				annotations: {
					textStyle: {
					  fontSize: 7,
					  bold: false,
					  opacity: 0.0,
					},
					stem : {
						color: "white",
					}
				},
				logScale: false,
			};
		}
		
		if (gbtn == true){
			var options = {
				title: '',
				width: 1000,
				height: 400,
				interpolateNulls: true,
				series: {
					0: {targetAxisIndex: 0},
					1: {targetAxisIndex: 1},
					2: {targetAxisIndex: 2}
				},
				vAxes: {
					0: {title: '',
						baseline: gmean1,
						ticks: [{v: (+gmean1 + +(gstndev1*3)), f: '+3sd'}, {v: (+gmean1 + +(gstndev1*2)), f: '+2sd'}, {v: (+gmean1 + +(gstndev1)), f: '+1sd'}, {v: gmean1 , f: 'mean'}, {v: (gmean1 - (gstndev1)), f: '-1sd'}, {v: (gmean1 - (gstndev1*2)), f: '-2sd'}, {v: (gmean1 - (gstndev1*3)), f: '-3sd'}],
						/*minValue: (gmean1 - (gstndev1*3)),
						maxValue: (+gmean1 + (+gstndev1*3)),*/
						//viewWindowMode: 'maximized',
						viewWindow: {
							max: (+gmean1 + (+gstndev1*3)),
							min: (gmean1 - (gstndev1*3))
						}
					},
					1: {title: '',
						baseline: gmean2,
						ticks: [{v: (+gmean2 + +(gstndev2*3)), f: ''}, {v: (+gmean2 + +(gstndev2*2)), f: ''}, {v: (+gmean2 + +(gstndev2)), f: ''}, {v: gmean2 , f: ''}, {v: (gmean2 - (gstndev2)), f: ''}, {v: (gmean2 - (gstndev2*2)), f: ''}, {v: (gmean2 - (gstndev2*3)), f: ''}],
						/*minValue: (gmean2 - (gstndev2*3)),
						maxValue: (+gmean2 + (+gstndev2*3)),*/
						//viewWindowMode: 'maximized',
						viewWindow: {
							max: (+gmean2 + +(gstndev2*3)),
							min: (gmean2 - (gstndev2*3))
						}
					},
					2: {title: '',
						baseline: gmean3,
						ticks: [{v: (+gmean3 + +(gstndev3*3)), f: ''}, {v: (+gmean3 + +(gstndev3*2)), f: ''}, {v: (+gmean3 + +(gstndev3)), f: ''}, {v: gmean3 , f: ''}, {v: (gmean3 - (gstndev3)), f: ''}, {v: (gmean3 - (gstndev3*2)), f: ''}, {v: (gmean3 - (gstndev3*3)), f: ''}],
						/*minValue: (gmean3 - (gstndev3*3)),
						maxValue: (+gmean3 + (+gstndev3*3)),*/
						//viewWindowMode: 'maximized',
						viewWindow: {
							max: (+gmean3 + +(gstndev3*3)),
							min: (gmean3 - (gstndev3*3))
						}
					}
				},
				chartArea:{
					top: '10%',
					width:'80%',
					height:'75%'
				},
				hAxis: {
					ticks: arrD[i],
					textStyle: {
						fontSize: 9
					},
				},			
				/*vAxis: {
					viewWindowMode: 'maximized',
				},		*/						
				pointSize: 5,
				annotations: {
					textStyle: {
					  fontSize: 7,
					  bold: false,
					  opacity: 0.0,
					},
					stem : {
						color: "white",
					}
				},
				logScale: false,
			};
		}
		
		
	
	
	var chart = new google.visualization.LineChart(ctx);
    chart.draw(data, options);
}

/*function showGivenData(){
	var givenDataContainer = document.getElementById('givenDataContainer');
	var gbtn = document.getElementById('gbtn');
	var level = document.getElementById('levelSelect');
	
	if (gbtn.checked){

		givenDataContainer.style.display= "block";
	}
	else{
		givenDataContainer.style.display= "none";
	}
}*/
/*function dataInput(inputType, containerType) {
	var entryType = document.getElementsByClassName("entryType");
	var resultContainer = document.getElementsByClassName("resultContainer");
	for (i = 0; i < entryType.length, i < resultContainer.length; i++) {
		entryType[i].style.display = "none"; 
		resultContainer[i].style.display = "none";
	}
	
	document.getElementById(inputType).style.display = "block";
	document.getElementById(containerType).style.display = "block";
}*/

$("#importExcelQC").click(function() {
	var entryType = document.getElementsByClassName("entryType");
	var resultContainer = document.getElementsByClassName("resultContainer");
	for (i = 0; i < entryType.length, i < resultContainer.length; i++) {
		entryType[i].style.display = "none"; 
		resultContainer[i].style.display = "none";
	}
	$("#excelImportContainer").css("display", "block");
	$("#givenResultContainer").css("display", "none");
	clearData();
	return false;
});

$("#manualInputQC").click(function() {
	var entryType = document.getElementsByClassName("entryType");
	var resultContainer = document.getElementsByClassName("resultContainer");
	for (i = 0; i < entryType.length, i < resultContainer.length; i++) {
		entryType[i].style.display = "none"; 
		resultContainer[i].style.display = "none";
	}
	$("#qcEnryContainer").css("display", "block");
	$("#givenResultContainer").css("display", "block");
	clearData();
	return false;
});


$("#gbtn").click(function() {
	if($("#gbtn").is(":checked")){
		if ($("#levelSelect").val() == 1) {
			$("#givenDataContainer").css("display", "block");
			$("#givenLevel1").css("display", "block");
		}
		else if ($("#levelSelect").val() == 2) {
			$("#givenDataContainer").css("display", "block");
			$("#givenLevel1").css("display", "block");
			$("#givenLevel2").css("display", "block");
			
		}
		else if ($("#levelSelect").val()== 3) {
			$("#givenDataContainer").css("display", "block");
			$("#givenLevel1").css("display", "block");
			$("#givenLevel2").css("display", "block");
			$("#givenLevel3").css("display", "block");
		}
	}
	else {
		$("#givenDataContainer").css("display", "none");
	}
	
	
});

$("#levelSelect").change(function() {
	if ($("#levelSelect").val() == 1){
		$("#level2Data").css("display", "none");
		$("#level3Data").css("display", "none");
	}
	else if ($("#levelSelect").val() == 2){
		$("#level2Data").css("display", "block");
		$("#level3Data").css("display", "none");
	}
	else if ($("#levelSelect").val() == 3){
		$("#level2Data").css("display", "block");
		$("#level3Data").css("display", "block");
	}
});

$('#printButton').click(function() {
	print() 
});
