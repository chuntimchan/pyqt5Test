from json import JSONEncoder
from typing import List
from classes.eventCategory import EventCategory
from classes.videoInfo import VideoInfo

class Project():
    def __init__(self, projectName: str = '', videoInfo: VideoInfo = None, eventCategories: List[EventCategory] = None, filepath: str = '',**kwargs):
        self.projectName = projectName
        self.videoInfo = VideoInfo(**videoInfo) if videoInfo is not None else VideoInfo("Default",0,0,filepath)
        self.eventCategories = [EventCategory(**category) for category in eventCategories] if eventCategories is not None else []
        self.filepath = filepath

    # Add Event to Event Category
    def addCategory(self, eventCategory):
        #print(eventCategory)
        self.eventCategories.append(eventCategory)
    
    @property
    def getFilepath(self) -> str:
        return self.filepath
    
    def __str__(self):
        eventsCat_str = ', '.join(map(str, self.eventCategories))
        return f"Project(name={self.projectName}, videoInfo={self.videoInfo},eventCategory=[{eventsCat_str}])"
        
    #Number of events
    def getNumberOfEvents(self) -> int:
        totalEvents = 0
        for category in self.eventCategories:
            totalEvents += category.getNumberOfEvents()
        return totalEvents
    
    #Get event by ID
    def getEventByID(self, eventID: int):
        for category in self.eventCategories:
            event = category.getEventByID(eventID)
            if event is not None:
                return event
        return None

    def to_dict(self) -> dict:
        '''Return a JSON representation of the project object (uses the eventCategory and VideoInfo to_dict method). Contains filepath, 
        projectName, videoInfo and eventCategories'''
        return {
            'filepath': self.filepath,
            'projectName': self.projectName,
            'videoInfo': self.videoInfo.to_dict(),
            'eventCategories': [category.to_dict() for category in self.eventCategories],
        }
    



    