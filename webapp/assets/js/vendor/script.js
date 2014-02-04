$(function() {
	var articles = $(".articles");
	var scroll_content = articles.clone();
	$('.scroller-inner').html(scroll_content.html());
});