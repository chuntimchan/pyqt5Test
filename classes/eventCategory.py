from classes.event import Event
from typing import List

class EventCategory():
    def __init__(self,categoryName: str,eventsList: List[Event] = None,colour :str = '#FFFFFF',**kwargs):
        self.categoryName = categoryName
        self.colour = colour
        self.eventsList = [Event(**event) for event in eventsList] if eventsList is not None else []

    #Add Event to Event Category
    def addEvent(self,event):
        #print(event)
        self.eventsList.append(event)

    @property
    def getName(self) -> str:
        return self.categoryName
    
    @property
    def getColour(self) -> str:
        return self.colour
    
    def __str__(self):
        events_str = ', '.join(map(str, self.eventsList))
        return f"EventCategory(name={self.categoryName}, colour={self.colour},eventList=[{events_str}])"
        
    #Number of events#
    def getNumberOfEvents(self) -> int:
        return len(self.eventsList)

    #Return a JSON representation of the object (uses the event to_dict method)
    def to_dict(self) -> dict:
        return {
            'categoryName': self.categoryName,
            'colour': self.colour,
            'eventsList': [event.to_dict() for event in self.eventsList],
        }

    #Get event by ID
    def getEventByID(self, eventID: int):
        for event in self.eventsList:
            if event.get_id == eventID:
                return event
        return None


    