#!/usr/bin/env python3
# Copyright 2021 the V8 project authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

# Processes {stdout} output generated by --trace-wasm-compilation-times
# for easier consumption by human readers.

import sys

def SizeInternal(number, suffix):
  if suffix == "": return "%d" % number
  if number < 10: return "%.1f%s" % (number, suffix)
  return "%d%s" % (number, suffix)

def Size(number):
  if (number < 1024): return SizeInternal(number, "")
  number /= 1024
  if (number < 1024): return SizeInternal(number, "K")
  number /= 1024
  if (number < 1024): return SizeInternal(number, "M")
  number /= 1024
  if (number < 1024): return SizeInternal(number, "G")
  return SizeInternal(number / 1024, "T")

modules = {}
max_module = 0
total_tf_time = 0
total_tf_size = 0

def RegisterName(raw):
  global max_module
  parts = raw.split("#")
  m = parts[0]
  if m not in modules:
    modules[m] = max_module
    max_module += 1

def Name(raw):
  parts = raw.split("#")
  if len(modules) == 1: return "#%s" % parts[1]
  return "m%d#%s" % (modules[parts[0]], parts[1])

class Function:
  def __init__(self, index):
    self.index = index
    self.has_lo = False
    self.has_tf = False
    self.time_lo = -1
    self.time_tf = -1
    self.mem_lo = -1
    self.mem_tf_max = -1
    self.mem_tf_total = -1
    self.name = ""
    self.size_wasm = -1
    self.size_lo = -1
    self.size_tf = -1

  def AddLine(self, words):
    assert self.index == words[2], "wrong function"
    if words[4] == "TurboFan,":
      self.AddTFLine(words)
    elif words[4] == "Liftoff,":
      self.AddLiftoffLine(words)
    else:
      raise Exception("unknown compiler: %s" % words[4])

  def AddTFLine(self, words):
    assert not self.has_tf, "duplicate TF line for %s" % self.index
    self.has_tf = True
    # 0        1        2  3     4         5    6 7  8   9     10 11
    # Compiled function #6 using TurboFan, took 0 ms and 14440 / 44656
    # 12        13     14       15 16   17
    # max/total bytes, codesize 24 name wasm-function#6
    self.time_tf = int(words[6])
    self.mem_tf_max = int(words[9])
    self.mem_tf_total = int(words[11])
    self.size_tf = int(words[15])
    self.name = words[17]

  def AddLiftoffLine(self, words):
    assert self.index == words[2], "wrong function"
    assert not self.has_lo, "duplicate Liftoff line for %s" % self.index
    self.has_lo = True
    # 0        1        2  3     4        5    6 7  8   9   10     11       12
    # Compiled function #6 using Liftoff, took 0 ms and 968 bytes; bodysize 4
    # 13       14
    # codesize 68
    self.time_lo = int(words[6])
    self.mem_lo = int(words[9])
    self.size_lo = int(words[14])
    self.size_wasm = int(words[12])

  def __str__(self):
    return "%s: time %d %d mem %s %s %s size %s %s %s name %s" % (
      Name(self.index), self.time_lo, self.time_tf,
      Size(self.mem_lo), Size(self.mem_tf_max), Size(self.mem_tf_total),
      Size(self.size_wasm), Size(self.size_lo), Size(self.size_tf), self.name
    )

funcs_dict = {}
funcs_list = []

if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
  print("Pass output file (generated with --trace-wasm-compilation-times) as "
        "argument")
  sys.exit(1)

with open(sys.argv[1], "r") as f:
  for line in f.readlines():
    words = line.strip().split(" ")
    if words[0] != "Compiled": continue
    name = words[2]
    RegisterName(name)
    if name in funcs_dict:
      func = funcs_dict[name]
    else:
      func = Function(name)
      funcs_dict[name] = func
      funcs_list.append(func)
    func.AddLine(words)

funcs_list.sort(key=lambda fun: fun.time_tf)
for f in funcs_list:
  print(f)
  total_tf_time += f.time_tf
  total_tf_size += f.size_tf

print("Total TF time: %d" % total_tf_time)
print("Total TF size: %d" % total_tf_size)
