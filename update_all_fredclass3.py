from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
import os, shutil


'''Python script for overwriting all copies of fredclass.py with the version in the current directory.
Obviously, use at your own risk.'''


orig_path = os.getcwd()+'fredclass3.py'
user = orig_path.split("/")[2]

drop_path = '/Users/'+user+'/Dropbox'
desk_path = '/Users/'+user+'/Desktop'
orig_path = os.getcwd()+'/fredclass3.py'

i = 0
for (path, dirs, files) in os.walk(drop_path):

    for f in files:
    	if f=='fredclass3.py' and path.lower() != os.getcwd().lower():
    		print(path)
    		# print files
    		shutil.copy(orig_path,path)
    		print("----")
    i += 1

for (path, dirs, files) in os.walk(desk_path):

    for f in files:
    	if f=='fredclass3.py':
    		print(path)
    		# print files
    		shutil.copy(orig_path,path)
    		print("----")
    i += 1
    # if i >= 400:
    #     break

