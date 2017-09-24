#!/usr/bin/env python

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from markdownview import MarkdownView
import doorstop
from documentview import DocumentTreeView


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    splitter = QSplitter()
    splitter.resize(1024, 768)

    v = MarkdownView()

    db = doorstop.core.builder.build()
    tree = DocumentTreeView()
    tree.connectdb(db)
    tree.connectview(v)
    splitter.addWidget(tree)
    splitter.addWidget(v)
    splitter.setSizes([320, 768])

    splitter.show()

    sys.exit(app.exec_())
