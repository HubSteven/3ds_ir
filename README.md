# 3ds_ir
Spoofing the 3DS Amiibo NFC adapter via an IRda USB/RS232 adapter
# Usage
3ds_write.py is used to emulate the NFC adapter. To run the python 2.7 script write in your terminal <code>python 3ds_write.py <serial port ex. /dev/ttyUSB0> <Amiibo .bin file></code> leaving the last argument blank emulates an NFC adapter without an Amiibo on top of it. The IRda adapter should work work as long as it has a serial port. Therefore it should also be compatible with Windows (haven't tested it though, I always use Linux). https://gembird.nl/item.aspx?id=3076&lang=en is the IRda adapter I used.
 
The script supports reading and writing to an Amiibo binary.
  
3ds.py is used to sniff the IR data between the NFC adapter and 3DS. The colors indicates the data layer of the data. The packets are already exor decrypted in python.

More info at https://www.3dbrew.org/wiki/NFC_adapter and https://gbatemp.net/threads/3ds-ir-amiibo-reader-hacked-better-late-than-never.538459/
