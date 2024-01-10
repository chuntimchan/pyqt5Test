import sys,os,json, cv2
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox, QStyle
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt, QTimer
import src.PoseAnalyser as PoseAnalyser
import classes.event, classes.project , classes.eventCategory , classes.videoInfo
from unittest.mock import patch, MagicMock, PropertyMock


class TestPoseAnalyser:
    def setup_method(self,method):
        '''Creating the Window which is the main object of the program. The PoseAnalyser'''
        print("hello")
        self.app = QApplication(sys.argv)
        self.window = PoseAnalyser.PoseAnalyser()

    #Correct Startup Tests -----------------------------------------------------
    #Test the GUI elements are all present
    def test_GUI_elements(self):
        '''Test that all GUI elements are present'''

        #Testing the buttons
        assert self.window.playBtn
        assert self.window.nextFrameBtn
        assert self.window.prevFrameBtn
        assert self.window.skipNextFrameBtn
        assert self.window.skipPrevFrameBtn
        assert self.window.videoSlider
        assert self.window.add_event_button
        assert self.window.save_project_action
        assert self.window.load_events_action
        assert self.window.saveBtn

        #Testing the video player
        assert self.window.videoLabel

        #Testing the menu bar
        assert self.window.menuBar()

    #Testing the objects are being instantiated properly
    def test_objects_creation(self):
        '''Testing Video Info Object and Project Object'''
        assert self.window.project is not None
        assert self.window.project.videoInfo.getFramerate == 0
        assert self.window.project.videoInfo.getLength == 0

    #Testing the constants are being instantiated properly
    def test_constants(self):
        '''Test default constants'''

        #Testing Constants
        assert self.window.golden_ratio == 0.618033988749895
        assert self.window.to_pose_estimate == False
        assert self.window.file_selected == False
        assert self.window.windowTitle() == 'Pose Analyser 40286980'
        assert self.window.currentFrame == 0
        assert self.window.frame_skip_size == 20
        assert self.window.used_colors == set()
        assert self.window.model is not None

    #Testing the buttons that should be disabled from the start are disabled
    def test_disable_buttons(self):
        '''Test that all buttons are disabled at the start'''
        assert not self.window.playBtn.isEnabled()
        assert not self.window.nextFrameBtn.isEnabled()
        assert not self.window.prevFrameBtn.isEnabled()
        assert not self.window.skipNextFrameBtn.isEnabled()
        assert not self.window.skipPrevFrameBtn.isEnabled()
        assert not self.window.videoSlider.isEnabled()
        assert not self.window.add_event_button.isEnabled()
        assert not self.window.save_project_action.isEnabled()
        assert not self.window.load_events_action.isEnabled()
        assert not self.window.saveBtn.isEnabled()

    #Methods Testing ---------------------------------------------------------------
    #Testing the buttons that should be enabled from the start are enabled
    def test_enable_buttons(self):
        '''Test that all buttons are enabled after calling enable_buttons'''
        self.window.enable_buttons()

        assert self.window.playBtn.isEnabled()
        assert self.window.nextFrameBtn.isEnabled()
        assert self.window.prevFrameBtn.isEnabled()
        assert self.window.skipNextFrameBtn.isEnabled()
        assert self.window.skipPrevFrameBtn.isEnabled()
        assert self.window.videoSlider.isEnabled()
        assert self.window.add_event_button.isEnabled()
        assert self.window.save_project_action.isEnabled()
        assert self.window.load_events_action.isEnabled()
        assert self.window.saveBtn.isEnabled()

    #Test close event method call when there are no events
    def test_closeEvent_with_no_unsaved_events(self):
        '''Test closeEvent when there are no unsaved events. There should be no popup called'''
    
        # Replace save_project with a mock
        self.window.save_project = MagicMock()

        # Trigger the closeEvent
        self.window.close()

        # Assert that save_project was not called
        self.window.save_project.assert_not_called()

    #Test close event method call when there are events, a popup should be called
    def test_closeEvent_with_unsaved_events(self):
        '''Test closeEvent when there are unsaved events. There should be a popup called'''
    
        # Replace save_project with a mock
        self.window.save_project = MagicMock()

        # Add an event category object
        category = classes.eventCategory.EventCategory(categoryName="TestEventCategory", colour="TestColor")

        # Add an event object
        eventObj = classes.event.Event(id=0, frameNumber=1, duration=0)
        
        #Add event object to category
        category.addEvent(eventObj)

        #Add event category to project
        self.window.project.addCategory(category)

        # Mock QMessageBox.exec_ to return QMessageBox.Save
        with patch('PyQt5.QtWidgets.QMessageBox.exec_', return_value=QMessageBox.Save):

            # Trigger the closeEvent
            self.window.close()

        # Assert that save_project was called
        self.window.save_project.assert_called()

    #Testing the save project method works
    def test_save_project(self):
        '''Test save_project method'''

        # Mock QInputDialog.getText to return a valid project name
        with patch('PyQt5.QtWidgets.QInputDialog.getText', return_value=("TestProject", True)):

            # Mock QMessageBox.exec_ to return QMessageBox.Ok
            with patch('PyQt5.QtWidgets.QMessageBox.exec_', return_value=QMessageBox.Ok):

                # Mock os.path.exists to return False (file does not exist)
                with patch('os.path.exists', return_value=False):

                    # Call save_project
                    self.window.save_project()

                    # Assert that the project name was set correctly
                    assert self.window.project.projectName == "TestProject"

                    # Assert that the project was saved to a file
                    with open("T.json", 'r') as f:
                        saved_project = json.load(f)
                    assert saved_project == self.window.project.to_dict()


                    #Delete the json file after the test
                    os.remove("T.json")

    #Testing the show pose method works changing the constant
    def test_show_pose(self):
        '''Test show_pose method and button'''

        #First test switching from False to True
        # Set to_pose_estimate to False
        self.window.to_pose_estimate = False
        self.window.show_pose()
        assert self.window.to_pose_estimate == True

        #Second test switching from True to False
        # Set to_pose_estimate to True
        self.window.to_pose_estimate = True
        self.window.show_pose()
        assert self.window.to_pose_estimate == False


    #Testing the Load Event Method 
    def test_load_events_file(self):
        '''Test load_events method with both json and non json'''

        #Set the current project's video to the video file that the json file stored
        videoInfoObj = classes.videoInfo.VideoInfo(name="test.mp4", length=1280.0, framerate=29.97002997002997, filepath="C:/Users/chunt/Downloads/test.mp4")
        self.window.project.videoInfo = videoInfoObj

        #Test with JSON
        # Mock QFileDialog.getOpenFileName to return a tuple with a filename and an empty string
        with patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName', return_value=('test.json', '')):

            # Mock json.load to return a dictionary with test data
            with patch('json.load', return_value={'videoInfo': {'name': 'test.mp4', 
                                                                'length': 1280.0,
                                                                'framerate': 29.97002997002997,
                                                                'filepath': 'C:/Users/chunt/Downloads/test.mp4' }}):
                # Call load_events_file
                self.window.load_events_file()

                # Assert that the project was loaded correctly
                assert self.window.project.videoInfo.getFilepath == 'C:/Users/chunt/Downloads/test.mp4'
                assert self.window.project.videoInfo.getName == 'test.mp4'
                assert self.window.project.videoInfo.getLength == 1280.0

        # Test with a non-JSON file
        with patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName', return_value=('test.txt', '')):
            #With patch pressing ok when the dialog box showing the file isn't a json appears.
            with patch('PyQt5.QtWidgets.QMessageBox.warning') as mock_warning:
                self.window.load_events_file()
                mock_warning.assert_called()

    #Testing the functionality to allow the user to set the frame skip size
    def test_set_frame_skip_size(self):
        '''Test set_frame_skip_size method'''

        # Mock QInputDialog.getInt to return a tuple with a test size and True
        with patch('PyQt5.QtWidgets.QInputDialog.getInt', return_value=(50, True)):

            # Call set_frame_skip_size
            # This will trigger the QInputDialog.getInt mock and get a test size of 50
            self.window.set_frame_skip_size()

            # Assert that frame_skip_size was updated correctly
            assert self.window.frame_skip_size == 50

    #Test the functionality that updates the event_combo boxes' contents to the current loaded in project event categories
    def test_update_event_combo(self):
        '''Test the functionality that updates the event_combo boxes' contents to the current loaded in project event categories'''

        # Set up a test project with some event categories
        self.window.project.eventCategories = [
            MagicMock(categoryName='Tim 1'),
            MagicMock(categoryName='Tim 2'),
            MagicMock(categoryName='Tim 3'),
        ]

        # Call update_event_combo
        self.window.update_event_combo()

        # Assert that event_category_combo_box was updated correctly
        assert self.window.event_category_combo_box.count() == 4  # 3 categories + "Add New Event Category"
        assert self.window.event_category_combo_box.itemText(0) == "Add New Event Category"
        assert self.window.event_category_combo_box.itemText(1) == "Tim 1"
        assert self.window.event_category_combo_box.itemText(2) == "Tim 2"
        assert self.window.event_category_combo_box.itemText(3) == "Tim 3" 

    # Test that the event tree can update to the current loaded in project event categories
    def test_update_event_tree_view(self):
        '''Test that the event tree can update to the current loaded in project event categories'''

        # Create 3 events to test with
        event1 = classes.event.Event(id=0, frameNumber=1, duration=0)
        event2 = classes.event.Event(id=1, frameNumber=2, duration=0)
        event3 = classes.event.Event(id=2, frameNumber=3, duration=0)

        # Create 2 event categry objects
        category1 = classes.eventCategory.EventCategory(categoryName='Tim 1')
        category2 = classes.eventCategory.EventCategory(categoryName='Tim 2')

        #Add events to event categories
        category1.addEvent(event1)
        category1.addEvent(event2)
        category2.addEvent(event3)

        # Create event categories and populate the project with them
        self.window.project.eventCategories = [category1, category2]

        # Call update_event_tree_view
        self.window.update_event_tree_view()

        # Assert that event_tree was updated correctly

        # 2 Categories at the top level (Tim 1 and Tim 2)
        assert self.window.event_tree.topLevelItemCount() == 2  

        # Tim 1 has 2 events
        category1 = self.window.event_tree.topLevelItem(0)
        assert category1.text(0) == "Tim 1"
        assert category1.childCount() == 2 
        assert category1.child(0).text(0) == "ID:0 , FrameNumber:1"
        assert category1.child(1).text(0) == "ID:1 , FrameNumber:2"

        # Tim 2 has 1 event
        category2 = self.window.event_tree.topLevelItem(1)
        assert category2.text(0) == "Tim 2"
        assert category2.childCount() == 1
        assert category2.child(0).text(0) == "ID:2 , FrameNumber:3"

    # Test the function that gets called every time the slider is changed
    def test_slider_changed(self):
        '''Test the function that gets called every time the slider is changed'''

        # Mock cv2.VideoCapture to return a mock object
        with patch('cv2.VideoCapture', return_value=MagicMock()) as cap_mock:

            self.window.cap = cv2.VideoCapture("Evan.mp4")

            # Mock self.videoSlider.value to return a test value
            with patch.object(self.window.videoSlider, 'value', new_callable=PropertyMock) as value_mock:
                value_mock.return_value = 50
                # Mock self.display_current_frame as I am not testing it, only that it is called
                with patch.object(self.window, 'display_current_frame') as display_mock:

                    # Call slider_changed
                    self.window.slider_changed()

                    # Assert that currentFrame was updated correctly
                    assert self.window.currentFrame == 50

                    # Assert mock cap object's method was called 
                    cap_mock.return_value.set.assert_called_with(cv2.CAP_PROP_POS_FRAMES, 50)
                    
                    # Assert that display_current_frame was called
                    display_mock.assert_called_once()

    # Test the function to create a new colour
    def test_auto_colour_picker(self):
        '''Test auto_colour_picker method'''

        # Set up a test project with some event categories
        self.window.project.eventCategories = [MagicMock()]

        # Call auto_colour_picker and collect the returned colors
        colors = {self.window.auto_colour_picker()}

        # Assert that auto_colour_picker returned a unique color for each category
        assert len(colors) == 1

        # Assert that auto_colour_picker returns the default color when all colors are used
        self.window.used_colors = set(colors)  # Simulate all colors being used
        assert self.window.auto_colour_picker() == '#FFFFFF'
    
    # Test the function to add a new event category
    def test_add_new_event_category(self):
        '''Test add_new_event_category method'''

        # Mock QInputDialog.getText, when called it will return the defined tuple
        with patch('PyQt5.QtWidgets.QInputDialog.getText', return_value=("Test Category", True)):

            # Mock self.auto_colour_picker to return a test color being the default colour
            with patch.object(self.window, 'auto_colour_picker', return_value="#FFFFFF"):

                # Mock self.project.addCategory and self.update_event_combo
                with patch.object(self.window.project, 'addCategory') as add_mock, patch.object(self.window, 'update_event_combo') as update_mock:

                    # Call add_new_event_category
                    category_name = self.window.add_new_event_category()

                    # Assert that add_new_event_category returned the correct name
                    assert category_name == "Test Category"

                    # Assert that addCategory was called with the correct arguments
                    new_event_category = add_mock.call_args[0][0]
                    assert isinstance(new_event_category, classes.eventCategory.EventCategory)
                    assert new_event_category.categoryName == "Test Category"
                    assert new_event_category.colour == "#FFFFFF"

                    # Assert that update_event_combo was called
                    update_mock.assert_called_once()

    # Test the function to add a new event
    def test_add_event(self):
        '''Test add_event method'''

        # Mock self.event_category_combo_box.currentText to return a test category name
        with patch.object(self.window.event_category_combo_box, 'currentText', return_value="Test Category"):

            # Mock self.add_new_event_category to return a test category name
            with patch.object(self.window, 'add_new_event_category', return_value="Test Category"):

                # Mock self.project.getNumberOfEvents to return a test number of events
                with patch.object(self.window.project, 'getNumberOfEvents', return_value=5):

                    # Mock self.update_markers and self.update_event_tree_view
                    with patch.object(self.window, 'update_markers') as update_markers_mock, patch.object(self.window, 'update_event_tree_view') as update_tree_view_mock:

                        # Set up a test category in the project
                        test_category = MagicMock()
                        test_category.categoryName = "Test Category"
                        self.window.project.eventCategories = [test_category]

                        # Call add_event
                        self.window.add_event()

                        # Assert that a new event was added to the test category
                        new_event = test_category.addEvent.call_args[0][0]
                        assert isinstance(new_event, classes.event.Event)
                        assert new_event.id == 5
                        assert new_event.frameNumber == self.window.currentFrame
        
                        # Assert that update_markers and update_event_tree_view were called
                        update_markers_mock.assert_called_once()
                        update_tree_view_mock.assert_called_once()

    #Test the pause method
    def test_pause(self):
        '''Test pause method'''

        # Mock timer object to assert whether it was called or not
        self.window.timer = MagicMock()

        # Mock self.timer.stop
        with patch.object(self.window.timer, 'stop') as stop_mock:

            # Mock self.style().standardIcon and self.playBtn.setIcon
            with patch.object(self.window.style(), 'standardIcon', return_value="Test Icon") as icon_mock, patch.object(self.window.playBtn, 'setIcon') as set_icon_mock, patch.object(self.window.playBtn, 'setChecked') as set_checked_mock:

                # Call pause
                self.window.pause()

                # Assert that stop was called on the timer
                stop_mock.assert_called_once()

                # Assert that standardIcon was called with the correct argument
                icon_mock.assert_called_once_with(QStyle.SP_MediaPlay)

                # Assert that setIcon was called with the correct argument
                set_icon_mock.assert_called_once_with("Test Icon")

                # Assert that setChecked was called with the correct argument
                set_checked_mock.assert_called_once_with(False)

    # Test the play_video method by mocking the methods and objects it calls
    def test_play_video(self):
        '''Test play_video method'''

        #Mocking the video object to check if it has been called as expected
        self.window.cap = MagicMock()
        # Mock timer object to assert whether it was called or not
        self.window.timer = MagicMock()

        # Mock self.cap.isOpened and self.playBtn.isChecked to return True
        with patch.object(self.window.cap, 'isOpened', return_value=True), patch.object(self.window.playBtn, 'isChecked', return_value=True):

            # Mock self.cap.get to return a test FPS
            with patch.object(self.window.cap, 'get', return_value=30):

                # Mock self.timer.start
                with patch.object(self.window.timer, 'start') as start_mock:

                    # Mock self.style().standardIcon and self.playBtn.setIcon
                    with patch.object(self.window.style(), 'standardIcon', return_value="Test Icon") as icon_mock, patch.object(self.window.playBtn, 'setIcon') as set_icon_mock:

                        # Call play_video
                        self.window.play_video()

                        # Assert that start was called on the timer with the correct argument 30FPS = 33ms
                        start_mock.assert_called_once_with(33)

                        # Assert that standardIcon was called with the correct argument
                        icon_mock.assert_called_once_with(QStyle.SP_MediaPause)

                        # Assert that setIcon was called with the correct argument
                        set_icon_mock.assert_called_once_with("Test Icon")

        # Testing the flip side functionality when playBtn is not checked
        # Mock self.cap.isOpened and self.playBtn.isChecked to return True and False, respectively
        with patch.object(self.window.cap, 'isOpened', return_value=True), patch.object(self.window.playBtn, 'isChecked', return_value=False):

            # Mock self.pause
            with patch.object(self.window, 'pause') as pause_mock:

                # Call play_video
                self.window.play_video()

                # Assert that pause was called
                pause_mock.assert_called_once()

    # Test the open_file method when a user selects a file
    def test_open_file(self):
        '''Test open_file method'''

        # Mock the file dialog and the user selecting test.mp4 when no events exist not triggering the saveEvent path
        with patch.object(QFileDialog, 'getOpenFileName', return_value=("test.mp4", "*.mp4")) as file_dialog_mock:

            # Mock self.project.getNumberOfEvents to return 0 (mocking the project having no events and this being the first video file)
            with patch.object(self.window.project, 'getNumberOfEvents', return_value=0) as get_number_of_events_mock:

                # Mock cv2's VideoCapture to return a mock object
                with patch.object(cv2, 'VideoCapture') as video_capture_mock:

                    # Mock self.nextFrameSlot to check if the open file method calls this to display the first frame
                    with patch.object(self.window, 'nextFrameSlot') as next_frame_slot_mock:

                        # Call open_file
                        self.window.open_file()

                        # List of things the method should have done
                        # Assert a file dialog was opened for the user to select a file
                        file_dialog_mock.assert_called_once()

                        # Assert get_number_of_events was called to check if the project has any events
                        get_number_of_events_mock.assert_called_once()

                        # Assert that VideoCapture was called with the correct argument
                        video_capture_mock.assert_called_once_with("test.mp4")

                        # Assert that nextFrameSlot was called
                        next_frame_slot_mock.assert_called_once()                

        # Mock the file dialog and the user selecting test.mp4 when events exist triggering the saveEvent path
                        
        # Same as before, mocking a file  dialog
        with patch.object(QFileDialog, 'getOpenFileName', return_value=("test.mp4", "*.mp4")) as file_dialog_mock:

            # Mock self.project.getNumberOfEvents to return 1 (mocking the project having events and this not being the first video file)
            with patch.object(self.window.project, 'getNumberOfEvents', return_value=1):
                
                # Mock QMessageBox.exec_ to appear and the user selecting to discard the events
                with patch.object(QMessageBox, 'exec_', return_value=QMessageBox.Discard) as message_box_mock:

                    # Mock self.save_project to check if it was not called since the user selected to discard the events
                    with patch.object(self.window, 'save_project') as save_project_mock:
                        
                         # Mock cv2's VideoCapture to return a mock object
                        with patch.object(cv2, 'VideoCapture') as video_capture_mock:

                            # Mock self.nextFrameSlot to check if the open file method calls this to display the first frame
                            with patch.object(self.window, 'nextFrameSlot') as next_frame_slot_mock:

                                # Call open_file
                                self.window.open_file()

                                # List of things the method should have done
                                # Assert a file dialog was opened for the user to select a file
                                file_dialog_mock.assert_called_once()

                                # Assert get_number_of_events was called to check if the project has any events
                                get_number_of_events_mock.assert_called_once()

                                # Assert the message box to prompt the user to save was called
                                message_box_mock.assert_called_once()

                                # Assert that save_project was not called as the user selected to discard the events
                                save_project_mock.assert_not_called()
                                
                                # Assert that VideoCapture was called with the correct argument
                                video_capture_mock.assert_called_once_with("test.mp4")

                                # Assert that nextFrameSlot was called
                                next_frame_slot_mock.assert_called_once()
               
        