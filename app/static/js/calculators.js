$(document).ready(function() {
	function N(id, places) { 
		return +(Math.round(id + "e+" + places)  + "e-" + places);
	 }
	
	$(".clear_button").click(function() {
		$(".data").each(function() {
			this.value = "";
			$(".units").css("display", "none");
		});
	});
	
	$("#hba1c_input").keyup(function() {
		var calcA1c = ($("#hba1c_input").val() * 28.7) - 46.7;
		calcA1c = N(calcA1c, 2);
		$("#eag").val(calcA1c + " mg/dL");
		$("#hba1cUnit").css("display", "inline-flex");
	});
	
	$("#hba1c_mmoll").change(function() {
		if(this.checked){
			$("#eag").prop("placeholder", "mmol/L");
				$("#hba1c_input").keyup(function() {
				var calcA1c= ($("#hba1c_input").val() * 1.59) - 2.59;
				calcA1c = N(calcA1c, 2);
				$("#eag").val(calcA1c + " mmol/L");
				$("#hba1cUnit").css("display", "inline-flex");
			});
		}
	});
	$("#hba1c_mgdl").change(function() {
		if(this.checked){
			$("#eag").attr("placeholder", "mg/dL");
				$("#hba1c_input").keyup(function() {
				var calcA1c = ($("#hba1c_input").val() * 28.7) - 46.7;
				calcA1c = N(calcA1c, 2);
				$("#eag").val(calcA1c + " mg/dL");
				$("#hba1cUnit").css("display", "inline-flex");
			});
		}
	});
	
	
});