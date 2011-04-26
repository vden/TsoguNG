// JavaScript Document
function cssmenuhover()
{
        if(!document.getElementById("cssmenu"))
                return;
        var lis = document.getElementById("cssmenu").getElementsByTagName("LI");
        for (var i=0;i<lis.length;i++)
        {
            lis[i].onmouseover=function(){this.className+=" iehover";};
            lis[i].onmouseout=function() {this.className=this.className.replace(new RegExp(" iehover\\b"), "");};
        }
}
if (window.attachEvent)
        window.attachEvent("onload", cssmenuhover);

function search_lookup(inputString) {
    if (inputString.length < 3) {
	$('#suggestions').fadeOut(); // Hide the suggestions box
    } else {
	if ((inputString.length+1)%2 != 0) return;
	$.post("/portal/lookup_search/", {search_word: ""+inputString+""}, function(data) { // Do an AJAX call
	    $('#suggestions').fadeIn(); // Show the suggestions box
	    $('#suggestions').html(data); // Fill the suggestions box
	});
    }
}

function set_bids_position() {
        $('#bids').val($.map($('input[name=ids:list]'), function (data){return data.value }).join(','));
        return true
}

