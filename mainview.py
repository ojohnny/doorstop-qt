#!/usr/bin/env python

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from markdownview import MarkdownView
import doorstop


def buildtree(cat, root):
    t = doorstop.core.builder.build()
    c = [x for x in t if x.prefix == cat][0]
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
            root.appendRow(item)


class Icon(object):
    def __init__(self):
        style = QCommonStyle()
        icons = [x for x in dir(QStyle) if x.startswith('SP_')]
        self.names = []
        for name in icons:
            icon = style.standardIcon(getattr(QStyle, name))
            setattr(self, name[3:], icon)
            self.names.append(name[3:])

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    icons = Icon()
    splitter = QSplitter()
    splitter.resize(1024, 768)

    v = MarkdownView()

    tree = QTreeView()
    model = QStandardItemModel()
    splitter.addWidget(tree)
    splitter.addWidget(v)
    splitter.setSizes([320, 768])
    tree.setContextMenuPolicy(Qt.CustomContextMenu)
    def treecontextmenu(pos):
        menu = QMenu(parent=tree)
        si = tree.selectedIndexes()
        if len(si) > 0:
            act = menu.addAction(icons.DialogSaveButton, 'Commit changes')
            act.setEnabled(False)
            act = menu.addAction(icons.DialogDiscardButton, 'Discard changes')
            act.setEnabled(False)
            menu.addSeparator()

            data = model.data(si[0], Qt.UserRole + 2)
            menu.addAction(icons.FileIcon, 'Create sibling document')
            act = menu.addAction(icons.FileIcon, 'Create child document')
            if str(data.level).split('.')[-1] != '0':
                act.setEnabled(False)

            menu.addSeparator()
            act = menu.addAction('Remove document')
            act.setEnabled(False)
        else:
            menu.addAction(icons.FileIcon, 'Create document')
        menu.addSeparator()
        menu.addAction('Expand all').triggered.connect(lambda: tree.expandAll())
        def collapse():
            tree.collapseAll()
            tree.clearSelection()
        menu.addAction('Collapse all').triggered.connect(collapse)
        menu.popup(tree.mapToGlobal(pos))
    tree.customContextMenuRequested.connect(treecontextmenu)

    tree.header().hide()
    tree.setIndentation(20)

    oldSelectionChanged = tree.selectionChanged
    def selectionChanged(selected, deselected):
        si = selected.indexes()
        di = deselected.indexes()
        if selected and deselected:
            if len(di) > 0:
                data = model.data(di[0], Qt.UserRole + 2)
                data.text = v.text()
        if len(si) > 0:
            data = model.data(si[0], Qt.UserRole + 2)
            v.settext(data.text)
        else:
            v.settext('')
        oldSelectionChanged(selected, deselected)
    tree.selectionChanged = selectionChanged
    tree.setModel(model)

    splitter.show()
    buildtree('req', model)

    sys.exit(app.exec_())
