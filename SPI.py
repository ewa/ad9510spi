"""
SPI.py

This module is a minimal protocol/logic analyzer for SPI busses.
It takes as input value-change events (perhaps read from a VCD file
by the vcd_reader module) and produces strings of bits from the
MOSI/SDI/SDIO wire.  Each string represents one period of the
CSB/CSN wire being low, and is composed of the characters '0' and
'1'.  The SPI.get_mosi() function returns a Python list of strings
for all the SPI communication periods observed since the object's
initialization.  Bits from an incomplete period (CSN was observed
to go low and has not yet gone high) will _NOT_ be returned, unless
SPI.end() has been called first.

Author: Eric Anderson http://www.ece.cmu.edu/~andersoe/
Copyright 2011 Carnegie Mellon University.  All rights reserved.
See README.TXT for details.
"""

import sys
from vcd_reader import VcdEater

class SPI (object):

  def __init__(self, CPOL, CPHA, SCLK, CSN, MOSI):
    self.CPOL = CPOL
    self.CPHA = CPHA
    self.sclk_name = SCLK
    self.csn_name = CSN
    self.mosi_name = MOSI

    self.sclk_state = None
    self.csn_state = None
    self.mosi_state = None
    self.vcd = None

    self.sequences = []
    self.current_sequence = None

  def register(self, vcd):
    self.vcd = vcd    
    vcd.reg_by_name(self.sclk_name, self.obs_sclk)
    vcd.reg_by_name(self.csn_name, self.obs_csn)
    vcd.reg_by_name(self.mosi_name, self.obs_mosi)


  def _sample_mosi(self):
    if self.csn_state == 0:
      #print "mosi: %d" % self.mosi_state
      self.current_sequence.append(self.mosi_state)

    
  def obs_sclk(self, now, id, name, old_value, new_value, first):    
    #print "%-6d %-8s/ %-30s: %10s -> %10s" % (now, id,name,old_value,new_value)
    self.sclk_state = new_value
    #print "CPOL=%1d,CPHA=%d" % (self.CPOL, self.CPHA)


    rising = (old_value == 0 and new_value == 1)
    falling = (old_value == 1 and new_value == 0)

    if   (self.CPOL==0 and self.CPHA == 0 and rising):
      self._sample_mosi()
    elif (self.CPOL==0 and self.CPHA == 1 and falling):
      self._sample_mosi()
    elif (self.CPOL==1 and self.CPHA == 0 and falling):
      self._sample_mosi()
    elif (self.CPOL==1 and self.CPHA == 1 and rising):
      self._sample_mosi()

      
      
  def obs_csn(self, now, id, name, old_value, new_value, first):
    self.csn_state = new_value
    rising = (old_value == 0 and new_value == 1)
    falling = (old_value == 1 and new_value == 0)

    if falling:
      # Start new block of bits
      if self.current_sequence is not None:
        raise ValueError("CSN going low, but bit sequence already open!")
      self.current_sequence = []

      if self.sclk_state is not None and self.CPOL != self.sclk_state:
        raise ValueError("CSN going low, and CPOL=%d, but SCLK=%d!"  %
                         (self.CPOL, self.sclk_state))
        
      
    if rising:
      #End current block of bits
      if self.current_sequence is None:
        raise ValueError("CSN going high, but no bit sequence!")
      self.sequences.append(self.current_sequence)
      self.current_sequence = None

      if self.sclk_state is not None and self.CPOL != self.sclk_state:
        raise ValueError("CSN going high, and CPOL=%d, but SCLK=%d!"  %
                         (self.CPOL, self.sclk_state))

    
    
  def obs_mosi(self, now, id, name, old_value, new_value, first):
    self.mosi_state = new_value
    rising = (old_value == 0 and new_value == 1)
    falling = (old_value == 1 and new_value == 0)

  def end(self):
    if self.current_sequence is not None:
      sys.stderr.write("Warning: SPI had a bit sequence open when end() called.\n")
      self.sequences.append(self.current_sequence)
      self.current_sequence = None

  def get_mosi(self):
    return [ ''.join([str(bit) for bit in s]) for s in self.sequences]



def main(args):
  
  vcdfile = "./foo.vcd"


  foo = VcdEater(vcdfile)

  spi = SPI(CPOL=0, CPHA=0,
            SCLK="revisit_ad9510./ad9510_hw/old_booter/clockEngine/SCLK",
            CSN="revisit_ad9510./ad9510_hw/old_booter/clockEngine/CSN",
            MOSI="revisit_ad9510./ad9510_hw/old_booter/clockEngine/SDIO")
  spi.register(foo.vcd)


  foo.process()
  spi.end()

  print spi.get_mosi()

if __name__ == '__main__':
  sys.exit(main(sys.argv))


