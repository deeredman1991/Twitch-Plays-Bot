# -*- mode: python -*-
from kivy.deps import sdl2, glew

block_cipher = None


a = Analysis(['J:\\ProgrammingStuff\\Python_Scripts\\Twitch-Plays-Bot\\main.py'],
             pathex=['J:\\ProgrammingStuff\\Python_Scripts\\Twitch-Plays-Bot'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='TPB',
          debug=False,
          strip=False,
          upx=True,
          console=True , icon='J:\\ProgrammingStuff\\Python_Scripts\\Twitch-Plays-Bot\\icon\\icon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
               strip=False,
               upx=True,
               name='TPB')
