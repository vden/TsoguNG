$(document).ready(function(){
	$('.datepick').datepicker({
		yearRange: "1930:2010",
		defaultDate: "y",
		changeMonth: true,
		changeYear: true,
		showAnim: 'fadeIn',
		clearText: 'Очистить', // Display text for clear link
		clearStatus: 'Стереть текущую дату', // Status text for clear link
		closeText: 'Закрыть', // Display text for close link
		closeStatus: 'Закрыть без сохранения', // Status text for close link
		prevText: '&#x3c;Пред', // Display text for previous month link
		prevStatus: 'Предыдущий месяц', // Status text for previous month link
		nextText: 'След&#x3e;', // Display text for next month link
		nextStatus: 'Следующий месяц', // Status text for next month link
		currentText: 'Сегодня', // Display text for current month link
		currentStatus: 'Текущий месяц', // Status text for current month link
		monthNames: ['Январь','Февраль','Март','Апрель','Май','Июнь',
		'Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь'], // Names of months for drop-down and formatting
		monthNamesShort: ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек'], // For formatting
		monthStatus: 'Показать другой месяц', // Status text for selecting a month
		yearStatus: 'Показать другой год', // Status text for selecting a year
		weekHeader: 'Нед', // Header for the week of the year column
		weekStatus: 'Неделя года', // Status text for the week of the year column
		dayNames: ['Воскресенье', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота'], // For formatting
		dayNamesShort: ['Вск', 'Пнд', 'Втр', 'Срд', 'Чтв', 'Птн', 'Сбт'], // For formatting
		dayNamesMin: ['Вс','Пн','Вт','Ср','Чт','Пт','Сб'], // Column headings for days starting at Sunday
		dayStatus: 'Установить первым днем недели', // Status text for the day of the week selection
		dateStatus: 'Выбрать день, месяц, год', // Status text for the date selection
		dateFormat: 'dd.mm.yy', // See format options on parseDate
		firstDay: 1, // The first day of the week, Sun = 0, Mon = 1, ...
		initStatus: 'Выбрать дату', // Initial Status text on opening
		isRTL: false // True if right-to-left language, false if left-to-right
	});
});
