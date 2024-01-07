class Event():
    def __init__(self,id: int,frameNumber: int,duration: int = 0,**kwargs):
        self.id = id
        self.frameNumber = frameNumber
        self.duration = duration

    def __str__(self):
        return f"Event(id={self.id}, frameNumber={self.frameNumber})"
    
    @property
    def getFrameNo(self) -> int:
        return self.frameNumber
    
        
    @property
    def get_id(self) -> int:
        return self.id
    
    #Return a JSON representation of the object
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'frameNumber': self.frameNumber,
            'duration': self.duration,
        }
    
