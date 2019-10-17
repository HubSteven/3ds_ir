import serial
import crc8
import random
from colorama import Fore, Back, Style 
from time import sleep
AMIIBO_ID=[0x04,0x9D,0xf3,0xda,0x5e,0x5c,0x80]
AMIIBO_SIG=[0xFF]*32
#AMIIBO_SIG=[0xA3,0x45,0xD9,0xB5,0x76,0xC7,0x9E,0x5E,0xF5,0x9C,0x4B,0x0A,0xC4,0x55,0x48,0x00,0x08,0xCC,0x5D,0xD2,0x6F,0x39,0xD2,0xFB,0xAF,0x40,0x46,0xEC,0x0C,0x67,0xA0,0x74]

class l3_message:
 def __init__(self,payload,mystery_bit=False):
  self.payload=payload
  self.mystery_bit=mystery_bit

#layer 3 nfc data dump wrapper
def dump_response(nfc_binary_file,id_byte):
 f = open(nfc_binary_file,"r")
 nfc_data=f.read()
 f.close()
 l3_data=l3_message([0x02,0x05,id_byte,0x00,0x00,0x00,0x01,0x01,0x02,0x00,0x07]+AMIIBO_ID+[0x00,0x00,0x00,0x00,0x04,0x04, 0x02,0x01,0x00,0x11,0x03,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00, 0x03,0x00,0x39,0x3A,0x73,0x74,0x86,0x00,0x00]+map(ord, nfc_data)+[0x00]*420+AMIIBO_SIG+[0x00])
 return l3_data
 
def open_port(port):
 global ser 
 ser= serial.Serial(port,115200)

#write raw serial debug data
def file_write(data):
 data=data
 #print data

#layer 3 master side messages
CONNECTION_REQUEST,DISCONNECTION_REQUEST,VERSION_REQUEST,MYSTERY_REQUEST,SELECTED_MEMORY_PAGES,WRITE_DATA,DUMP_DONE,MEMORY_DUMP_REQUEST=range(8)

def get_message():
 l2,l3=get_rawdata()
 global l3_raw_data
 l3_raw_data=l3[:]#needed for mem_dump function
 global connection_identifier
 connection_identifier=l2[5]
 if (l2[7]==0x0C):
  return CONNECTION_REQUEST
 elif (l2[7]==0x0A):
  return DISCONNECTION_REQUEST
 if ((l2[7]&~0x10)==0):#mask out mystery bit
  global l3_message_number
  l3_message_number=l3[0]
  #print "L3:",l3
  #print "l3 bits:", l3[2:4]
  if(l3[2:4]==[0x00,0x03]):
   #print "VERSION_REQUEST"
   return VERSION_REQUEST
  elif(l3[2:4]==[0x01,0x00]):
   #print "MYSTERY_REQUEST"
   return MYSTERY_REQUEST
  elif(l3[2:4]==[0x02,0x06]):
   ##print("SELECTED_MEMORY_PAGES")
   return SELECTED_MEMORY_PAGES
  elif(l3[2:4]==[0x02,0x04]):
   return MEMORY_DUMP_REQUEST
  elif(l3[2:4]==[0x02,0x07]):
   return WRITE_DATA
  elif(l3[2:4]==[0x02,0x02]):
   return DUMP_DONE

def mem_dump_write(nfc_binary_file):
 f = open(nfc_binary_file,"r")
 nfc_data=f.read()
 f.close()
 global l3_raw_data
 nfc_data=map(ord,nfc_data)
 #print "nfc_data:",nfc_data
 nfc_data[128:520]=l3_raw_data[277:453]+l3_raw_data[519:735]
 nfc_data[16:52]=l3_raw_data[1006:1010]+l3_raw_data[35:67]
 nfc_data=''.join([chr(item) for item in nfc_data])
 #print "nfc_data1:",nfc_data
 f = open(nfc_binary_file,"wb")
 f.write(nfc_data)
 f.close()

#exor encryption of layer 2 and 3 data
def exor_encrypt(data):
 #print "l2 en l3:", [hex(x) for x in data]
 xorval_higher=0xE9
 xorval_lower=0x63
 for x in range(0,len(data)-1,2):
  data[x]^=xorval_higher
  xorval_higher=data[x]
  if (x+1 > (len(data)-1)):#check if packet is uneven
   break
  data[x+1]^=xorval_lower
  xorval_lower=data[x+1]
 return data

#layer 1 and 2 wrapper
def layer_wrapper(master_identifier,slave_identifier,l2,l3_seq=[],l3=[],mystery_bit=False):
 output=[]
 for x in range(4):
  output.append(random.randint(0x01,0xFE))
 #output.extend([0xFE,0xFE,0xFE,0xFE])
 if l3_seq!=[]:
  output[4:]=[0x01,master_identifier,slave_identifier,l2+mystery_bit*0x10,l3_seq,0x10]+l3
 else: 
  output[4:]=[0x01,master_identifier,slave_identifier,l2+mystery_bit*0x10]
 return output

#layer 1 header
def header(data):
 high, low =divmod(len(data), 0x100)
 high|=0b01000000 #set long frame bit
 if (len(data)<64):
  data=[0xA5,0x00,low]+data
 else:
  data=[0xA5,0x00,high,low]+data
 hash = crc8.crc8()
 #print "output encrypted:", [hex(x) for x in data]
 for x in range(len(data)):#add crc8 as last data byte to frame
  hash.update(chr(data[x]))
 data.append(ord(hash.digest()))
 return data

#layer 3 slave side messages
version_number=l3_message([0x00,0x04,0x01,0x06,0x00,0x00,0x03,0x00])#0x03 indicates battery level
ACK=l3_message(5*[0x00]+[0xAA],True)
DUMP_RESET=l3_message([0x02,0x02])
NO_AMIIBO=l3_message([0x02,0x05,0x01]+41*[0x00])
DUMP_DONE=l3_message([0x02,0x05,0x00]+41*[0x00])

def l3_send(message):
 sleep(0.06)
 ser.write(str(bytearray(header(exor_encrypt(layer_wrapper(connection_identifier,ident, 0x00,l3_message_number,message.payload,message.mystery_bit))))))

#layer 2 Disconnection acknowledgment
def disconnect():
 sleep(0.02)
 ser.write(header(exor_encrypt(layer_wrapper(connection_identifier,ident, 0x0b))))

#layer 2 connection Handshake acknowledgement
def connect():
 global ident
 ident=random.randint(0x00,0xFF)
 #ident=0xA4
 sleep(0.06)
 ser.write(str(bytearray(header(exor_encrypt(layer_wrapper(connection_identifier,ident, 0x0d))))))
 #print ("connect request")

def padded_hex(value):
 return '0x{0:0{1}X}'.format(value,2)

def get_rawdata():
 while True:
  l2=[]
  l3=[]
  x=ser.read()
  if padded_hex(ord(x))!='0xA5':
   file_write(Fore.GREEN+padded_hex(ord(x)))
  else:
   hash = crc8.crc8()
   hash.update(x)
   #print("")
   #print(Fore.RED+padded_hex(ord(x))),
   #print(Style.RESET_ALL),
   x=ser.read()
   hash.update(x) 
   #print(padded_hex(ord(x))),
   x=ser.read()
   hash.update(x)
   #print(padded_hex(ord(x))),
   if ord(x) & (1<<6):
    short_frame=False
   else:
    short_frame=True
   payload_size=0b00111111 & ord(x)
   if short_frame==False:
    x=ser.read()
    #print(padded_hex(ord(x))),
    hash.update(x)
    payload_size*=256
    payload_size+=ord(x)
   xorval_higher=0xE9
   xorval_lower=0x63
   #if payload_size>1500:
    #payload_size=20
   for x in range(payload_size/2):
    a=ser.read()
    hash.update(a)
    output=ord(a)^xorval_higher
    xorval_higher=ord(a)
    if x>3:
     #print(Back.YELLOW+Fore.BLACK+padded_hex(output)),
     l3.append(output)
    else:
     #print(Back.WHITE+Fore.BLACK+padded_hex(output)),
     l2.append(output)
    a=ser.read()
    hash.update(a)
    output=ord(a)^xorval_lower
    xorval_lower=ord(a)
    if x>3:
     #print(Back.YELLOW+Fore.BLACK+padded_hex(output)),
     l3.append(output)
    else:
     #print(Back.WHITE+Fore.BLACK+padded_hex(output)),
     l2.append(output)
   if (payload_size%2)!=0:
    a=ser.read()
    hash.update(a)
    output=ord(a)^xorval_higher
    xorval_higher=ord(a)
    if x>3:
     #print(Back.YELLOW+Fore.BLACK+padded_hex(output)),
     l3.append(output)
    else:
     #print(Back.WHITE+Fore.BLACK+padded_hex(output)),
     l2.append(output)
   x=ser.read()
   if x==hash.digest():
    #print(Back.GREEN+padded_hex(ord(x))+Style.RESET_ALL)
    return l2,l3
   #else:
    #print(Back.RED+padded_hex(ord(x))+Style.RESET_ALL)
