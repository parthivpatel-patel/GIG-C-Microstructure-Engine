# Fixture child-process network boundary,not application runtime configuration.
import socket
_original=socket.socket.connect
_original_ex=socket.socket.connect_ex
def permitted(address):
 if isinstance(address,str):return True # local Unix domain socket
 return isinstance(address,tuple)and address[0]in ('127.0.0.1','::1','localhost')
def connect(self,address):
 if not permitted(address):raise AssertionError('SPRINT3_EXTERNAL_NETWORK_FORBIDDEN')
 return _original(self,address)
def connect_ex(self,address):
 if not permitted(address):raise AssertionError('SPRINT3_EXTERNAL_NETWORK_FORBIDDEN')
 return _original_ex(self,address)
socket.socket.connect=connect;socket.socket.connect_ex=connect_ex
