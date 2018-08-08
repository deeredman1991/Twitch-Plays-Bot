import psutil


class ProcessManager(object):
    def __init__( self, *args, configs=None, **kwargs ):
        self.configs = configs
        self.paused = False
        self.process = None
        
    def start(self):
        if self.open_emulator() or \
           self.get_process_by_name() or \
           self.get_process_by_pid() or \
           self.get_process_by_gui():
                return self
        assert False, 'ProcessManager could not find process. Please check "emulator_settings.json"'
        
    def open_emulator(self):
        emu_path = self.configs['emulator_settings']['emu_path']
        if emu_path:
            self.process = psutil.Popen([emu_path])
            return True
        return False

    def pause_emulator(self):
        assert self.process, 'ProcessManager has no process.'
        if not self.paused:
            self.process.suspend()
            self.paused = True
            return True
        return False

    def resume_emulator(self):
        assert self.process, 'ProcessManager has no process'
        if self.paused:
            self.process.resume()
            self.paused = False
            return True
        return False

    def get_process_by_name(self):
        proc_name = self.configs['emulator_settings']['process_name']
        for proc in psutil.process_iter():
            pinfo = proc.as_dict(attrs=['pid', 'name'])
            if pinfo['name'] == proc_name:
                self.process = psutil.Process( pinfo['pid'] )
                return True
        return False

    def get_process_by_gui(self):
        #Create a gui window with a list of all running processes and allow the user to select one.
        #assert False 'Unfinished method in ProcessManager "get_process_by_gui"'
        return False

    def get_process_by_pid(self):
        pid = self.configs['emulator_settings']['pid']
        
        if pid:
            self.process = psutil.Process( pid )
            return True
        return False
        
if __name__ == '__main__':
    import time
    figs = {'emulator_settings': {
                "emu_path": 'notepad',
                "process_name": False,
                "pid": False
            }}
            
    pm = ProcessManager( configs=figs ).start()
    time.sleep(1)
    print( pm.pause_emulator())
    time.sleep(5)
    print( pm.resume_emulator() )