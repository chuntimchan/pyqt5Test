class VideoInfo:
    def __init__(self,name : str,length : int,framerate : float,filepath : str,**kwargs):
        self.name = name
        self.length = length
        self.framerate = framerate
        self.filepath = filepath
    
    def __str__(self):
        return f"VideoInfo(name={self.name}, length={self.length},framerate={self.framerate},filepath={self.filepath})"
    
    @property
    def getName(self):
        return self.name
    
    @property
    def getLength(self):
        return self.length
    
    @property
    def getFramerate(self):
        return self.framerate
    
    @property
    def getFilepath(self):
        return self.filepath
    
    #Return a JSON representation of the object
    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'length': self.length,
            'framerate': self.framerate,
            'filepath': self.filepath,
        }
    

