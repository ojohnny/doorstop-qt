from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from markdown import markdown


class LinkView(QListView):
    def __init__(self, parent=None):
        super(LinkView, self).__init__(parent)

        self.db = None
        self.model = QStandardItemModel()
        self.setModel(self.model)
        self.setAlternatingRowColors(True)
        self.linkentry = None
        def dataChanged(index):
            if self.db is None:
                return
            if self.currentuid is None:
                return
            item = self.model.itemFromIndex(index)
            data = item.data()
            uid = item.text()
            if data is None:
                doc = self.db.find(uid)
                if doc is not None:
                    self.db.root.link_items(self.currentuid, uid)
            else:
                doc = self.db.find(uid)
                if uid == '' or doc is not None:
                    olduid = str(data.uid)
                    self.db.root.unlink_items(self.currentuid, olduid)
                if doc is not None:
                    self.db.root.link_items(self.currentuid, uid)

            self.read(self.currentuid)
        self.model.dataChanged.connect(dataChanged)

        self.clicked.connect(lambda s: self.edit(s))

    def connectdb(self, db):
        self.db = db

    def read(self, uid):
        if self.db is None:
            return

        self.currentuid = None

        data = self.db.find(uid)
        self.model.clear()
        self.linkentry = QStandardItem('<Click here to add parent link>')
        self.model.appendRow(self.linkentry)
        for link in data.links:
            d = self.db.find(str(link))
            text = QTextDocument()
            text.setHtml(markdown(d.text.split('\n')[0]))
            item = QStandardItem(str(link) + '\t' + text.toPlainText())
            item.setData(d)
            self.model.appendRow(item)

        clinks = data.find_child_links()
        for clink in clinks:
            d = self.db.find(str(clink))
            text = QTextDocument()
            text.setHtml(markdown(d.text.split('\n')[0]))
            item = QStandardItem('linked from: ' + str(clink) + '\t' + text.toPlainText())
            item.setData(d)
            self.model.appendRow(item)

        if self.model.rowCount() < 6:
            self.model.setRowCount(6)

        self.currentuid = uid
