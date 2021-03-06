$(function() {
	$(window).load(function(){
		$(".be-loader").fadeOut("slow");
	});
	$('#complaints-container').mixItUp();
	$('.trai-info').slick({
	  slidesToScroll: 1,
	  autoplay: true,
	  autoplaySpeed: 2000,
	  dots: true,
  	  infinite: true,
  	  cssEase: 'linear'
	});
	$('.sign-up-button').bind('click', function(e){
		e.preventDefault();
		$(".error").remove();
		var signup_sub_but = $(this);
		var form_id = "#sign-up-form";
		var signup_url = $(form_id).attr("action");
		signup_sub_but.attr("disabled","disabled");
		$.ajax(
		{
			type: 'POST',
			url:signup_url,
			data:$(form_id).serialize(),
			success:function(response)
			{
				signup_sub_but.removeAttr("disabled","disabled");
				location.href = response.location;
		
			},
			error:function(response)
			{
				console.log("error");
				console.log(response);
				for(key in response.responseJSON.form_errors){
					if(key == '__all__')
						$(form_id + ' div.box-body').append('<span class="error">'+response.responseJSON.form_errors[key]+'</span>');
					else
						$("#"+key).parents('div.form-group').append('<span class="error">'+response.responseJSON.form_errors[key]+'</span>');
				}
				signup_sub_but.removeAttr("disabled","disabled");
		
			}
		});  
	});
	$('.sign-in-button').bind('click', function(e){
		e.preventDefault();
		$(".error").remove();
		var signin_sub_but = $(this);
		var form_id = "#sign-in-form";
		var signin_url = $(form_id).attr("action");
		signin_sub_but.attr("disabled","disabled");
		$.ajax(
		{
			type: 'POST',
			url:signin_url,
			data:$(form_id).serialize(),
			success:function(response)
			{
				signin_sub_but.removeAttr("disabled","disabled");
				location.href = response.location;
		
			},
			error:function(response)
			{
				console.log("error");
				console.log(response);
				for(key in response.responseJSON.form_errors){
					if(key == '__all__')
						$(form_id + ' div.box-body').append('<span class="error">'+response.responseJSON.form_errors[key]+'</span>');
					else
						$("#"+key).parents('div.form-group').append('<span class="error">'+response.responseJSON.form_errors[key]+'</span>');
				}
				signin_sub_but.removeAttr("disabled","disabled");
		
			}
		});  
	});
	$('.create-complaint-button').bind('click', function(e){
		e.preventDefault();
		$(".error").remove();
		var but = $(this);
		var form_id = "#create-complaint-form";
		var url = $(form_id).attr("action");
		but.attr("disabled","disabled");
		$.ajax(
		{
			type: 'POST',
			url:url,
			data:$(form_id).serialize(),
			success:function(response)
			{
				// console.log(response);
				if(jQuery.isEmptyObject( response )){
					//redirect
					location.href = "/do-it-yourself/";
				}else{
					for(key in response){
						$("#"+key).parents('div.form-group').append('<span class="error">'+response[key]+'</span>');
					}
				}
				but.removeAttr("disabled","disabled");		
			},
			error:function(response)
			{
				console.log("error");
				console.log(response);
				but.removeAttr("disabled","disabled");
		
			}
		});  
	});
	$(".filter-select").change(function(){
		var but_id = $(this).val() + "-filter-but";
		$("#"+but_id).click();
	});
});
