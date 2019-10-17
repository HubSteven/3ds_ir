import sys

if (len(sys.argv)<2):
    print("Usage: 3ds_write.py <serial port> <name of Amiibo bin>")
    exit()
if (len(sys.argv)>2):
 amiibo_ready=True
 amiibo_file_name=sys.argv[2]
else:
 amiibo_ready=False

import ir_3ds as ir
ir.open_port(sys.argv[1])
connection=False
data_written=False
while(True):
  message=ir.get_message()
  if (message==ir.CONNECTION_REQUEST):
   ir.connect()
   dump_reset=False
   connection=True
  elif (message==ir.DISCONNECTION_REQUEST):
   ir.disconnect()
   connection=False
  elif (connection):
   if (message==ir.VERSION_REQUEST):
    ir.l3_send(ir.version_number)
   elif (message==ir.MYSTERY_REQUEST):
    ir.l3_send(ir.ACK)
   elif (message==ir.SELECTED_MEMORY_PAGES):
    ir.l3_send(ir.ACK)
    data_written=False
    dump_reset=False
    dump_response_counter=0
   elif (message==ir.WRITE_DATA):
    ir.mem_dump_write(amiibo_file_name)
    ir.l3_send(ir.ACK)
    data_written=True
   elif (message==ir.MEMORY_DUMP_REQUEST):
    if (dump_reset==True):
     ir.l3_send(ir.DUMP_RESET)
    elif (amiibo_ready==True):
     if (data_written):
      ir.l3_send(ir.dump_response(amiibo_file_name,0x05))
     else:
      if (dump_response_counter==0):
       ir.l3_send(ir.NO_AMIIBO)
       #print("EERSTE")
       dump_response_counter+=1
      elif (dump_response_counter==1):
       ir.l3_send(ir.dump_response("test.bin",0x02))
       #print("TWEEDE")
       dump_response_counter+=1       
      else:
       ir.l3_send(ir.dump_response(amiibo_file_name,0x04))
       #print("DERDE")
    else:
     ir.l3_send(ir.NO_AMIIBO)
   elif (message==ir.DUMP_DONE):
    ir.l3_send(ir.ACK)
    dump_reset=True 
