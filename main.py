import sys

from PyQt6.QtWidgets import QApplication,QDialog,QGridLayout,QLineEdit,QMainWindow,QPushButton,QTabWidget,QTableWidget,QTextEdit,QVBoxLayout,QWidget

class Editor(QDialog):
	def __init__(self,text):
		super().__init__()
		self.setWindowTitle("编辑")
		self.resize(400,400)
		layout=QVBoxLayout()
		self.setLayout(layout)
		layout.addWidget(QTextEdit(text,self))
		layout.addWidget(QPushButton("确定",self,clicked=self.accept))
		layout.addWidget(QPushButton("取消",self,clicked=self.reject))

class VSTC(QMainWindow):
	def __init__(self):
		super().__init__()

		self.setWindowTitle("Sentences")
		self.resize(500,500)
		tab=QTabWidget(self)

		tab.addTab(self.main(),"管理")
		tab.addTab(self.search(),"搜索")
		tab.addTab(self.label(),"标签")
		tab.addTab(self.preference(),"设置")

		self.setCentralWidget(tab)

	def main(self):
		widget=QWidget(self)
		layout=QGridLayout()
		widget.setLayout(layout)
		for i in range(5):
			layout.setColumnStretch(i,1)

		self.mainBtn=QPushButton("添加",self,clicked=lambda _:self.add())
		layout.addWidget(self.mainBtn,0,0,1,5)

		self.mainTable=QTableWidget(self)
		self.mainTable.setColumnCount(5)
		self.mainTable.setHorizontalHeaderLabels(["句子","标签","时间","编辑","删除"])
		width=[285,60,80,50,50]
		for i in range(5):
			self.mainTable.setColumnWidth(i,width[i])
		layout.addWidget(self.mainTable,1,0,1,5)

		return widget

	def search(self):
		widget=QWidget(self)
		layout=QGridLayout()
		widget.setLayout(layout)
		for i in range(5):
			layout.setColumnStretch(i,1)

		self.searchTxt=QLineEdit(self,placeholderText="text")
		self.searchBtn=QPushButton("搜索",self,clicked=lambda _:self.search())
		self.searchTxt.returnPressed.connect(self.searchBtn.click)
		layout.addWidget(self.searchTxt,0,0,1,4)
		layout.addWidget(self.searchBtn,0,4,1,1)

		self.searchTable=QTableWidget(self)
		self.searchTable.setColumnCount(5)
		self.searchTable.setHorizontalHeaderLabels(["句子","标签","时间","编辑","删除"])
		width=[285,60,80,50,50]
		for i in range(5):
			self.searchTable.setColumnWidth(i,width[i])
		layout.addWidget(self.searchTable,1,0,1,5)

		return widget

	def label(self):
		widget=QWidget(self)
		layout=QGridLayout()
		widget.setLayout(layout)
		for i in range(5):
			layout.setColumnStretch(i,1)

		self.labelBtn=QPushButton("添加",self,clicked=lambda _:self.add())
		layout.addWidget(self.labelBtn,0,0,1,5)

		self.labelTable=QTableWidget(self)
		self.labelTable.setColumnCount(4)
		self.labelTable.setHorizontalHeaderLabels(["标签","计数","编辑","删除"])
		width=[200,80,50,50]
		for i in range(4):
			self.labelTable.setColumnWidth(i,width[i])
		layout.addWidget(self.labelTable,1,0,1,5)

		return widget

	def preference(self):
		widget=QWidget(self)
		layout=QGridLayout()
		widget.setLayout(layout)
		return widget

if __name__=="__main__":
	app=QApplication(sys.argv)
	ex=VSTC()
	ex.show()
	sys.exit(app.exec())
