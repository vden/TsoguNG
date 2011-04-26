tinyMCE.init({
	// General options
	mode : "exact",
	elements : "id_text",
	theme : "advanced",
	language:"ru",
	plugins : "safari,spellchecker,pagebreak,style,layer,table,save,advhr,advimage,advlink,iespell,inlinepopups,insertdatetime,preview,media,searchreplace,print,contextmenu,paste,fullscreen,noneditable,visualchars,nonbreaking,xhtmlxtras,template,images",

	// Theme options
	theme_advanced_buttons1 : "bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justifyfull,|,formatselect,fontsizeselect,|,cut,copy,paste,pastetext,pasteword,|,bullist,numlist,",
	theme_advanced_buttons2 : ",code,|,undo,redo,|,link,|,tablecontrols,|,outdent,indent,|,forecolor,backcolor,",
	theme_advanced_buttons3 : "",
//	theme_advanced_buttons3 : "tablecontrols,|,hr,removeformat,visualaid,|,sub,sup,|,charmap,iespell,advhr,|,print,",
//	theme_advanced_buttons4 : "spellchecker,|,cite,abbr,acronym,del,ins,|,visualchars,nonbreaking,blockquote,pagebreak,|,insertfile,insertimage,|,forecolor,backcolor,|,fullscreen",
	theme_advanced_toolbar_location : "top",
	theme_advanced_toolbar_align : "left",
	theme_advanced_statusbar_location : "bottom",
	theme_advanced_resizing : true,
	relative_urls : false,

//	Example content CSS (should be your site CSS)
	content_css : "/media/css/",

//	Drop lists for link/image/media/template dialogs
	template_external_list_url : "js/template_list.js",
	external_link_list_url : "js/link_list.js",
	external_image_list_url : "js/image_list.js",
		 media_external_list_url : "js/media_list.js"
	// Replace values for the template plugin
//	template_replace_values : {
//	username : "Some User",
//	staffid : "991234"
//	}
//NOTE: Remember to remove the last "," character in the options list. In some versions of Microsoft Internet Explorer, not removing the final comma will cause tinyMCE to be initialized with the default settings.
});
