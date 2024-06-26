import sys, os, cv2, colorsys,json, shutil
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PyQt5.QtWidgets import QCheckBox,QTabWidget,QTreeWidget, QTreeWidgetItem,QApplication, QWidget,QComboBox, QHBoxLayout, QFrame, QVBoxLayout, QMainWindow, QLabel,QPushButton, QSpacerItem, QSizePolicy, QStyle, QSlider, QAction, QMessageBox, QInputDialog
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QImage,QPixmap
from src.MarkerSlider import MarkerSlider
from classes import eventCategory,project,videoInfo, event
from pose_estimator import webcam_pose_head_tracking
import itertools

class PoseAnalyser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1280, 720)
        self.create_constants()
        self.init_ui()
        self.disable_buttons()
        print(cv2.__version__)

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

        #Create a TabWidget to hold the main editor and a secondary editor
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        # Create the main editor frame section------------------------+
        editor_frame = QFrame(self)
        editor_frame.setFrameShape(QFrame.StyledPanel)
        editor_frame.setFrameShadow(QFrame.Raised)
        editor_frame.setLineWidth(2)  # Set border width

        # Create a 2 vertical layouts for the editor_frame
        editor_layout = QHBoxLayout(editor_frame)

        # Add the editor_frame to the tab_widget
        self.tab_widget.addTab(editor_frame, "Editor")

        # Add a second tab a vertical layout for the secondary editor
        #Add a frame for the secondary editor
        secondary_editor_frame = QFrame(self)
        secondary_editor_frame.setFrameShape(QFrame.StyledPanel)
        secondary_editor_frame.setFrameShadow(QFrame.Raised)
        secondary_editor_frame.setLineWidth(2)

        #New Vertical Layout for the event editor layout
        event_editor_layout = QVBoxLayout(secondary_editor_frame)
        self.tab_widget.addTab(secondary_editor_frame, "Secondary Editor")

        # |--1st vertical layout for the main video player--|
        video_layout = QVBoxLayout()
        video_layout.setSpacing(0)
        # Adding widgets to the video_layout

        #Making a VideoPlayer
        self.videoLabel = QLabel("Video Label")
        self.videoLabel.setFixedSize(800, 450)
        self.videoName = QLabel("Video Name")
        
        #Add open video button
        self.openBtn = QPushButton('Open Project')
        self.openBtn.clicked.connect(self.open_project) 

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

        #Add Load Events JSON Button
        self.load_events_button = QPushButton('Load Events')
        self.load_events_button.clicked.connect(self.load_events_file)

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
        event_add_layout.addWidget(self.load_events_button, alignment=Qt.AlignRight)

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

        self.detect_pose_button = QPushButton("Detect Pose")
        self.detect_pose_button.setFixedSize(100, 50)  # Set width to 100 and height to 50

        self.show_pose_only_button = QPushButton("Show Pose Only")
        self.show_pose_only_button.setFixedSize(100, 50)  # Set width to 100 and height to 50

        spacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        # Adding buttons to the pose_layout
        pose_layout.addWidget(self.show_pose_button, alignment=Qt.AlignCenter)
        pose_layout.addWidget(self.detect_pose_button, alignment=Qt.AlignCenter)
        pose_layout.addWidget(self.show_pose_only_button, alignment=Qt.AlignCenter)
        pose_layout.addItem(spacer)

        # Set the stretch factor of video_layout to pose_layout as a 5:1 ratio
        editor_layout.addLayout(video_layout, 5)
        editor_layout.addLayout(pose_layout, 1)
        
        # Populate the event editor layout
        # Add 2 horizontal layouts for the event editor

        # Create a horizontal layout for the event editor for a Double Video Viewer
        double_video_viewer = QHBoxLayout()
        double_video_viewer.setSpacing(0)
        double_video_viewer.setContentsMargins(0, 0, 0, 0)

        #Add 2 vertical layouts for the double video viewer
        left_video_viewer = QVBoxLayout()
        right_video_viewer = QVBoxLayout()
        #Add a Small Margin to the vertical layouts
        left_video_viewer.setContentsMargins(5, 0, 5, 0)
        right_video_viewer.setContentsMargins(5, 0, 5, 0)

        #Add slider and checkbox to the vertical layouts using the custom widget
        self.left_video = EventTabSlider(self)
        self.right_video = EventTabSlider(self)

        left_video_viewer.addWidget(self.left_video)
        right_video_viewer.addWidget(self.right_video)

        #Add the vertical layouts to the event editor layout
        double_video_viewer.addLayout(left_video_viewer)
        double_video_viewer.addLayout(right_video_viewer)

        # Create a horizontal layout for the event editor for the video controls
        video_controls = QHBoxLayout()
        video_controls.setSpacing(0)
        video_controls.setContentsMargins(0, 0, 0, 0)

        #Add video control buttons to the horizontal layout
        video_controls.addWidget(QPushButton("Skip Backward"))
        #Previous button
        twoWindow_prevBtn = QPushButton("Previous")
        twoWindow_prevBtn.clicked.connect(self.prevVideoSnippets)
        video_controls.addWidget(twoWindow_prevBtn)
        twoWindow_playBtn = QPushButton("Play")
        twoWindow_playBtn.clicked.connect(self.playVideoSnippets)
        video_controls.addWidget(twoWindow_playBtn)
        twoWindowNextBtn = QPushButton("Next")
        twoWindowNextBtn.clicked.connect(self.nextVideoSnippets)
        video_controls.addWidget(twoWindowNextBtn)
        video_controls.addWidget(QPushButton("Skip Forward"))

        
        # Add the horizontal layouts to the event editor layout
        event_editor_layout.addLayout(double_video_viewer)
        event_editor_layout.addLayout(video_controls)

        #-------------------------------------------------------------!

        main_layout.addWidget(event_frame,1)
        main_layout.addWidget(self.tab_widget)
        

    
    def playVideoSnippets(self):
        if(self.left_video.checkbox.isChecked()):
            self.left_video.play_video()
        if(self.right_video.checkbox.isChecked()):
            self.right_video.play_video()


    def nextVideoSnippets(self):
        if(self.left_video.checkbox.isChecked()):
            self.left_video.next_frame()
        if(self.right_video.checkbox.isChecked()):
            self.right_video.next_frame()

    def prevVideoSnippets(self):
        '''Prev Video Snippets'''
        if(self.left_video.checkbox.isChecked()):
            self.left_video.prev_frame()
        if(self.right_video.checkbox.isChecked()):
            self.right_video.prev_frame()

    def duration_changed(self, duration):
        self.videoSlider.setRange(0, duration)

    #Open file function, gets the filename and sets the video label to the video and starts the first frame while setting the label video name
    def open_file(self,filename):
        '''With an input filename (full file path and name) it will proceed to open the video file and update all GUI elements with the loaded in video
        Used opening an existing project'''
        filename = filename
        
        #All the clearing also moved to open project
        #Clear Events Tree and Event Combo Box and Markers
        self.project.videoInfo = videoInfo.VideoInfo("",0,0,"")
        
        self.currentFrame = 0

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
        self.currentFrame = self.nextFrameSlot()

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
    def nextFrameSlot(self,video_label = None,video_object = None,video_slider = None,to_pose_estimate = None,end_frame = None,frame_number = None) -> int:
        #Default video label if not given is self.videoLabel
        mainView = False
        if (video_label is None or frame_number is None or end_frame is None):
            video_label = self.videoLabel
            video_object = self.cap
            video_slider = self.videoSlider
            to_pose_estimate = self.to_pose_estimate
            end_frame = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
            frame_number = self.currentFrame
            mainView = True

        #Code duplication with display_current_frame as calling display current frame from next frame slot constantly heavily slows down the video
        if(end_frame > frame_number + 1):
            frame_number += 1
            success, frame = video_object.read()

            #Pose Estimation
            if to_pose_estimate:
                frame = webcam_pose_head_tracking.add_pose(frame,self.model)

            video_slider.setValue(frame_number)
            print("Main nextframeslot method. Video Object Frame Number:", video_object.get(cv2.CAP_PROP_POS_FRAMES))
            if success:
                #OpenCV Label Magic to convert to QImage and display in QLabel
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(video_label.width(), video_label.height(), Qt.KeepAspectRatio)
                video_label.setPixmap(QPixmap.fromImage(p))
                if(mainView):
                    self.currentFrame = frame_number
                return frame_number
        
        return end_frame

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
        new_event = event.Event(self.project.getNumberOfEvents(), self.currentFrame,30)

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
                #Add right click functionality tree widget item
                

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
        #Create New Project
        create_new_project_action = QAction('Create New Project', self)
        file_menu.addAction(create_new_project_action)
        create_new_project_action.triggered.connect(self.create_project)

        #Open Existing Project Folder
        open_project_action = QAction('Open Existing Project', self)
        file_menu.addAction(open_project_action)
        open_project_action.triggered.connect(self.open_project)

        #Save Project
        self.save_project_action = QAction('Save Project', self)
        file_menu.addAction(self.save_project_action)
        self.save_project_action.triggered.connect(self.save_project)
        
        #Frame Skip Number
        set_frame_skip_size_action = QAction('Set Frame Skip Size', self)
        settings_menu.addAction(set_frame_skip_size_action)
        set_frame_skip_size_action.triggered.connect(self.set_frame_skip_size)

    #Opens an existing project folder
    def open_project(self):

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
        
        #Let's the user choose what folder to open
        project_path = QFileDialog.getExistingDirectory(self, "Choose Project Directory", "")
        if project_path == "":
            #Show message box that the path was invalid
            QMessageBox.warning(self, "Invalid Path", "Please select a valid path.")
            return
                
        #Check if a events json file exists in the directory
        events_file_path = ""
        events_files_number = 0
        for file in os.listdir(project_path):
            if file.endswith(".json"):
                events_file_exists = True
                events_files_number = events_files_number + 1
                events_file_path = project_path + "/" + file
                break

        #Clear project and subsiquent nested objects are created
        self.project = project.Project()
        myVideoInfo = videoInfo.VideoInfo("",0,0,"")
        self.project.videoInfo = myVideoInfo

        #Load in the Json file found
        self.load_events_file(events_file_path)
        
        #Open the video file specified in the events json file
        self.open_file(self.project.videoInfo.filepath)
        
        #Clear Events Tree and Event Combo Box and Markers
        self.event_tree.clear()
        self.videoSlider.setMarkers([])
        self.event_category_combo_box.clear()
        self.event_category_combo_box.addItem("Add New Event Category")


        
        #Change the current project JSON file's filepath to the new project directory
        self.project.filepath = project_path

        #Update Event Widgets
        self.update_event_tree_view()
        self.update_event_combo()
        self.update_markers()

        #Enable Play Skip Buttons
        self.enable_buttons()

        #Menu cleanup remove open button when a file is opened
        if self.file_selected == False:
            self.file_selected = True
            self.openBtn.setEnabled(False)
            self.openBtn.hide()




    #Creates a new project
    def create_project(self):
        #First it opens a file dialog to let the user choose where to create the project
        project_path = QFileDialog.getExistingDirectory(self, "Choose Project Directory", "")
        if project_path == "":
            #Show message box that the path was invalid
            QMessageBox.warning(self, "Invalid Path", "Please select a valid path.")
            return
        
        #Then it opens a input dialog to get the project name
        project_name = QInputDialog.getText(self, "Create Project", "Project Name")
        if project_name[0] == "":
            #Show message box that the project name was invalid
            QMessageBox.warning(self, "Invalid Project Name", "Please enter a valid project name.")
            return
        
        self.project.projectName = project_name[0]

        #Check the directory doesn't already exist
        if os.path.exists(project_path + "/" + project_name[0]):
            #Add a message box that the directory already exists
            QMessageBox.warning(self, "Invalid Project Name", "The project directory already exists.")
            return
        
        #Create the project directory
        os.mkdir(project_path + "/" + project_name[0])

        #Show a message box to prompt the user to select a video file
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Please select a video file.")
        msg.setWindowTitle("Information")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

        #Change the current project filepath to the new project directory
        self.project.filepath = project_path

        #Make user choose a video file
        filename, _ = QFileDialog.getOpenFileName(self, "Open Video", "", "MP4 Files (*.mp4)")
        # Check if the file is an MP4 video
        if not filename.lower().endswith('.mp4'):
            QMessageBox.warning(self, "Invalid file", "Please select an MP4 video.")
            return

        #Opens the video file
        self.open_file(filename)

        #Show a message box that the project was created including filename and path
        QMessageBox.information(self, "Project Created", "Project created at " + project_path + "/" + project_name[0])

    
    #Loads events file in and populates the global project variable object  
    def load_events_file(self,filepath):
        #Let's the user choose a JSON file
        filename = filepath

        # Check if the file is an JSON file
        if not filename.lower().endswith('.json'):
            QMessageBox.warning(self, "Invalid file", "Please select an JSON file.")
            return
        
        #Open the JSON file
        with open(filename) as f:
            data = json.load(f)

        #Check if the video Info matches the current video and sends a information message box and does not continue
        print(type(self.project.videoInfo))

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

        #Add .json to the end of filename
        save_file_name = self.project.projectName + ".json"

        # Check if the file already exists in the project directory

        if os.path.exists(self.project.filepath + "/" + self.project.projectName + "/"+ save_file_name):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("The file already exists. Do you want to overwrite it?")
            msg.setWindowTitle("Warning")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

            retval = msg.exec_()
            if retval != QMessageBox.Ok:  # If the user did anything else that is not Ok return
                return
        
        #Save the project to the project directory
        with open(self.project.filepath + "/" + self.project.projectName + "/" + save_file_name, 'w') as f:
            json.dump(self.project.to_dict(), f, indent=4)

        #Show a messagebox to confirm the project has been saved
        QMessageBox.information(self, "Project Saved", "Project saved at " + self.project.filepath +"/"+ save_file_name)

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
        #self.load_events_action.setEnabled(False)
        self.saveBtn.setEnabled(False)
        #self.load_events_button.setEnabled(False)
        self.show_pose_button.setEnabled(False)
        self.detect_pose_button.setEnabled(False)
        self.show_pose_only_button.setEnabled(False)
        self.load_events_button.setEnabled(False)
        #Disable secondary editor tab
        self.tab_widget.setTabEnabled(1, False)

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
        #self.load_events_action.setEnabled(True)
        self.saveBtn.setEnabled(True)
        #self.load_events_button.setEnabled(True)
        self.show_pose_button.setEnabled(True)
        self.detect_pose_button.setEnabled(True)
        self.show_pose_only_button.setEnabled(True)
        #Enable secondary editor tab
        self.tab_widget.setTabEnabled(1, True)

    #When the tab is changed
    def on_tab_changed(self, index):
        #If the tab is in the main editor
        if index == 1:
            #Check if the timer exists without using the timer variable
            if hasattr(self, 'timer'):
                #If the timer is running pause the video
                if self.timer.isActive():
                    self.pause()

#Create a custom widget 
class EventTabSlider(QWidget):
    '''This class is a custom widget which is a horizontal layout with a checkbox and a slider'''
    id_obj = itertools.count()
    timer : QTimer = QTimer()

    def __init__(self,poseAnalyserInstance : PoseAnalyser=None):
        super().__init__()
        self.init_ui()
        self.id = next(EventTabSlider.id_obj)
        self.poseAnalyserInstance = poseAnalyserInstance
        self.videoEvent : cv2.VideoCapture = None
        self.videoStartFrame : int  = 0
        self.videoEndFrame : int = 0
        self.frame_number : int = 0
        self.event : event.Event = None

    def init_ui(self):
        #Create a Vertical layout for the event editor
        self.event_editor_layout = QVBoxLayout(self)

        #Create the videolabel
        self.video_label = QLabel("Video Label")

        #Add the video label to the vertical layout
        self.event_editor_layout.addWidget(self.video_label)

        #Make a horizontal layout to hold checkbox and button
        self.checkbox_layout = QHBoxLayout()
        
        #Add a Qcheckbox to the vertical layout
        self.checkbox = QCheckBox("Control Event")
        self.checkbox.setChecked(True)

        #Add a button beside the checkbox to add selected event
        self.select_event = QPushButton("Select Event")
        self.select_event.setFixedSize(100, 50)
        self.select_event.clicked.connect(self.add_event_to_video_box)

        self.checkbox_layout.addWidget(self.checkbox)
        self.checkbox_layout.addWidget(self.select_event)

        #Add the horizontal layout to the vertical layout
        self.event_editor_layout.addLayout(self.checkbox_layout)

        #Add a slider to the vertical layout
        self.slider = QSlider(Qt.Horizontal)
        self.event_editor_layout.addWidget(self.slider,alignment=Qt.AlignTop)

        #Remove space between the widgets
        self.event_editor_layout.setSpacing(0)
        self.event_editor_layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.event_editor_layout)

    def set_event(self,event : event.Event):
        self.event = event
        #Mocking behaviour by setting the video 
        self.set_duration(event.frameNumber,event.frameNumber + event.getDuration)
        print("Set Event Frame Number: ", self.frame_number, "Event Frame Duration: ", event.getDuration)
        #Play next frame
        self.next_frame()
        #Print the current frame
        print("Set Event: ", self.frame_number)


    def get_duration(self):
        '''Returns the duration of the video in frames'''
        return self.videoEndFrame - self.videoStartFrame
    
    def set_duration(self,videoStartFrame,videoEndFrame):
        '''Sets the duration of the video in frames'''
        self.videoStartFrame = videoStartFrame
        self.videoEndFrame = videoEndFrame
        self.frame_number = videoStartFrame
        self.slider.setRange(videoStartFrame,videoEndFrame)
        self.videoEvent.set(cv2.CAP_PROP_POS_FRAMES, self.frame_number-1)

    #Makes the object's next_frame method call the poseAnalyserInstance's nextFrameSlot method using this video label
    def next_frame(self):
        self.frame_number = self.poseAnalyserInstance.nextFrameSlot(self.video_label,self.videoEvent,self.slider,False,self.videoEndFrame,self.frame_number) 
        print("View ID:", self.id, "Frame Number: ", self.frame_number, "Video EndFrame: ", self.videoEndFrame)
        if self.frame_number >= self.videoEndFrame:
            self.pause()

    def prev_frame(self):
        self.videoEvent.set(cv2.CAP_PROP_POS_FRAMES, self.frame_number - 2)
        self.frame_number -= 2
        self.frame_number = self.poseAnalyserInstance.nextFrameSlot(self.video_label,self.videoEvent,self.slider,False,self.videoEndFrame,self.frame_number)

    def play_video(self):
        '''Plays the video'''
        self.timer.timeout.connect(self.next_frame)
        self.timer.start(round(1000/round(self.poseAnalyserInstance.cap.get(cv2.CAP_PROP_FPS))))
        print("GADFADFDASF")

    def pause(self):
        '''Pauses the video'''
        self.timer.stop()
        
    #Method to add the highlighted event into the videobox with multiple views
    def add_event_to_video_box(self):
        #Set videoEvent to the poseAnalyserInstance's videoEvent
        self.videoEvent = cv2.VideoCapture(self.poseAnalyserInstance.project.videoInfo.filepath)

        #Get selected event in event tree
        selected_event = self.poseAnalyserInstance.event_tree.selectedItems()
        if len(selected_event) == 0:
            #Show message that no event is selected
            QMessageBox.warning(self, "No Event Selected", "Please select an event to add to the video box.")
            return
        
        #Get the selected event's text
        selected_event_text = selected_event[0].text(0)

        #Parse ID from the selected event's text
        event_id = int(selected_event_text.split(',')[0].split(':')[1])

        #Get the event from the project
        selected_event = self.poseAnalyserInstance.project.getEventByID(event_id)

        self.set_event(selected_event)

    #Future Works
    # #Slider changed
    # def slider_change_snippet(self):
    #     self.frame_number = self.slider.value()
    #     self.videoEvent.set(cv2.CAP_PROP_POS_FRAMES, self.frame_number-1)
    #     self.frame_number = self.poseAnalyserInstance.display_current_frame(self.video_label,self.videoEvent,self.slider,False,self.videoEndFrame,self.frame_number)

        
if __name__ == '__main__':
    os.environ['QT_MULTIMEDIA_PREFERRED_PLUGINS'] = 'windowsmediafoundation'
    app = QApplication(sys.argv)
    app.setStyle('fusion')
    window = PoseAnalyser()
    window.show()
    sys.exit(app.exec_())