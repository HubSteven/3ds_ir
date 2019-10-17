import serial
import crc8
from colorama import Fore, Back, Style 
ser = serial.Serial('/dev/ttyUSB0',115200)

def padded_hex(value):
 return '0x{0:0{1}X}'.format(value,2)

while True:
 x=ser.read()
 if padded_hex(ord(x))!='0xA5':
  print(Fore.GREEN+padded_hex(ord(x))),
 else:
  hash = crc8.crc8()
  hash.update(x)
  print("")
  print(Fore.RED+padded_hex(ord(x))),
  print(Style.RESET_ALL),
  x=ser.read()
  hash.update(x) 
  print(padded_hex(ord(x))),
  x=ser.read()
  hash.update(x)
  print(padded_hex(ord(x))),
  if ord(x) & (1<<6):
   short_frame=False
  else:
   short_frame=True
  payload_size=0b00111111 & ord(x)
  if short_frame==False:
   x=ser.read()
   print(padded_hex(ord(x))),
   hash.update(x)
   payload_size*=256
   payload_size+=ord(x)
  xorval_higher=0xE9
  xorval_lower=0x63
  for x in range(payload_size/2):
   a=ser.read()
   hash.update(a)
   output=ord(a)^xorval_higher
   xorval_higher=ord(a)
   if x>3:
    print(Back.YELLOW+Fore.BLACK+padded_hex(output)),
   else:
    print(Back.WHITE+Fore.BLACK+padded_hex(output)),
   a=ser.read()
   hash.update(a)
   output=ord(a)^xorval_lower
   xorval_lower=ord(a)
   if x>3:
    print(Back.YELLOW+Fore.BLACK+padded_hex(output)),
   else:
    print(Back.WHITE+Fore.BLACK+padded_hex(output)),
  if (payload_size%2)!=0:
   a=ser.read()
   hash.update(a)
   output=ord(a)^xorval_higher
   xorval_higher=ord(a)
   if x>3:
    print(Back.YELLOW+Fore.BLACK+padded_hex(output)),
   else:
    print(Back.WHITE+Fore.BLACK+padded_hex(output)),
  x=ser.read()
  if x==hash.digest():
   print(Back.GREEN+padded_hex(ord(x))+Style.RESET_ALL)
  else:
   print(Back.RED+padded_hex(ord(x))+Style.RESET_ALL)

