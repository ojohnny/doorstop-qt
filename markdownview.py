#!/usr/bin/env python

import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class SimpleMarkdownHighlighter(QSyntaxHighlighter):
    def highlightBlock(self, text):
        import re

        self.matchAndApply('^#.*', text, 'b', sz=3)
        self.matchAndApply('^##.*', text, 'b', sz=2)
        self.matchAndApply('^###.*', text, 'b', sz=1)
        self.matchAndApply('^####.*', text, 'b', sz=0)
        self.matchAndApply('^#####.*', text, 'b', sz=-1)
        self.matchAndApply('!\[[^]]*\]\([^)]*\)', text, 'i', color=QColor('#336699'))
        self.matchAndApply('(?<!!)\[[^]]*\]\([^)]*\)', text, 'u', color=QColor('blue'))
        self.matchAndApply('(?<![\w\\\\])_((?!_\s).)*_(?!\w)', text, 'i')
        self.matchAndApply('(?<!\\\\)\*[^\s][^\*]*\*(?!\*)', text, 'i')
        self.matchAndApply('(?<!\\\\)\*\*[^\s]((?!\*\*).)*(?!\s)\*\*', text, 'b')

    def setformat(self, idx, length, attr, color=None, sz=None):
        fmt = self.format(idx)
        if 'b' in attr:
            fmt.setFontWeight(QFont.Bold)
        if 'u' in attr:
            fmt.setFontUnderline(True)
        if color is not None:
            fmt.setForeground(color)
        if 'i' in attr:
            fmt.setFontItalic(True)
        if sz is not None:
            fmt.setProperty(QTextFormat.FontSizeAdjustment, sz)

        self.setFormat(idx, length, fmt)

    def matchAndApply(self, rexp, text, attr, color=None, sz=None):
        import re

        for match in re.finditer(rexp, text):
            idx, end = match.span()
            self.setformat(idx, end - idx, attr, color, sz)


class MarkdownEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super(MarkdownEditor, self).__init__(parent)
        self.highlighter = SimpleMarkdownHighlighter(self.document())

    def dropEvent(self, ev):
        from os.path import basename
        from urllib.request import FancyURLopener
        from base64 import b64encode
        import imghdr

        c = self.cursorForPosition(ev.pos())
        s = ev.mimeData().text().split('\n')
        for url in s:
            url = url.strip()
            if len(url):
                data = FancyURLopener().open(url).read()
                t = imghdr.what(None, h=data)
                data = b64encode(data).decode('utf-8')
                if t is None:
                    continue
                if c.block().length() != 1:
                    c.insertBlock()
                if c.block().previous().length() != 1:
                    c.insertBlock()
                data = 'data:image/' + t + ';base64,' + data
                c.insertText('![{0}]({1})'.format(basename(url), data))
                if c.block().next().length() != 1:
                    c.insertBlock()
                else:
                    c.movePosition(QTextCursor.NextBlock)

        self.setTextCursor(c)

        mimeData = QMimeData()
        mimeData.setText("")
        dummyEvent = QDropEvent(ev.posF(), ev.possibleActions(),
                mimeData, ev.mouseButtons(), ev.keyboardModifiers())

        super(MarkdownEditor, self).dropEvent(dummyEvent)


class MarkdownView(QWidget):
    def __init__(self, text='', parent=None):
        super(MarkdownView, self).__init__(parent)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.htmlview = QTextEdit()
        self.htmlview.setReadOnly(True)
        self.editview = MarkdownEditor()
        self.editview.setWordWrapMode(QTextOption.ManualWrap)
        self.editview.setPlainText(text)
        self.previewbtn = QPushButton("Preview")
        self.previewbtn.clicked.connect(self.viewhtml)
        self.editbtn = QPushButton("Edit")
        self.editbtn.clicked.connect(self.vieweditor)
        self.layout.addWidget(self.editview)
        self.layout.addWidget(self.htmlview)
        self.layout.addWidget(self.editbtn)
        self.layout.addWidget(self.previewbtn)
        self.text = self.editview.document().toPlainText
        self.connectzoomfunctions()
        self.viewhtml()

    def viewhtml(self):
        from markdown import markdown
        ext = (
            'markdown.extensions.extra',
            'markdown.extensions.sane_lists'
        )

        html = markdown(self.text(), extensions=ext)
        self.htmlview.setHtml(html)
        self.htmlview.setVisible(True)
        self.editbtn.setVisible(True)
        self.editview.setVisible(False)
        self.previewbtn.setVisible(False)

    def vieweditor(self):
        self.editview.setVisible(True)
        self.previewbtn.setVisible(True)
        self.htmlview.setVisible(False)
        self.editbtn.setVisible(False)
        self.editview.setFocus()

    def connectzoomfunctions(self):
        def zoomeditor(ev):
            if ev.modifiers() & Qt.ControlModifier:
                # zoom only works in read-only mode
                self.editview.setReadOnly(True)
                super(MarkdownEditor, self.editview).wheelEvent(ev)
                self.editview.setReadOnly(False)

                if self.editview.isVisible():
                    self.htmlview.wheelEvent(ev)
            else:
                super(MarkdownEditor, self.editview).wheelEvent(ev)

        htmlzoom = self.htmlview.wheelEvent
        def zoomhtml(ev):
            htmlzoom(ev)
            if self.htmlview.isVisible():
                self.editview.wheelEvent(ev)

        self.htmlview.wheelEvent = zoomhtml
        self.editview.wheelEvent = zoomeditor

    def settext(self, newtext):
        self.editview.setPlainText(newtext)
        self.viewhtml()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MarkdownView()
    w.show()

    sys.exit(app.exec_())
