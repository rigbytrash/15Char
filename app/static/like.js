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

	$("button.like").on("click", function() {
        var clicked_obj = $(this);

        // Which post was liked/unliked?
        var post_id = $(this).attr('id');

        $.ajax({
            url: '/like',
            type: 'POST',
            data: JSON.stringify({ post_id: post_id }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(response) {
                console.log(response);

                // Update the html rendered to reflect new count
                clicked_obj.children()[1].innerHTML = "(" + response.likes +")";

                // Update the SVG image based on whether the user has liked the post
                var svgSrc = response.user_has_liked ? clicked_obj.data('liked-src') : clicked_obj.data('unliked-src');
				console.log(response.user_has_liked);
				console.log(svgSrc);
                clicked_obj.children('img').attr('src', svgSrc);
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
});