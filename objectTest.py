from classes import eventCategory, event, project, videoInfo
from json import JSONEncoder
import json
from json import JSONEncoder
import json

# Create a new project
myProject = project.Project()
myProject.projectName = "My Project"

# Create a new video info object
myVideoInfo = videoInfo.VideoInfo("My Video", 1920, 1080, 30)

# Create a new event category
myEventCategory = eventCategory.EventCategory("My Category")

# Add the event category to the project
myProject.addCategory(myEventCategory)

# Create and add events
myProject.eventCategories[0].addEvent(event.Event(myProject.getNumberOfEvents(),0))
myProject.eventCategories[0].addEvent(event.Event(myProject.getNumberOfEvents(),10))
myProject.eventCategories[0].addEvent(event.Event(myProject.getNumberOfEvents(),20))

# Encode myProject variable into JSON
with open('myProject.json', 'w') as f:
    json.dump(myProject.to_dict(), f, indent=4)





