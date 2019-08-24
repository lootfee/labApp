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
	
	$("#hemoglobin").keyup(function() {
		$("#hgb_unit").css("display", "inline-flex");
	});
	$("#hematocrit").keyup(function() {
		$("#hct_unit").css("display", "inline-flex");
	});
	$("#rbc").keyup(function() {
		$("#rbc_unit").css("display", "inline-flex");
	});
	
	$("#calc_indices").click(function() {
		var hgb = $("#hemoglobin").val();
		var hct = $("#hematocrit").val();
		var rbc = $("#rbc").val();
		
		$("#mcv").val(N((hct*10) / rbc, 1) + " fL");
		$("#mch").val(N((hgb*10) / rbc, 1) + " pg");
		$("#mchc").val(N((hgb*100) / hct, 1) + " g/dL");
		
	});
});