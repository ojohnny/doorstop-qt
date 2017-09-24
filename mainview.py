#!/usr/bin/env python

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from markdownview import MarkdownView
import doorstop
from documentview import DocumentTreeView
from createcatdiag import CreateCategoryDialog
from attributeview import AttributeView


class ReqDatabase(object):
    def __init__(self):
        self.listeners = []
        self.root = None
        self.reload()

    def add_listeners(self, l):
        if type(l) is list:
            for listener in l:
                listener.connectdb(self)
                self.listeners.append(listener)
        else:
            l.connectdb(self)
            self.listeners.append(l)

    def reload(self):
        self.root = doorstop.core.builder.build()
        for l in self.listeners:
            l.connectdb(self)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    splitter = QSplitter()
    splitter.resize(1024, 768)

    v = MarkdownView()
    createcatdiag = CreateCategoryDialog()

    attribview = AttributeView()

    tree = DocumentTreeView()
    tree.connectview(v)
    tree.connectcreatecatdiag(createcatdiag)
    def selectfunc(uid):
        attribview.read(uid)
        v.read(uid)
    tree.selectionclb = selectfunc

    db = ReqDatabase()
    db.add_listeners(attribview)
    v.readfunc = lambda uid: db.root.find_item(uid).text
    def savefunc(uid, text):
        db.root.find_item(uid).text = text
    v.savefunc = savefunc
    db.add_listeners([tree, createcatdiag])

    editor = QWidget()
    editorgrid = QVBoxLayout()
    editorgrid.addWidget(attribview)
    editorgrid.addWidget(v)
    editor.setLayout(editorgrid)

    splitter.addWidget(tree)
    splitter.addWidget(editor)
    splitter.setSizes([320, 768])

    splitter.show()

    sys.exit(app.exec_())
