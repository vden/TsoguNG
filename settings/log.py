from django.utils.termcolors import colorize
import logging
import logging.handlers

LOG_COLOR = {
	'DEBUG':'blue',
	'INFO':'yellow',
	'ERROR':'red',
	'WARNING':'magenta',
}

class ColoredFormatter(logging.Formatter):
	def format(self, record):
		result = logging.Formatter.format(self, record)
		if record.levelname in LOG_COLOR:
			result = colorize(result, fg=LOG_COLOR[record.levelname])
		return result

formatter = ColoredFormatter('%(asctime)s %(levelname)-8s %(message)s', '%Y-%m-%d %H:%M:%S')

console = logging.StreamHandler()
console.setFormatter(formatter)

file = logging.handlers.RotatingFileHandler('logs/log', 'a', 5*1024*1024, 4)
file.setFormatter(formatter)

logging.root.addHandler(console)
logging.root.addHandler(file)
logging.root.setLevel(logging.DEBUG)

logging.tsogung_config = True
logging.info('SET LOGGING CONF')
