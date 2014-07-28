var email_input = document.getElementById("email_input");
var password_input = document.getElementById("password_input");
var password_check_input = document.getElementById("password_check_input");
email_input.onblur = function(){
	var email = email_input.value;
	if (Boolean(email.match(/^[a-zA-z._0-9]+@[a-zA-Z0-9-]+\.(com|net|ac\.kr)$/)))
	{
		email_input.removeAttribute("class");
		document.getElementById("email_error").style.display = "none";
		$.ajax({
			url:'/email_check',
			type:'POST',
			data:{'email':email},
			success:function(response)
			{
				if (response=="taken")
				{
					email_input.setAttribute('class', 'invalid');
					document.getElementById("email_taken").style.display = "inline";
				}
				else
				{
					document.getElementById("email_taken").style.display = "none";
				}
			},
			error:function()
			{
				console.log('error');
			}
		});
	}
	else
	{
		email_input.setAttribute('class', 'invalid');
		document.getElementById("email_error").style.display = "inline";
		document.getElementById("email_taken").style.display = "none";
	}

};
password_input.onblur = function(){
	var password = password_input.value;
	if (Boolean(password.match(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*\W).{8,20}$/)))
	{
		password_input.removeAttribute("class");
		document.getElementById("password_error").style.display = "none";
	}
	else
	{
		password_input.setAttribute('class', 'invalid');
		document.getElementById("password_error").style.display = "inline";
	}
};
password_check_input.onblur = function(){
	var password = password_input.value;
	var password_check = password_check_input.value;
	if (password === password_check)
	{
		password_check_input.removeAttribute("class");
		document.getElementById("password_check_error").style.display = "none";
	}
	else
	{
		password_check_input.setAttribute('class', 'invalid');
		document.getElementById("password_check_error").style.display = "inline";
	}
}