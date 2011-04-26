
"""
	Simple Django-like signal working over AMQP

	@author: Vlasov Dmitry
	@contact: scailer@veles.biz
	@contact: scailer@tsogu.ru
	@organization: TSOGU
	@status: testing
	@version: 1.0$
"""

from django.dispatch import Signal
from carrot.connection import DjangoBrokerConnection
from carrot.messaging import Consumer, Publisher
import threading
import settings


class ConsumerLoop(threading.Thread):
	""" Consumer listener loop. Wait when signal came."""
	consumer = None

	def run(self):
		self.consumer.wait()


class SignalAMQP(Signal):
	def __init__(self, exchange, queue, routing_key=None, debug=None):
		"""
			Initialise signal, conection, exchange, queue and run consumer 
			@return: Django Signal like object.

			@param exchange: name of exchange for this signal
			@type exchange: string

			@param queue: name queue of this signal
			@type queue: string

			@param routing_key: name of routing_key betwen exchange and queue of this signal
			@type routing_key: string

			@param debug: debug flag
			@type debug: bool

			Example:
			>>> amqp_signal_1 = SignalAMQP(exchange="test1", queue="q1")
			>>> amqp_signal_2 = SignalAMQP(exchange="test2", queue="q2")
			>>> amqp_signal_1.queue_bind(['q2'])
			>>> def amqp_handler(sender, **kwargs):
				print "AMPQ handler:", sender, kwargs
			>>> amqp_signal_2.connect(amqp_handler, sender=None)
			>>> amqp_signal_1.send("Hello world!")
		"""
		super(SignalAMQP, self).__init__(providing_args=["message"])

		self.exchange = exchange
		self.queue = queue
		self.routing_key = routing_key
		self.debug = debug is None and settings.DEBUG or debug

		self.conn = DjangoBrokerConnection()
		self.publisher = Publisher(connection=self.conn, exchange=self.exchange, exchange_type="fanout",\
							routing_key=self.routing_key)
		self.consumer = Consumer(connection=self.conn, queue=self.queue, exchange_type="fanout",\
					exchange=self.exchange, routing_key=self.routing_key)
		self.consumer.register_callback(self.callback)

		self.cl = self.listen()

	def send(self, message, **kw):
		""" Transfer message to bus. Message can be any simple python type. """
		self.publisher.send(message, **kw)

	def callback(self, message_data, message):
		""" Consumer callback function. Send Django singnal."""
		try:
			sender = message_data['sender'] 
		except:
			sender = None
		super(SignalAMQP, self).send(sender=sender, message_data=message_data, message=message)
		message.ack()
		if self.debug:
			print "AMPQ CALLBACK: sender=", sender, "messege=", message_data, message
		return True

	def get_backend(self):
		return self.conn.get_backend_cls()(DjangoBrokerConnection())

	def queue_bind(self, queue_list):
		""" Bind another queues to current exchange """
		routing_keys = []
		backend = self.get_backend()
		for x in queue_list:
			backend.queue_bind(queue=x, exchange=self.exchange, \
						routing_key='%s_%s' % (self.exchange, x))
			routing_keys.append('%s_%s' % (self.exchange, x))
		return routing_keys

	def listen(self):
		""" Run consumer loop thread """
		cl = ConsumerLoop()
		cl.consumer = self.consumer
		cl.start()
		return cl

	def stop(self):
		""" Unactivate this signal """
		self.conn.close()


#amqp_signal = SignalAMQP(exchange="tsogu", queue="cache")#, routing_key="tsogu_cache")

def amqp_handler(sender, **kwargs):
	print "AMPQ handler:", sender, kwargs
#amqp_signal.connect(amqp_handler, sender=None)#, exchange="tsogu", queue="cache", routing_key="spec")


