#!/usr/bin/env python

"""
ad9510spi.py

This module decodes a subset of the SPI packet structure defined
for configuring Analog Devices' AD9510 clock distribution and PLL
chips.  It is based on the AD9510 Data Sheet, Revision A (2005).
It decodes only one-byte writes!

This module expects the PHY-layer decoding to be handled by some
other code (perhaps the SPI module in this package, as in the main
function below.)  Its notion of a packet is a sequence of bits from
the MOSI/SDIO line, corresponding to a CSB-low period.  Bit
sequences are to be represented as strings of the characters '0'
and '1'.

Author: Eric Anderson http://www.ece.cmu.edu/~andersoe/
Copyright 2011 Carnegie Mellon University.  All rights reserved.
See README.TXT for details.
"""

import sys
#from vcd_reader import VcdEater
from cmu_vcd import AntlrVCD
from SPI import SPI


class ad9510spi  (object):

   def __init__(self):
      self.last_c1 = {}      # remember CMD1 (high-order byte of command)
      self.state=None
      self.prev_meaning=None
      self.memory={}

   def newstate(self, prev, input):
      if input['raw'] == 'MOSI':
         state = 'CMD1'
      elif prev == 'CMD1':
         self.last_c1 = input
         state = 'CMD0'
      elif prev == 'CMD0' :
         #print (input)
         #print (last_c1)
         if self.last_c1['bytes'] == 1:
            state = 'DATA0'
         else:
            sys.stderr.write ("Streaming?\n")
            state = 'DATA0'
      elif prev == 'DATA0' :
         state = 'CMD1'
      else:
         state = prev

      return state

   def begin(self):
      self.state = 'CMD1'

   def end(self):
      pass
   def bool_bit(self, str, pos):
      return (str[pos] == '1')

   def interp(self, state, input):
      meaning = {}
      meaning['raw'] = input
      if (input == 'MOSI'):
         return meaning

      if ((state == 'CMD1') or
          (state == 'CMD0') or
          (state == 'DATA0')):
         if len(input) != 8:
            raise ValueError("Expecting strings of 8 bits (as characters).  Got: %s" % repr(input))
        
         if state == 'CMD1':
            meaning['read']     = self.bool_bit(input, 0)
            meaning['bytes']    =  { '00':1,
                                     '01':2,
                                     '10':3,
                                     '11':'Streaming'}[input[1:3]]
            meaning['addr_top'] = input[3:8]
         elif state == 'CMD0':
            meaning['addr_bottom'] = input[0:8]
         elif state == 'DATA0':
            meaning['value'] = input[0:8]
      return meaning

   def think(self, state, input, memory):
      
      action = None

      if state == 'CMD1':
         memory = input
      elif state == 'CMD0':
         # meaning['read']     = memory['read']
         # meaning['bytes']    = memory['bytes']
         #print (memory)
         memory['raw']=memory['raw'] + input['raw']
         addr_str = memory['addr_top'] + input['addr_bottom']
         memory['addr_str']  = addr_str
         memory['addr'] = int(addr_str,2)
         memory['addr_hex'] = hex(memory['addr'])
      elif state == 'DATA0':
         memory['raw']=memory['raw'] + input['raw']
         memory['value']=int(input['value'],2)
         memory['value_hex']=hex(memory['value'])

         action = memory
         memory = {}

      return (memory, action, input)

   def run(self, data):
      actions = []
      for line in data:         
         l = line.strip()
         self.begin()
         while len(l) > 0:
            byte = l[:8]
            l = l[8:]
            meaning = self.interp(self.state, byte)
            next_state = self.newstate(self.state, meaning)            
            (self.memory, action, input) = self.think(self.state, meaning, self.memory)
            #print ((self.state, byte, next_state, input, action))
            #print ((byte, action))
            if action is not None:
               actions.append(action)
            #print ((byte, meaning))
            self.state = next_state
         self.end()
      return actions

   
def main(argv):
  vcdfile = "./foo.vcd"  
  #foo = VcdEater(vcdfile)
  foo = AntlrVCD(file(vcdfile))

  spi = SPI(CPOL=0, CPHA=1,
            SCLK="/ad9510_hw/old_booter/clockEngine/SCLK",
            CSN="/ad9510_hw/old_booter/clockEngine/CSN",
            MOSI="/ad9510_hw/old_booter/clockEngine/SDIO")
  spi.register(foo)
  
  foo.go()
  spi.end()

  print '\n'.join(spi.get_mosi())

   
  p = ad9510spi()
  cmds = p.run(spi.get_mosi())
  #print cmds
  for c in cmds:
     tag = ("read" if c['read'] else "write")
     length = c['bytes']
     addr_start = c['addr_hex']
     value = c['value_hex']
     print "%-5s addr:%5s value:%4s" % (tag, addr_start, value)

if __name__ == '__main__':
   sys.exit(main(sys.argv))
