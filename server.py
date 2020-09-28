import random
import socket
import time
from _thread import *
import threading
from datetime import datetime
import json

clients_lock = threading.Lock()
connected = 0

clients = {}
# addr = IP and PORT, 2 VALUES
# clients[addr] = {"lastBeat: 10:50pm, "color: 0"}

def connectionLoop(sock):
   while True:
      data, addr = sock.recvfrom(1024)
      data = str(data)
      if addr in clients:
         if 'heartbeat' in data:
            clients[addr]['lastBeat'] = datetime.now()
      else:
         if 'connect' in data:
            clients[addr] = {}
            clients[addr]['lastBeat'] = datetime.now()
            clients[addr]['color'] = 0
            
            playerlist = {"list": []}
            for c in clients:
               templist = {"player":{"id":str(c)}}
               playerlist['list'].append(templist)

            plist = json.dumps(playerlist)
            sock.sendto(bytes(plist,'utf8'), (addr[0],addr[1]))

            message = {"cmd": 0,"player":{"id":str(addr)}}
            m = json.dumps(message)
            for c in clients:
               sock.sendto(bytes(m,'utf8'), (c[0],c[1]))

def cleanClients():
   while True:
      for c in list(clients.keys()):
         if (datetime.now() - clients[c]['lastBeat']).total_seconds() > 5:
            print('Dropped Client: ', c)
            clients_lock.acquire()
            del clients[c]
            clients_lock.release()
      time.sleep(1)

def gameLoop(sock):
   while True:
      # addr = IP and PORT, 2 VALUES
      # clients[addr 1 = 0] = {"lastBeat: 10:50pm, "color: {"R": random.random(), "G": random.random(), "B": random.random()}"}
     
      # clients[addr 2 = 1] = {"lastBeat: 10:45pm, "color: 2"}
      
      # GameState = {"cmd": 1, "players": []}
      #clients[c]['color']['R'] = 5

      GameState = {"cmd": 1, "players": []}
      clients_lock.acquire()
      print (clients)
      for c in clients: # we only have 1 user, c = 0
         player = {}
         clients[c]['color'] = {"R": random.random(), "G": random.random(), "B": random.random()}
         player['id'] = str(c)
         player['color'] = clients[c]['color']
         GameState['players'].append(player)
      s=json.dumps(GameState)
      print(s)
      for c in clients:
         sock.sendto(bytes(s,'utf8'), (c[0],c[1]))
      clients_lock.release()
      time.sleep(1)

def main():
   port = 12345
   s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   s.bind(('', port))
   start_new_thread(gameLoop, (s,))
   start_new_thread(connectionLoop, (s,))
   start_new_thread(cleanClients,())
   while True:
      time.sleep(1)

if __name__ == '__main__':
   main()
