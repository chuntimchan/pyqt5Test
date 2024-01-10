import sys,os
from unittest.mock import patch, MagicMock, call,  ANY
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PyQt5.QtCore import Qt, QPointF, QEvent
from PyQt5.QtGui import QMouseEvent, QPainter, QColor
from PyQt5.QtWidgets import QApplication, QSlider
import src.MarkerSlider as MarkerSlider
import pytest

class TestMarkerSlider:
    def setup_method(self, method):
        '''Set up the MarkerSlider object before each test'''
        self.app = QApplication([])
        self.slider = MarkerSlider.MarkerSlider()
        self.slider.setRange(0, 100)  # Set the range of the slider
        self.slider.setMarkers([(50,50, 'red'), (75,50,'blue')])  # Set the markers

    def test_mousePressEvent_on_marker(self):
        '''Test mousePressEvent when the click is on a marker'''

        # Create a mock QMouseEvent
        event = QMouseEvent(QEvent.MouseButtonPress, QPointF(0, 0), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
        # Mock the x method to return 50 which is on the marker
        event.x = MagicMock(return_value=50)  
        # Mock the width method to return 100
        self.slider.width = MagicMock(return_value=100)  

        # Create a mock method and connect it to the markerClicked signal to simulate if this was called or not
        mock_marker_clicked_method = MagicMock()
        self.slider.markerClicked.connect(mock_marker_clicked_method)

        # Mock self.setValue and self.markerClicked.emit
        with patch.object(self.slider, 'setValue') as set_value_mock:

            # Call mousePressEvent
            self.slider.mousePressEvent(event)

            print(self.slider.markers)
            # Assert that setValue and emit were called with the correct argument
            set_value_mock.assert_called_once_with(50)
            mock_marker_clicked_method.assert_called_once_with(50)

    def test_mousePressEvent_off_marker(self):
        '''Test mousePressEvent when the click is not on a marker'''

        # Create a mock QMouseEvent
        event = QMouseEvent(QEvent.MouseButtonPress, QPointF(0, 0), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)

        # Mock the parent class's mousePressEvent
        with patch.object(QSlider, 'mousePressEvent') as mouse_press_event_mock:

            # Call mousePressEvent
            self.slider.mousePressEvent(event)

            # Assert that the parent class's mousePressEvent was called
            mouse_press_event_mock.assert_called_once_with(event)

    def test_paintEvent_with_markers(self):
        '''Test paintEvent when the markers list is not empty'''
        # Mock QPainter to allow us to assert whether it has been called. It mocks the original QPainter class, only difference is our ability 
        # to assert whether it has been called. This mocks the QPainter class in the MarkerSlider.py file
        with patch('src.MarkerSlider.QPainter', autospec=True) as painter_mock:

            # Create an instance of QPainter
            painter_instance = painter_mock.return_value

            # Call paintEvent with no event as it's not used

            self.slider.paintEvent(None)

        # Assert that the QPainter methods were called with the correct arguments
        assert painter_instance.setBrush.call_count == 2

        #This was needed due to the inability to compare 2 identical objects as this QColor object is created in the MarkerSlider class and
        #the one in this test is created in this test and these 2 objects are identical but not in the same memory location
        assert painter_instance.setBrush.call_args_list[0][0][0].name() == QColor('red').name()
        assert painter_instance.setBrush.call_args_list[1][0][0].name() == QColor('blue').name()        
        
        painter_instance.drawPolygon.assert_called()
        assert painter_instance.save.call_count == 2
        assert painter_instance.restore.call_count == 2