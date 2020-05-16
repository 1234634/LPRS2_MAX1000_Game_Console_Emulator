#! /usr/bin/env python
# encoding: utf-8

'''
@author: Milos Subotic <milos.subotic.sm@gmail.com>
@license: MIT

'''

###############################################################################

import os
import sys
import fnmatch
import shutil
import datetime

import waflib

###############################################################################

APPNAME = 'LPRS2_GPU_Emulator'

top = '.'

###############################################################################

def prerequisites(ctx):
	ctx.recurse('emulator')

	if sys.platform.startswith('linux'):
		# Ubuntu.
		ctx.exec_command2('sudo apt-get -y install python-pil')
	elif sys.platform == 'msys':
		# MSYS2 Windows.
		ctx.exec_command2('pacman --noconfirm -S mingw-w64-python-pillow')

def options(opt):
	opt.load('compiler_c compiler_cxx')
	
	opt.recurse('emulator')

def configure(conf):
	conf.load('compiler_c compiler_cxx')
	
	conf.recurse('emulator')

	conf.env.append_value('CFLAGS', '-std=c99')
	
	conf.find_program(
		'img_to_src.py',
		var = 'IMG_TO_SRC',
		path_list = os.path.abspath('.')
	)
	

def build(bld):
	bld.recurse('emulator')
	
	for p in ['intro', 'advanced_modes']:
		bld.program(
			features = 'cxx',
			source = [p + '.c'],
			use = 'emulator',
			target = p
		)
		
	if True:
		bld(
			rule = '${IMG_TO_SRC} -f RGB333 -o ${TGT} ${SRC}',
			source = 'images/Pacman_Sprite_Map.png',
			target = 'sprites.c'
		)
		for p in ['sprite_anim']:
			bld.program(
				features = 'cxx',
				source = [p + '.c', 'sprites.c'],
				use = 'emulator',
				target = p
			)
	
###############################################################################

def recursive_glob(pattern, directory = '.'):
	for root, dirs, files in os.walk(directory, followlinks = True):
		for f in files:
			if fnmatch.fnmatch(f, pattern):
				yield os.path.join(root, f)
		for d in dirs:
			if fnmatch.fnmatch(d + '/', pattern):
				yield os.path.join(root, d)

def collect_git_ignored_files():
	for gitignore in recursive_glob('.gitignore'):
		with open(gitignore) as f:
			base = os.path.dirname(gitignore)
			
			for pattern in f.readlines():
				pattern = pattern[:-1]
				for f in recursive_glob(pattern, base):
					yield f

###############################################################################

def exec_command2(self, cmd, **kw):
	# Log output while running command.
	kw['stdout'] = None
	kw['stderr'] = None
	ret = self.exec_command(cmd, **kw)
	if ret != 0:
		self.fatal('Command "{}" returned {}'.format(cmd, ret))
setattr(waflib.Context.Context, 'exec_command2', exec_command2)

def distclean(ctx):
	for fn in collect_git_ignored_files():
		if os.path.isdir(fn):
			shutil.rmtree(fn)
		else:
			os.remove(fn)

def dist(ctx):
	now = datetime.datetime.now()
	time_stamp = '{:d}-{:02d}-{:02d}-{:02d}-{:02d}-{:02d}'.format(
		now.year,
		now.month,
		now.day,
		now.hour,
		now.minute,
		now.second
	)
	ctx.arch_name = '../{}-{}.zip'.format(APPNAME, time_stamp)
	ctx.algo = 'zip'
	ctx.base_name = APPNAME
	# Also pack git.
	waflib.Node.exclude_regs = waflib.Node.exclude_regs.replace(
'''
**/.git
**/.git/**
**/.gitignore''', '')
	# Ignore waf's stuff.
	waflib.Node.exclude_regs += '\n**/.waf*'
	
###############################################################################
