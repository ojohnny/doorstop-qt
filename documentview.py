from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from icon import Icon


class CategorySelector(QWidget):
    def __init__(self, parent=None):
        super(CategorySelector, self).__init__(parent)
        self.grid = QHBoxLayout()
        self.grid.setSpacing(10)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.combo = QComboBox()
        icons = Icon()
        self.newcatbtn = QPushButton(icons.FileDialogNewFolder, '')
        self.newcatbtn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.grid.addWidget(self.combo)
        self.grid.addWidget(self.newcatbtn)
        self.setLayout(self.grid)
        self.db = None

    def connectdb(self, db):
        self.db = db
        self.buildlist()

    def buildlist(self):
        if self.db is None or len(self.db.documents) == 0:
            return
        self.combo.clear()
        graph = self.db.draw().split('\n')
        self.combo.addItems([x for x in graph if x.split()[-1].isidentifier()])

    def callback(self, func):
        def clb(index):
            cat = self.combo.itemText(index).split()[-1]
            func(cat)
        self.combo.currentIndexChanged.connect(clb)


class DocumentTreeView(QWidget):
    def __init__(self, parent=None):
        super(DocumentTreeView, self).__init__(parent)

        self.tree = QTreeView()
        self.tree.header().hide()
        self.tree.setIndentation(20)
        self.model = QStandardItemModel()

        self.catselector = CategorySelector()
        self.catselector.callback(self.buildtree)

        self.db = None
        self.editview = None
        self.icons = Icon()

        oldSelectionChanged = self.tree.selectionChanged
        def selectionChanged(selected, deselected):
            if self.editview is not None:
                si = selected.indexes()
                di = deselected.indexes()
                if selected and deselected:
                    if len(di) > 0:
                        data = self.model.data(di[0], Qt.UserRole + 2)
                        data.text = self.editview.text()
                if len(si) > 0:
                    data = self.model.data(si[0], Qt.UserRole + 2)
                    self.editview.settext(data.text)
                else:
                    self.editview.settext('')

            oldSelectionChanged(selected, deselected)
        self.tree.selectionChanged = selectionChanged
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.contextmenu)
        self.tree.setModel(self.model)

        self.grid = QVBoxLayout()
        self.grid.addWidget(self.catselector)
        self.grid.addWidget(self.tree)
        self.setLayout(self.grid)

    def contextmenu(self, pos):
        menu = QMenu(parent=self.tree)
        si = self.tree.selectedIndexes()
        if len(si) > 0:
            act = menu.addAction(self.icons.DialogSaveButton, 'Commit changes')
            act.setEnabled(False)
            act = menu.addAction(self.icons.DialogDiscardButton, 'Discard changes')
            act.setEnabled(False)
            menu.addSeparator()

            data = self.model.data(si[0], Qt.UserRole + 2)
            menu.addAction(self.icons.FileIcon, 'Create sibling document')
            act = menu.addAction(self.icons.FileIcon, 'Create child document')
            if str(data.level).split('.')[-1] != '0':
                act.setEnabled(False)

            menu.addSeparator()
            act = menu.addAction('Remove document')
            act.setEnabled(False)
        else:
            menu.addAction(self.icons.FileIcon, 'Create document')
        menu.addSeparator()
        menu.addAction('Expand all').triggered.connect(lambda: self.tree.expandAll())
        def collapse():
            self.tree.collapseAll()
            self.tree.clearSelection()
        menu.addAction('Collapse all').triggered.connect(collapse)
        menu.popup(self.tree.mapToGlobal(pos))

    def buildtree(self, cat=None):
        self.model.clear()
        if self.db is None or len(self.db.documents) == 0:
            return
        if cat is None:
            cat = self.db.documents[0].prefix
        c = [x for x in self.db if x.prefix == cat][0]
        items = {}
        for doc in sorted(c, key=lambda x: x.level):
            level = str(doc.level)
            title = '{} {}{:03}'.format(level, doc.prefix, doc.number)
            item = QStandardItem(title)
            item.setData(doc, Qt.UserRole + 2)
            items[level] = item
            up = level.split('.')
            up[-1] = '0'
            up = '.'.join(up)
            if up != level and up in items:
                items[up].appendRow(item)
            else:
                self.model.appendRow(item)
        self.tree.setCurrentIndex(self.model.index(0, 0))

    def connectdb(self, db):
        self.db = db
        self.buildtree()
        self.catselector.connectdb(db)

    def connectview(self, view):
        self.editview = view