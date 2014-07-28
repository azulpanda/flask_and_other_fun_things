$(document).ready(function(){
	$('#email_input').change(function(){
		var email = $('#email_input').val();

		$.ajax({
			url:'/email_check',
			type:'POST',
			data:{'email':email},
			success:function(response){
				var result = $.parseJSON(response);
				console.log(result['message']);
			},
			error:function(){
				console.log('error');
			}
		});
	});
});