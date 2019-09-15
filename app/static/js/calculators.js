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
	
	//////Lipid Profile///////
	$("#lp_mmoll").click(function() {
		$(".data").each(function() {
			this.value = "";
			$(".units").css("display", "none");
		});
		
		$("#cholesterol").prop("placeholder", "mmol/L");
		$("#hdl").prop("placeholder", "mmol/L");
		$("#ldl").prop("placeholder", "mmol/L");
		$("#vldl").prop("placeholder", "mmol/L");
		$("#trig").prop("placeholder", "mmol/L");
		$("#ldlc").prop("placeholder", "mmol/L");
	});	

	$("#lp_mgdl").click(function() {
		$(".data").each(function() {
			this.value = "";
			$(".units").css("display", "none");
		});
		
		$("#cholesterol").prop("placeholder", "mg/dL");
		$("#hdl").prop("placeholder", "mg/dL");
		$("#ldl").prop("placeholder", "mg/dL");
		$("#vldl").prop("placeholder", "mg/dL");
		$("#trig").prop("placeholder", "mg/dL");
		$("#ldlc").prop("placeholder", "mg/dL");
	});
	
	
	$("#cholesterol").keyup(function() {
		if($("#lp_mmoll").is(":checked")){
			$("#chol_mmoll").css("display", "inline-flex");
		}
		else if($("#lp_mgdl").is(":checked")){
			$("#chol_mgdl").css("display", "inline-flex");
		}		
	});
	$("#hdl").keyup(function() {
		if($("#lp_mmoll").is(":checked")){
			$("#hdl_mmoll").css("display", "inline-flex");
		}
		else if($("#lp_mgdl").is(":checked")){
			$("#hdl_mgdl").css("display", "inline-flex");
		}
	});
			
	$("#ldl").keyup(function() {
		if($("#lp_mmoll").is(":checked")){
			$("#ldl_mmoll").css("display", "inline-flex");
		}
		else if($("#lp_mgdl").is(":checked")){
			$("#ldl_mgdl").css("display", "inline-flex");
		}
	});
	
	$("#trig").keyup(function() {
		if($("#lp_mmoll").is(":checked")){
			$("#trig_mmoll").css("display", "inline-flex");
		}
		else if($("#lp_mgdl").is(":checked")){
			$("#trig_mgdl").css("display", "inline-flex");
		}
	});
			
	$("#calc_lipid_profile").click(function(){
		if($("#lp_mmoll").is(":checked")){
			var vldl = $("#trig").val()/2.2;
			$("#vldl_mmoll").css("display", "inline-flex");
		}
		else if ($("#lp_mgdl").is(":checked")){
			var vldl = $("#trig").val()/5;
			$("#vldl_mgdl").css("display", "inline-flex");
		}
			vldl = N(vldl, 2);
			$("#vldl").val(vldl);
			
			var ldlc = $("#cholesterol").val() - $("#hdl").val() - vldl;
			ldlc = N(ldlc, 2);
			$("#ldlc").val( ldlc );
			if($("#lp_mmoll").is(":checked")){
				$("#ldlc_mmoll").css("display", "inline-flex");
			}
			else if ($("#lp_mgdl").is(":checked")){
				$("#ldlc_mgdl").css("display", "inline-flex");
			}
			if( $("#ldl").val().length === 0 ){
				var ldl = ldlc; 
			}
			else {
				var ldl = $("#ldl").val();
			}
			var chol_hdl = $("#cholesterol").val()/ $("#hdl").val();
			chol_hdl = N(chol_hdl, 2);
			$("#cholhdl").val(chol_hdl);
			var hdl_ldl = $("#hdl").val()/ ldl;
			hdl_ldl = N(hdl_ldl, 2);
			$("#hdlldl").val(hdl_ldl);
			var ldl_hdl = ldl / $("#hdl").val();
			ldl_hdl = N(ldl_hdl, 2);
			$("#ldlhdl").val(ldl_hdl);
			var trig_hdl = $("#trig").val()/ $("#hdl").val();
			trig_hdl = N(trig_hdl, 2);
			$("#trighdl").val(trig_hdl);
		
	});
			
	
	
	
	////////HbA1c///////
	$("#hba1c_input").keyup(function() {
		var calcA1c = ($("#hba1c_input").val() * 28.7) - 46.7;
		calcA1c = N(calcA1c, 2);
		$("#eag").val(calcA1c + " mg/dL");
		$("#hba1cUnit").css("display", "inline-flex");
	});
	
	$("#hba1c_mmoll").change(function() {
		$(".data").each(function() {
			this.value = "";
			$(".units").css("display", "none");
		});
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
		$(".data").each(function() {
			this.value = "";
			$(".units").css("display", "none");
		});
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


	