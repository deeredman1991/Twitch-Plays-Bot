import os

#print( subprocess.check_output([ 'python', '-m', '--name', 'TPB',  ])

os.system('python -m PyInstaller --icon "J:\\ProgrammingStuff\\Python Scripts\\Twitch-Plays-Bot\\images\\icon32.ico" --name TPB "J:\\ProgrammingStuff\\Python Scripts\\Twitch-Plays-Bot\\main.py')

os.system('xcopy /y "J:\\ProgrammingStuff\\Python Scripts\\Twitch-Plays-Bot\\scripts\\TPB.spec" "J:\\ProgrammingStuff\\Python Scripts\\Twitch-Plays-Bot\\TPB.spec"')

os.system('python -m PyInstaller "J:\\ProgrammingStuff\\Python Scripts\\Twitch-Plays-Bot\\TPB.spec"')

#for f in os.listdir( 'J:\\ProgrammingStuff\\Python Scripts\\ZombiesWithoutBorders\\configs' ):
#    f2 = f
#    if f == 'login.json':
#        f = 'dummy_login.json'
#    if f2 != 'dummy_login.json':
#        os.system('xcopy /y "J:\\ProgrammingStuff\\Python Scripts\\ZombiesWithoutBorders\\configs\\{0}" "J:\\ProgrammingStuff\\Python Scripts\\ZombiesWithoutBorders\\dist\\Zombot\\configs\\{1}"'.format(f, f2))

#os.system('xcopy /y "J:\\ProgrammingStuff\\Python Scripts\\ZombiesWithoutBorders\\config.ini" "J:\\ProgrammingStuff\\Python Scripts\\ZombiesWithoutBorders\\dist\\Zombot\\config.ini"')
        
#os.system('xcopy /y "J:\\ProgrammingStuff\\Python Scripts\\ZombiesWithoutBorders\\data_files" "J:\\ProgrammingStuff\\Python Scripts\\ZombiesWithoutBorders\\dist\\Zombot\\data_files"')

#os.system('xcopy /y "J:\\ProgrammingStuff\\Python Scripts\\ZombiesWithoutBorders\\images" "J:\\ProgrammingStuff\\Python Scripts\\ZombiesWithoutBorders\\dist\\Zombot\\images"')

#os.system('xcopy /y "J:\\ProgrammingStuff\\Python Scripts\\ZombiesWithoutBorders\\icon" "J:\\ProgrammingStuff\\Python Scripts\\ZombiesWithoutBorders\\dist\\Zombot\\icon"')