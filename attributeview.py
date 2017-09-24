from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class AttributeView(QWidget):
    def __init__(self, parent=None):
        super(AttributeView, self).__init__(parent)

        self.db = None
        self.currentuid = None

        grid = QHBoxLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        self.active = QCheckBox('Active')
        self.derived = QCheckBox('Derived')
        self.normative = QCheckBox('Normative')
        self.heading = QCheckBox('Heading')

        def active(s):
            if self.currentuid is None:
                return
            data = self.db.find(self.currentuid)
            data.active = True if s == Qt.Checked else False
            self.read(self.currentuid)
            self.db.reload()
        self.active.stateChanged.connect(active)

        def derived(s):
            if self.currentuid is None:
                return
            data = self.db.find(self.currentuid)
            data.derived = True if s == Qt.Checked else False
            self.read(self.currentuid)
            self.db.reload()
        self.derived.stateChanged.connect(derived)

        def normative(s):
            if self.currentuid is None:
                return
            data = self.db.find(self.currentuid)
            data.normative = True if s == Qt.Checked else False
            self.read(self.currentuid)
            self.db.reload()
        self.normative.stateChanged.connect(normative)

        def heading(s):
            if self.currentuid is None:
                return
            data = self.db.find(self.currentuid)
            data.heading = True if s == Qt.Checked else False
            self.read(self.currentuid)
            self.db.reload()
        self.heading.stateChanged.connect(heading)

        grid.addWidget(self.active)
        grid.addWidget(self.derived)
        grid.addWidget(self.normative)
        grid.addWidget(self.heading)
        grid.addStretch(1)
        self.setLayout(grid)

    def connectdb(self, db):
        self.db = db
        self.read(self.currentuid)

    def read(self, uid):
        if uid is None:
            return
        self.currentuid = None
        if self.db is None:
            return
        data = self.db.find(uid)
        self.active.setCheckState(Qt.Checked if data.active else Qt.Unchecked)
        self.derived.setCheckState(Qt.Checked if data.derived else Qt.Unchecked)
        self.normative.setCheckState(Qt.Checked if data.normative else Qt.Unchecked)
        self.heading.setCheckState(Qt.Checked if data.heading else Qt.Unchecked)
        self.currentuid = uid
