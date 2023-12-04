$(document).ready(function() {

	// Set the token so that we are not rejected by server
	var csrf_token = $('meta[name=csrf-token]').attr('content');
	 // Configure ajaxSetup so that the CSRF token is added to the header of every request
	$.ajaxSetup({
	    beforeSend: function(xhr, settings) {
	        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
	            xhr.setRequestHeader("X-CSRFToken", csrf_token);
	        }
	    }
	});

	$("button.follow").on("click", function() {
        var clicked_obj = $(this);

        // Which post was used?
        var post_id = $(this).attr('id');

        $.ajax({
            url: '/follow',
            type: 'POST',
            data: JSON.stringify({ post_id: post_id }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(response) {
                console.log(response);

                // Change the button text but make sure the font is the same
                clicked_obj.children()[0].innerHTML = response.btntxt;  
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
});