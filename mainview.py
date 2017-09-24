#!/usr/bin/env python

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from markdownview import MarkdownView
import doorstop
from documentview import DocumentTreeView
from createcatdiag import CreateCategoryDialog


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

    tree = DocumentTreeView()
    tree.connectview(v)
    tree.connectcreatecatdiag(createcatdiag)

    db = ReqDatabase()
    db.add_listeners([tree, createcatdiag])

    splitter.addWidget(tree)
    splitter.addWidget(v)
    splitter.setSizes([320, 768])

    splitter.show()

    sys.exit(app.exec_())
