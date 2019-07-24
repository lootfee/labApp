$(document).ready(function() {
    $("#reg_company_form").hide();
	$("#register_company").click(function(){
		$("#reg_company_form").show();
	});
});

$(document).ready(function() {
    $("#edit_company_profile_form").hide();
	$("#edit_company_profile").click(function(){
		$("#edit_company_profile_form").show();
		$("#company_profile").hide();
	});
});

$(document).ready(function() {
	$("#cancel").click(function(){
		window.history.go(-1);
		return false;
	});
	
	$("#open_supplier_sidenav").click(function() {
		$("#supplier_sidenav").css( "width", "350px");
	});
	
	$("#open_product_sidenav").click(function() {
		$("#product_sidenav").css( "width", "80%");
	});
	$("#open_orders_sidenav").click(function() {
		$("#create_orders_sidenav").css( "width", "40%");
	});
	
	
	$(".hide_sidenav").click(function() {
		$(".sidenav").css( "width", "0");
	});
});




$(document).ready(function() {
	$("#qc_admin").change(function(){
		if (this.checked) {
			$("#qc_access").prop("disabled", true);
			$("#qc_access").prop("checked", true);
		}
		else {
			$("#qc_access").prop("disabled", false);
			$("#qc_access").prop("checked", false);
		}
	});
});

$(document).ready(function() {
	$("#inv_admin").change(function(){
		if (this.checked) {
			$("#inv_access").prop("checked", true);
			$("#inv_access").prop("disabled", true);
		}
		else {
			$("#inv_access").prop("checked", false);
			$("#inv_access").prop("disabled", false);
		}
	});
});

$(document).ready(function() {
    $("#super_admin").change(function() {
        if (this.checked) {
            $(".single_check").each(function() {
                this.checked=true;
				$(".single_check").prop("disabled", true);
            });
        } else {
            $(".single_check").each(function() {
                this.checked=false;
				$(".single_check").prop("disabled", false);
            });
        }
    });

    $(".single_check").click(function () {
        if ($(this).is(":checked")) {
            var isAllChecked = 0;
            $(".single_check").each(function() {
                if (!this.checked)
                    isAllChecked = 1;
            });
            if (isAllChecked == 0) {
                $("#super_admin").prop("checked", true);
				$(".single_check").prop("disabled", true);
            }     
        }
        else {
            $("#super_admin").prop("checked", false);
        }
    });
	$(".double_check").click(function () {
        if ($(this).is(":checked")) {
            var isAllChecked = 0;
            $(".double_check").each(function() {
                if (!this.checked)
                    isAllChecked = 1;
            });
            if (isAllChecked == 0) {
                $("#super_admin").prop("checked", true);
				$(".double_check").prop("disabled", true);
            }     
        }
        else {
            $("#super_admin").prop("checked", false);
        }
    });
	
	
	
});