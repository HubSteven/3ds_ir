# 3ds_ir
Spoofing the 3DS Amiibo NFC adapter via an IRda USB/RS232 adapter
# Usage
3ds_write.py is used to emulate the NFC adapter. To run the python2.7 script write <code>python 3ds_write.py <serial port ex. /dev/ttyUSB0> <Amiibo .bin file></code> leaving this argument blank emulates and NFC adapter without an Amiibo on top of it. The IRda adapter should work work as long as it has a serial port. Therefore it should also be compatible with Windows (haven't tested it though)
  
3ds.py is used to sniff the IR data between the NFC adapter and 3DS. The colors indicates the data layer of the data. The packets are already exor decrypted in python.

More info at https://www.3dbrew.org/wiki/NFC_adapter and https://gbatemp.net/threads/3ds-ir-amiibo-reader-hacked-better-late-than-never.538459/
