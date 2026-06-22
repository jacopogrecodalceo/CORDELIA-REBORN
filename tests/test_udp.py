import socket
import pytest
from pythonosc.udp_client import SimpleUDPClient

from cordelia.udp import UDPRouter


@pytest.fixture
def router():
   test_ports = {
      12001: "A",
      12002: "B",
   }

   r = UDPRouter(test_ports)
   r.open_ports()
   yield r

   for sock in r.socket_map:
      sock.close()
      
def test_single_message(router):
   client = SimpleUDPClient("127.0.0.1", 12001)

   client.send_message("/test", "hello")

   messages = router.receive()

   assert len(messages) == 1

   direction, msg = messages[0]

   assert direction == "A"
   assert "hello" in msg
   
def test_multiple_ports(router):
   client_a = SimpleUDPClient("127.0.0.1", 12001)
   client_b = SimpleUDPClient("127.0.0.1", 12002)

   client_a.send_message("/a", "msg_a")
   client_b.send_message("/b", "msg_b")

   messages = router.receive()

   directions = {m[0] for m in messages}

   assert directions == {"A", "B"}