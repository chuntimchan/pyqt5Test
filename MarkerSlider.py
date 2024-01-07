from PyQt5.QtWidgets import QSlider, QToolTip
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QPolygon
from PyQt5.QtCore import QPoint, pyqtSignal


class MarkerSlider(QSlider):
    #New marker clicked signal
    markerClicked = pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        super(MarkerSlider, self).__init__(*args, **kwargs)
        self.markers = []
        self.setMouseTracking(True)  # Enable mouse tracking

    def setMarkers(self, markers):
        self.markers = markers
        self.update()  # Trigger a repaint

    def addMarker(self, frame,color = QColor(255, 0, 0)):
        #Make marker a tuple of (frameNumber,colour)
        marker = (frame,self.value(),color)
        self.markers.append(marker)
        self.update()

    def paintEvent(self, e):
        super(MarkerSlider, self).paintEvent(e)

        if not self.markers:
            return

        painter = QPainter(self)
        #print(self.markers)
        for marker in self.markers:
            x = self.width() * (marker[0] / self.maximum())
            x = int(x)  # Convert x to an integer

            painter.save()  # Save the painter state
            #print(marker[1])
            painter.setBrush(QColor(marker[2]))  # Set the brush color for markers

            # Define the points of the triangle
            points = [QPoint(x, 10), QPoint(x - 5, 0), QPoint(x + 5, 0)]
            triangle = QPolygon(points)

            painter.drawPolygon(triangle)

            painter.restore()  # Restore the painter state

    #Detect if a mouse is hovering over a marker
    def mouseMoveEvent(self, e):
        for marker in self.markers:
            x = self.width() * (marker[0] / self.maximum())
            x = int(x)  # Convert x to an integer
            if abs(e.x() - x) < 3:  # If the mouse is within 3 pixels of the marker
                QToolTip.showText(e.globalPos(), f"Marker at {marker[0]}")
                break
        else:  # If the loop didn't break, the mouse isn't over any marker
            QToolTip.hideText()
        super(MarkerSlider, self).mouseMoveEvent(e)

    #Detect if a mouse click is over a marker
    def mousePressEvent(self, e):
        for marker in self.markers:
            x = self.width() * (marker[0] / self.maximum())
            x = int(x)  # Convert x to an integer
            if abs(e.x() - x) < 3:  # If the click is within 3 pixels of the marker
                self.setValue(marker[0])  # Set the slider to the marker's value
                self.markerClicked.emit(marker[0])  # Emit the markerClicked signal
                break
        else:  # If the loop didn't break, the click wasn't on any marker
            super(MarkerSlider, self).mousePressEvent(e)  # Call the parent class's mousePressEvent to handle the click normally