#!/usr/bin/env python3
import sys


last_c1 = {}                         # remember CMD1 (high-order byte of command)
def newstate(prev, input):
   global last_c1
   if input['raw'] == 'MOSI':
      state = 'CMD1'
   elif prev == 'CMD1':
      last_c1 = input
      state = 'CMD0'
   elif prev == 'CMD0' :
      #print (input)
      #print (last_c1)
      if last_c1['bytes'] == 1:
         state = 'DATA0'
      else:
         sys.stderr.write ("Streaming?\n")
         state = 'DATA0'
   elif prev == 'DATA0' :
      state = 'CMD1'
   else:
      state = prev
      
   return state


def bool_bit(str, pos):
   return (str[pos] == '1')

def interp(state, input):
   meaning = {}
   meaning['raw'] = input
   if (input == 'MOSI'):
      return meaning
   
   if ((state == 'CMD1') or
       (state == 'CMD0') or
       (state == 'DATA0')):
      byte_str = bin(int(input,16))[2:]
      # zero-pad
      while len(byte_str) < 8:
         byte_str = "0" + byte_str
         
      if state == 'CMD1':
         meaning['read']     = bool_bit(byte_str, 0)
         meaning['bytes']    =  { '00':1,
                               '01':2,
                               '10':3,
                               '11':'Streaming'}[byte_str[1:3]]
         meaning['addr_top'] = byte_str[3:8]
      elif state == 'CMD0':
         meaning['addr_bottom'] = byte_str[0:8]
      elif state == 'DATA0':
         meaning['value'] = byte_str[0:8]
   return meaning


def think(state, input, memory):
   action = None
   
   if state == 'CMD1':
      memory = input
   elif state == 'CMD0':
      # meaning['read']     = memory['read']
      # meaning['bytes']    = memory['bytes']
      print (memory)
      addr_str = memory['addr_top'] + input['addr_bottom']
      memory['addr_str']  = addr_str
      memory['addr'] = int(addr_str,2)
      memory['addr_hex'] = hex(memory['addr'])
   elif state == 'DATA0':
      action = memory
      memory = {}
              
   return (memory, action, input)


state=None
prev_meaning=None
memory={}
for line in sys.stdin:
   l = line.strip()
   
   meaning = interp(state, l)
   next_state = newstate(state, meaning)
   
   (memory, action, input) = think(state, meaning, memory)
   

   print ((state, l, next_state, input, action))
   state = next_state

   

      
		
	
