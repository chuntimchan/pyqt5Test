import sys, os, cv2, colorsys,json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem,QApplication, QWidget,QComboBox, QHBoxLayout, QFrame, QVBoxLayout, QMainWindow, QLabel,QPushButton, QSpacerItem, QSizePolicy, QStyle, QSlider, QAction, QMessageBox, QInputDialog
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QImage,QPixmap
from src.MarkerSlider import MarkerSlider
from classes import eventCategory,project,videoInfo, event
from pose_estimator import webcam_pose_head_tracking

class PoseAnalyser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1280, 720)
        self.create_constants()
        self.init_ui()
        self.disable_buttons()

    def init_ui(self):
        # Create menu bar
        self.createMenuBar()
        # Create a central widget to set the layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create a horizontal layout for the central widget
        main_layout = QHBoxLayout(central_widget)

        # Create the event section-------------------------------------+
        event_frame = QFrame(self)
        event_frame.setFrameShape(QFrame.StyledPanel)
        event_frame.setFrameShadow(QFrame.Raised)
        event_frame.setLineWidth(2)  # Set border width

        event_layout = QVBoxLayout(event_frame)

        self.event_tree = QTreeWidget(event_frame)
        self.event_tree.setHeaderLabel("Event View")
        self.event_tree.itemDoubleClicked.connect(self.event_tree_double_clicked)
        self.event_tree.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        event_layout.addWidget(self.event_tree)
        #--------------------------------------------------------------!

        # Create the main editor frame section------------------------+
        editor_frame = QFrame(self)
        editor_frame.setFrameShape(QFrame.StyledPanel)
        editor_frame.setFrameShadow(QFrame.Raised)
        editor_frame.setLineWidth(2)  # Set border width

        # Create a 2 vertical layouts for the editor_frame
        editor_layout = QHBoxLayout(editor_frame)

        # |--1st vertical layout for the main video player--|
        video_layout = QVBoxLayout()
        video_layout.setSpacing(0)
        # Adding widgets to the video_layout

        #Making a VideoPlayer
        self.videoLabel = QLabel("Video Label")
        self.videoLabel.setFixedSize(800, 450)
        self.videoName = QLabel("Video Name")
        
        #Add open video button
        self.openBtn = QPushButton('Open Video')
        self.openBtn.clicked.connect(self.open_file) 

        #create Horizontal Layout for play pause, next frame etc buttons.--------------------------
        play_skip_layout = QHBoxLayout()
        play_skip_layout.setSpacing(30)
        play_skip_layout.setContentsMargins(40, 40, 40, 40)

        #Creating Buttons for the Layout to Play, Next Frame, Prev Frame, Skip Next Frame, Skip Prev Frame
        #Play Button
        self.playBtn = QPushButton()
        self.playBtn.setEnabled(False)
        self.playBtn.setCheckable(True)
        self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playBtn.clicked.connect(self.play_video)
        #Next Frame Button
        self.nextFrameBtn = QPushButton()
        self.nextFrameBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaSeekForward))
        self.nextFrameBtn.setEnabled(False)
        self.nextFrameBtn.clicked.connect(self.nextFrameSlot)
        #Prev Frame Button
        self.prevFrameBtn = QPushButton()
        self.prevFrameBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaSeekBackward))
        self.prevFrameBtn.setEnabled(False)
        self.prevFrameBtn.clicked.connect(self.prevFrameSlot)
        #Skip Next Frame Button
        self.skipNextFrameBtn = QPushButton()
        self.skipNextFrameBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipForward))
        self.skipNextFrameBtn.setEnabled(False)
        self.skipNextFrameBtn.clicked.connect(self.skipNextFrameSlot)
        #Skip Prev Frame Button
        self.skipPrevFrameBtn = QPushButton()
        self.skipPrevFrameBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipBackward))
        self.skipPrevFrameBtn.setEnabled(False)
        self.skipPrevFrameBtn.clicked.connect(self.skipPrevFrameSlot)

        #Adding Buttons to the play_skip_layout
        play_skip_layout.addWidget(self.skipPrevFrameBtn)
        play_skip_layout.addWidget(self.prevFrameBtn)
        play_skip_layout.addWidget(self.playBtn)
        play_skip_layout.addWidget(self.nextFrameBtn)
        play_skip_layout.addWidget(self.skipNextFrameBtn)

        #------------

        #Creating Horizontal Layout for Event Addition Buttons---------------
        event_add_layout = QHBoxLayout()
        event_add_layout.setSpacing(30)
        event_add_layout.setContentsMargins(40, 40, 40, 40)

        #Adding a Push Button to add an event
        self.add_event_button = QPushButton("Add Event")
        self.add_event_button.setFixedSize(100, 50)  # Set width to 100 and height to 50
        self.add_event_button.clicked.connect(self.add_event)

        #Add save event button
        self.saveBtn = QPushButton('Save Project')
        self.saveBtn.clicked.connect(self.save_project)

        #Adding a Combo Box to select an event category or add new category
        self.event_category_combo_box = QComboBox()
        self.event_category_combo_box.setFixedSize(150, 50)  # Set width to 100 and height to 50
        #Adding List of Categories from Project to the Combo Box
        self.event_category_combo_box.clear()
        self.event_category_combo_box.addItem("Add New Event Category")
        for category in self.project.eventCategories:
            self.event_category_combo_box.addItem(category.name)
        
        #Adding Button and Combo Box to the event_add_layout
        event_add_layout.addWidget(self.add_event_button, alignment=Qt.AlignLeft)
        event_add_layout.addWidget(self.event_category_combo_box, alignment=Qt.AlignLeft)
        event_add_layout.addStretch(1)
        event_add_layout.addWidget(self.saveBtn, alignment=Qt.AlignRight)

        #---------------------------------
        #Create Slider
        self.videoSlider = MarkerSlider(Qt.Horizontal)
        self.videoSlider.setRange(0,0)
        self.videoSlider.sliderReleased.connect(self.slider_changed) 
        self.videoSlider.sliderPressed.connect(self.pause)
        self.videoSlider.markerClicked.connect(self.marker_jump)


        #Adding to video frame layout
        video_layout.addWidget(self.openBtn,1,alignment=Qt.AlignCenter)
        video_layout.addWidget(self.videoName,1,alignment=Qt.AlignCenter)
        video_layout.addWidget(self.videoLabel, 10, alignment=Qt.AlignTop | Qt.AlignHCenter)
        play_skip_layout.setSpacing(30)
        play_skip_layout.setContentsMargins(10, 10, 10, 5)
        video_layout.addLayout(play_skip_layout, 1)    
        video_layout.addWidget(self.videoSlider,1,alignment=Qt.AlignTop)
        event_add_layout.setSpacing(30)
        event_add_layout.setContentsMargins(10, 0, 10, 0)
        video_layout.addLayout(event_add_layout, 1)
        video_layout.addStretch(1)


        # |--2nd vertical layout for pose estimation button slots--|
        pose_layout = QVBoxLayout()

        pose_layout = QVBoxLayout()
        pose_layout.setSpacing(30)
        pose_layout.setContentsMargins(40, 40, 40, 40)
        # Adding widgets to the pose_layout
        self.show_pose_button = QPushButton("Show Pose")
        self.show_pose_button.setFixedSize(100, 50)  # Set width to 100 and height to 50
        self.show_pose_button.clicked.connect(self.show_pose)

        detect_pose_button = QPushButton("Detect Pose")
        detect_pose_button.setFixedSize(100, 50)  # Set width to 100 and height to 50

        show_pose_only_button = QPushButton("Show Pose Only")
        show_pose_only_button.setFixedSize(100, 50)  # Set width to 100 and height to 50

        spacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        # Adding buttons to the pose_layout
        pose_layout.addWidget(self.show_pose_button, alignment=Qt.AlignCenter)
        pose_layout.addWidget(detect_pose_button, alignment=Qt.AlignCenter)
        pose_layout.addWidget(show_pose_only_button, alignment=Qt.AlignCenter)
        pose_layout.addItem(spacer)

        # Set the stretch factor of video_layout to pose_layout as a 5:1 ratio
        editor_layout.addLayout(video_layout, 5)
        editor_layout.addLayout(pose_layout, 1)
        
        #-------------------------------------------------------------!

        main_layout.addWidget(event_frame,1)
        main_layout.addWidget(editor_frame,5)
        

    
    def duration_changed(self, duration):
        self.videoSlider.setRange(0, duration)

    #Open file function, gets the filename and sets the video label to the video and starts the first frame while setting the label video name
    def open_file(self):
        #Gets file name
        filename, _ = QFileDialog.getOpenFileName(self, "Open Video", "", "MP4 Files (*.mp4)")

        #Check if there are currently any events in the project and if there are any unsaved events
        if self.project.getNumberOfEvents() > 0:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("There are unsaved events in the project. Do you want to save them? They will be deleted if unsaved.")
            msg.setWindowTitle("Warning")
            msg.setStandardButtons(QMessageBox.Save | QMessageBox.Discard)

            retval = msg.exec_()
            if retval == QMessageBox.Save:
                self.save_project()
            
        # Check if the file is an MP4 video
        if not filename.lower().endswith('.mp4'):
            QMessageBox.warning(self, "Invalid file", "Please select an MP4 video.")
            return
        
        #Clear Events Tree and Event Combo Box and Markers
        self.event_tree.clear()
        self.videoSlider.setMarkers([])
        self.event_category_combo_box.clear()
        self.event_category_combo_box.addItem("Add New Event Category")
        #Clear project and Video Info and Event category variables
        self.project = project.Project()
        self.project.videoInfo = videoInfo.VideoInfo("",0,0,"")
        
        self.currentFrame = 0
        #Menu cleanup remove open button when a file is opened
        if self.file_selected == False:
            self.file_selected = True
            self.openBtn.setEnabled(False)
            self.openBtn.hide()

        #Opens Video CV2
        self.cap = cv2.VideoCapture(filename)

        #Sets label name
        self.videoName.setText(filename)
        #Enable Play Skip Buttons
        self.enable_buttons()

        #Sets slider range
        self.videoSlider.setRange(0,int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)))

        #Update Project's Video Info
        self.project.videoInfo.name = (os.path.basename(filename))
        self.project.videoInfo.length = (self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.project.videoInfo.framerate = (self.cap.get(cv2.CAP_PROP_FPS))
        self.project.videoInfo.filepath = (filename)

        #Creates timer to play video
        self.timer = QTimer()
        self.timer.timeout.connect(self.nextFrameSlot)

        #Display next frame
        self.nextFrameSlot()

    #Pose Estimation Function
    def pose_estimate(self, frame):
        return webcam_pose_head_tracking.add_pose(frame,self.model)

    #Display Current Frame
    def display_current_frame(self):
        success, frame = self.cap.read()

        #Pose Estimation
        if self.to_pose_estimate:
            frame = webcam_pose_head_tracking.add_pose(frame,self.model)

        self.videoSlider.setValue(self.currentFrame)
        if success:
            #OpenCV Label Magic to convert to QImage and display in QLabel
            rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgbImage.shape
            bytesPerLine = ch * w
            convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
            p = convertToQtFormat.scaled(self.videoLabel.width(), self.videoLabel.height(), Qt.KeepAspectRatio)
            self.videoLabel.setPixmap(QPixmap.fromImage(p))

    #Reads the next frame of the cap (OpenCV Video Object) and sets the label's image to it
    def nextFrameSlot(self):
        #Code duplication with display_current_frame as calling display current frame from next frame slot constantly heavily slows down the video
        if(self.cap.get(cv2.CAP_PROP_FRAME_COUNT) > self.currentFrame + 1):
            self.currentFrame += 1
            success, frame = self.cap.read()

            #Pose Estimation
            if self.to_pose_estimate:
                frame = webcam_pose_head_tracking.add_pose(frame,self.model)

            self.videoSlider.setValue(self.currentFrame)
            if success:
                #OpenCV Label Magic to convert to QImage and display in QLabel
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(self.videoLabel.width(), self.videoLabel.height(), Qt.KeepAspectRatio)
                self.videoLabel.setPixmap(QPixmap.fromImage(p))

    #Skips back a frame
    def prevFrameSlot(self):
        if(self.currentFrame > 0):
            self.currentFrame -= 1
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.currentFrame)
            self.display_current_frame()

    #Skips forward a frame_skip_size amount of frames
    def skipNextFrameSlot(self):
        if(self.currentFrame + self.frame_skip_size < self.cap.get(cv2.CAP_PROP_FRAME_COUNT)):
            self.currentFrame += self.frame_skip_size
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.currentFrame)
            self.display_current_frame()

    #Skips back a frame_skip_size amount of frames
    def skipPrevFrameSlot(self):
        if(self.currentFrame - self.frame_skip_size > 0):
            self.currentFrame -= self.frame_skip_size
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.currentFrame)
            self.display_current_frame()

    #Jumps to the marker clicked
    def marker_jump(self, marker):
        self.currentFrame = marker
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.currentFrame)
        self.display_current_frame()

    #Double Clicked Event Tree
    def event_tree_double_clicked(self, item, column):
        if item.parent() is not None:  # Check if the item has a parent
            self.marker_jump(int(item.text(0).split(',')[1].split(':')[1])) #Extract Frame Number
        else:
            return

    #Resume or pause timer
    def play_video(self):
        if self.cap.isOpened():
            if self.playBtn.isChecked():

                #Get FPS of the video
                fps = round(self.cap.get(cv2.CAP_PROP_FPS))
                #Calculate the time to wait between frames
                time_to_wait = round(1000/fps)
                self.timer.start(time_to_wait)

                self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            else:
                self.pause()

    #Pause Video
    def pause(self):
        self.timer.stop()
        self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playBtn.setChecked(False)

    #Sets video to the slider value
    def slider_changed(self):
        value = self.videoSlider.value()
        self.currentFrame = value
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.currentFrame)
        self.display_current_frame()

    #Add Event
    def add_event(self):
        if self.event_category_combo_box.currentText() == "Add New Event Category":
            category_name = self.add_new_event_category()
        else:
            category_name = self.event_category_combo_box.currentText()

        if category_name == "":
            #Show a message box that the category name is empty
            QMessageBox.warning(self, "Invalid Category Name", "Please enter a valid category name.")
            #Break out of the add_event function
            return
        elif category_name == -1:
            #Show a message box that the category name already exists
            QMessageBox.warning(self, "Invalid Category Name.", "Category Already exists. Select this in the combo box")
            #Break out of the add_event function
            return
            

        #Create the event Object
        new_event = event.Event(self.project.getNumberOfEvents(), self.currentFrame)

        #Add event to project's corresponding category using a dictionary
        self.category_dict = {category.categoryName: category for category in self.project.eventCategories}
        category = self.category_dict.get(category_name)
        if category is not None:
            category.addEvent(new_event)

        #Draw the event on the slider
        self.update_markers()
        self.update_event_tree_view()

    #Add New Event Category
    def add_new_event_category(self) -> str:
        #Get user input for event category name
        event_category_name = QInputDialog.getText(self, "Add New Event Category", "Event Category Name")

        #Break if user cancels or enters nothing
        if event_category_name[0] == "":
            #Show a message box error that the category name is empty
            print("Empty Category Name")
            return ""
        
        #Check if the category name already exists
        for category in self.project.eventCategories:
            if category.categoryName == event_category_name[0]:
                #Show a message box error that the category name already exists
                print("Category Name Already Exists")
                return -1
            
        #Create new event category
        new_event_category = eventCategory.EventCategory(event_category_name[0],None,self.auto_colour_picker())
        #Add new event category to project
        self.project.addCategory(new_event_category)
        #Add new event category to combo box
        self.update_event_combo()

        return event_category_name[0]

    #Automatic Colour Picker
    def auto_colour_picker(self):
        hue = (len(self.project.eventCategories) * self.golden_ratio) % 1  # Use the golden ratio to get a unique hue
        rgb = colorsys.hls_to_rgb(hue, 0.5, 1)  # Convert the HSL color to an RGB color
        color = '#%02x%02x%02x' % (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))  # Convert the RGB color to a hexadecimal color string
        if color not in self.used_colors:
            self.used_colors.add(color)
            return color
        return '#FFFFFF'  # Default color if all colors are used

    #Update markers to correspond to the project's events
    def update_markers(self):
        self.videoSlider.setMarkers([])
        for category in self.project.eventCategories:
            for event in category.eventsList:
                self.videoSlider.addMarker(event.getFrameNo,category.colour)

    #Update Event Tree View
    def update_event_tree_view(self):
        #Clear the tree view
        self.event_tree.clear()
        #Add the categories to the tree view
        for category in self.project.eventCategories:
            print(type(category))
            category_tree_item = QTreeWidgetItem(self.event_tree)
            category_tree_item.setText(0, category.categoryName)
            #Add the events to the tree view
            for event in category.eventsList:
                print(type(event))
                event_tree_item = QTreeWidgetItem(category_tree_item)
                event_tree_item.setText(0, ("ID:%s , FrameNumber:%s" % (event.get_id,event.getFrameNo)))

        self.event_tree.expandAll()

    #Update Event Combo Box to match project's event categories
    def update_event_combo(self):
        self.event_category_combo_box.clear()
        self.event_category_combo_box.addItem("Add New Event Category")
        for category in self.project.eventCategories:
            self.event_category_combo_box.addItem(category.categoryName)

    #Setting Skip Frame Size by using user input
    def set_frame_skip_size(self):
        size = QInputDialog.getInt(self, "Set Frame Skip Size", "Frame Skip Size", self.frame_skip_size, 1, 200, 1)
        self.frame_skip_size = size[0]

    #Create MenuBar
    def createMenuBar(self):
        #Create menu bar
        menu_bar = self.menuBar()

        #Create Menus for the bar
        file_menu = menu_bar.addMenu('File')
        settings_menu = menu_bar.addMenu('Settings')
        #help_menu = menu_bar.addMenu('Help')

        #Link methods for each menu
        #Open File
        open_video_action = QAction('Open Video', self)
        file_menu.addAction(open_video_action)
        open_video_action.triggered.connect(self.open_file)

        #Save Project
        self.save_project_action = QAction('Save Project', self)
        file_menu.addAction(self.save_project_action)
        self.save_project_action.triggered.connect(self.save_project)
        
        #Load Events File
        self.load_events_action = QAction('Load Events File', self)
        file_menu.addAction(self.load_events_action)
        self.load_events_action.triggered.connect(self.load_events_file)

        #Frame Skip Number
        set_frame_skip_size_action = QAction('Set Frame Skip Size', self)
        settings_menu.addAction(set_frame_skip_size_action)
        set_frame_skip_size_action.triggered.connect(self.set_frame_skip_size)

    #Loads events file in and populates the global project variable object  
    def load_events_file(self):
        #Let's the user choose a JSON file
        filename, _ = QFileDialog.getOpenFileName(self, "Open Events File", "", "JSON Files (*.json)")

        # Check if the file is an JSON file
        if not filename.lower().endswith('.json'):
            QMessageBox.warning(self, "Invalid file", "Please select an JSON file.")
            return
        
        #Open the JSON file
        with open(filename) as f:
            data = json.load(f)

        #Check if the video Info matches the current video and sends a information message box and does not continue

        print(type(self.project.videoInfo))

        
        errors = []

        if data['videoInfo']['filepath'] != self.project.videoInfo.getFilepath:
            errors.append("The filepath in the events json does not match the current video's filepath.")

        if data['videoInfo']['name'] != self.project.videoInfo.getName:
            errors.append("The name in the events json does not match the current video's name.")

        if data['videoInfo']['length'] != self.project.videoInfo.getLength:
            errors.append("The length in the events json does not match the current video's length.")

        if errors:
            #If the only error is the filepath error allow the user to continue if they choose to and update the project video info file path
            if len(errors) == 1 and errors[0] == "The filepath in the events json does not match the current video's filepath.":
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("The filepath in the events json does not match the current video's filepath. Do you want to continue?")
                msg.setWindowTitle("Warning")
                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

                retval = msg.exec_()
                if retval == QMessageBox.No:
                    return
                else:
                    #Set the events json file's filepath to the current video's filepath
                    data['videoInfo']['filepath'] = self.project.videoInfo.filepath

            #Else show all errors and do not continue
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("\n".join(errors))
                msg.setWindowTitle("Information")
                msg.setStandardButtons(QMessageBox.Ok)

                retval = msg.exec_()
                return

        print("Matched")
        #Clear Events Tree and Event Combo Box and Markers
        self.event_tree.clear()
        self.videoSlider.setMarkers([])
        self.event_category_combo_box.clear()
        self.event_category_combo_box.addItem("Add New Event Category")

        #Clear project and subsiquent nested objects are created
        self.project = project.Project(**data)

        self.update_event_tree_view()
        self.update_event_combo()
        self.update_markers()
        
    #Show Pose Button temporarily displays the project info for now
    def show_pose(self):
        #Switch the button's text between Show Pose and Hide Pose
        if self.to_pose_estimate:
            self.show_pose_button.setText("Show Pose")
        else:
            self.show_pose_button.setText("Hide Pose")
        
        #Switch the to_pose_estimate boolean to the opposite of what it was
        self.to_pose_estimate = not self.to_pose_estimate
        print(self.to_pose_estimate)


    #Save Project and all objects within project into a json file
    def save_project(self):

        #If the project name is not empty
        if self.project.projectName != "":
            #Show the Input dialog prefilled with the project name
            self.project.projectName = QInputDialog.getText(self, "Save Project", "Project Name", text=self.project.projectName[0])[0]
        else:
            #Opens a Message box to get the project name
            self.project.projectName = QInputDialog.getText(self, "Save Project", "Project Name")[0]

        #Set a default if QInput dialog returns nothing
        if self.project.projectName == "":
            self.project.projectName = "Default"
            #Show a message box saying the file did not save as the name was invalid
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("The project name was invalid. The project has not been saved")
            msg.setWindowTitle("Warning")
            msg.setStandardButtons(QMessageBox.Ok)

            retval = msg.exec_()
            return

        #Add .json to the end of filename
        save_file_name = self.project.projectName + ".json"

        # Check if the file already exists
        if os.path.exists(save_file_name):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("The file already exists. Do you want to overwrite it?")
            msg.setWindowTitle("Warning")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

            retval = msg.exec_()
            if retval != QMessageBox.Ok:  # If the user did anything else that is not Ok return
                return
        
        with open(save_file_name, 'w') as f:
            json.dump(self.project.to_dict(), f, indent=4)

    def closeEvent(self, event):
        #Check if there are currently any events in the project and if there are any unsaved events
        if self.project.getNumberOfEvents() > 0:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("There are unsaved events in the project. Do you want to save them? They will be deleted if unsaved.")
            msg.setWindowTitle("Warning")
            msg.setStandardButtons(QMessageBox.Save | QMessageBox.Discard)

            retval = msg.exec_()
            if retval == QMessageBox.Save:
                self.save_project()
            else:
                return

    #Creates constants all in 1 method
    def create_constants(self):
        #Project Level Constants for event storage
        self.project = project.Project()
        myVideoInfo = videoInfo.VideoInfo("",0,0,"")
        self.project.videoInfo = myVideoInfo

        self.golden_ratio = 0.618033988749895  # Golden ratio
        self.to_pose_estimate : bool = False
        self.file_selected = False
        self.setWindowTitle('Pose Analyser 40286980')
        self.currentFrame = 0
        self.frame_skip_size = 20
        self.used_colors = set()
        self.model = webcam_pose_head_tracking.load_model()

    #Disable Play Control Buttons and Add Event Button
    def disable_buttons(self):
        self.playBtn.setEnabled(False) 
        self.nextFrameBtn.setEnabled(False)
        self.prevFrameBtn.setEnabled(False)
        self.skipNextFrameBtn.setEnabled(False)
        self.skipPrevFrameBtn.setEnabled(False)
        self.videoSlider.setEnabled(False)
        self.add_event_button.setEnabled(False)
        self.save_project_action.setEnabled(False)
        self.load_events_action.setEnabled(False)
        self.saveBtn.setEnabled(False)

    #Enable Play Control Buttons and Add Event Button
    def enable_buttons(self):
        self.playBtn.setEnabled(True) 
        self.nextFrameBtn.setEnabled(True)
        self.prevFrameBtn.setEnabled(True)
        self.skipNextFrameBtn.setEnabled(True)
        self.skipPrevFrameBtn.setEnabled(True)
        self.videoSlider.setEnabled(True)
        self.add_event_button.setEnabled(True)
        self.save_project_action.setEnabled(True)
        self.load_events_action.setEnabled(True)
        self.saveBtn.setEnabled(True)

if __name__ == '__main__':
    os.environ['QT_MULTIMEDIA_PREFERRED_PLUGINS'] = 'windowsmediafoundation'
    app = QApplication(sys.argv)
    app.setStyle('fusion')
    window = PoseAnalyser()
    window.show()
    sys.exit(app.exec_())