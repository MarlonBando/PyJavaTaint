import yaml

class Settings:
    USER = ''
    JSESSIONID = ''


    def __init__(self):
        with open('settings.yaml','r') as f:
            settings = yaml.safe_load(f)
            
            if 'username' in settings:
                self.USER = settings['user']

            if 'jsessionid' in settings:
                self.JSESSIONID = settings['jsessionid']
        