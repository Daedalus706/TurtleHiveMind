from websockets import InvalidStatus
from websockets.sync.client import connect

try:
    ws = connect("ws://magnus-rpg.de:5020")
    ws.send('{"type": "shutdown"}')
    ws.close()
except (InvalidStatus, TimeoutError) as e:
    pass