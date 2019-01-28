
class Log:
    def __init__(self, status='OFF'):
        self.status = status
    def set_status(self, status='OFF'):
        if status != 'OFF' and status != 'ON' and status != 'DEBUG':
            raise ValueError('Invalid status request: try "ON", "OFF", or "DEBUG"')
        self.status = status
    def log(self, string):
        if self.status == 'ON':
            print(string)
        elif self.status == 'DEBUG':
            print('DEBUG: ' + string)
    # Add dump to file option