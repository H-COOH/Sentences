import datetime
import sqlite3
import sys

from PyQt6.QtCore import QSettings,Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication,QDialog,QGridLayout,QLabel,QLineEdit,QMainWindow,QMessageBox,QPlainTextEdit,QPushButton,QTabWidget,QTableWidget,QWidget

con=sqlite3.connect("sentences.db")
cur=con.cursor()

label_id=0

def confirm(parent,title,text):
	res=QMessageBox.question(parent,title,text,QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)
	return res==QMessageBox.StandardButton.Yes

class Sel_Label(QDialog):
	def __init__(self):
		super().__init__()

		self.setWindowTitle("选择标签")
		self.setFixedWidth(200)
		layout=QGridLayout()
		self.setLayout(layout)
		for i in range(5):
			layout.setColumnStretch(i,1)

		self.labelTable=QTableWidget(self)
		self.labelTable.setColumnCount(2)
		self.labelTable.setHorizontalHeaderLabels(["标签","选择"])
		width=[100,50]
		for i in range(2):
			self.labelTable.setColumnWidth(i,width[i])
		layout.addWidget(self.labelTable,0,0,1,5)

		layout.addWidget(QPushButton("取消",self,clicked=self.reject),1,3,1,2)
		layout.setSpacing(15)
		layout.setContentsMargins(15,15,15,15)

		labels=cur.execute("SELECT * FROM labels").fetchall()
		for k,v in enumerate(labels):
			self.labelTable.insertRow(k)
			label=QLabel(v[1],self)
			if v[0]==label_id:
				bold=QFont()
				bold.setBold(True)
				label.setFont(bold)
			self.labelTable.setCellWidget(k,0,label)
			label.setAlignment(Qt.AlignmentFlag.AlignCenter)
			self.labelTable.setCellWidget(k,1,QPushButton("选择",self,clicked=lambda _,id=v[0]:self.sel_item(id)))

	def sel_item(self,id):
		global label_id
		label_id=id
		self.accept()

class Edit_Quote(QDialog):
	def __init__(self,id):
		super().__init__()

		self.id=id
		self.setWindowTitle("摘录")
		self.setFixedWidth(250)
		layout=QGridLayout()
		self.setLayout(layout)
		for i in range(5):
			layout.setColumnStretch(i,1)

		layout.addWidget(QLabel("摘录内容：",self),0,0,1,5)
		res=cur.execute("SELECT quote,label FROM quotes WHERE id=?",(id,)).fetchone() if ~id else ("",0)
		self.quoteEdit=QPlainTextEdit(res[0],self)
		self.label=res[1]
		layout.addWidget(self.quoteEdit,1,0,1,5)
		layout.addWidget(QLabel("标签：",self),2,0,1,1)
		self.name=QLabel(self)
		self.set_name()
		layout.addWidget(self.name,2,1,1,2)
		layout.addWidget(QPushButton("选择",self,clicked=self.sel_label),2,3,1,2)

		layout.addWidget(QPushButton("确定",self,clicked=self.save),3,0,1,2)
		layout.addWidget(QPushButton("取消",self,clicked=self.reject),3,3,1,2)
		layout.setSpacing(15)
		layout.setContentsMargins(15,15,15,15)

	def set_name(self):
		name=cur.execute("SELECT label FROM labels WHERE id=?",(self.label,)).fetchone()
		self.name.setText(name[0])

	def sel_label(self):
		global label_id
		label_id=self.label
		Sel_Label().exec()
		self.label=label_id
		self.set_name()

	def save(self):
		quote=self.quoteEdit.toPlainText()
		time=str(datetime.datetime.now())
		if ~self.id: cur.execute("UPDATE quotes SET quote=?,label=? WHERE id=?",(quote,self.label,self.id))
		else: cur.execute("INSERT INTO quotes (quote,label,time) VALUES (?,?,?)",(quote,self.label,time))
		con.commit()
		self.accept()

class Edit_Label(QDialog):
	def __init__(self,id):
		super().__init__()

		self.id=id
		self.setWindowTitle("标签")
		self.setFixedWidth(200)
		layout=QGridLayout()
		self.setLayout(layout)
		for i in range(5):
			layout.setColumnStretch(i,1)

		layout.addWidget(QLabel("标签名称：",self),0,0,1,2)
		res=cur.execute("SELECT label FROM labels WHERE id=?",(id,)).fetchone() if ~id else ("",)
		self.labelEdit=QLineEdit(res[0],self)
		layout.addWidget(self.labelEdit,0,2,1,3)

		layout.addWidget(QPushButton("确定",self,clicked=self.save),1,0,1,2)
		layout.addWidget(QPushButton("取消",self,clicked=self.reject),1,3,1,2)
		layout.setSpacing(15)
		layout.setContentsMargins(15,15,15,15)

	def save(self):
		label=self.labelEdit.text()
		if ~self.id: cur.execute("UPDATE labels SET label=? WHERE id=?",(label,self.id))
		else: cur.execute("INSERT INTO labels (label) VALUES (?)",(label,))
		con.commit()
		self.accept()

class Sentences(QMainWindow):
	def __init__(self):
		super().__init__()

		self.setWindowTitle("Sentences")
		self.resize(500,500)

		setting=QSettings("Mzxr","Sentences")
		if not setting.value("init"):
			cur.execute("CREATE TABLE quotes (id INTEGER PRIMARY KEY AUTOINCREMENT, quote TEXT, label INTEGER, time TEXT)")
			cur.execute("CREATE TABLE labels (id INTEGER PRIMARY KEY AUTOINCREMENT, label TEXT)")
			cur.execute("INSERT INTO labels (id,label) VALUES (0,'None')")
			con.commit()
			setting.setValue("init",True)

		tab=QTabWidget(self)
		tab.addTab(self.quote(),"摘录")
		tab.addTab(self.search(),"搜索")
		tab.addTab(self.label(),"标签")
		tab.addTab(self.preference(),"设置")

		self.setCentralWidget(tab)
		self.update_show()

	def quote(self):
		widget=QWidget(self)
		layout=QGridLayout()
		widget.setLayout(layout)
		for i in range(5):
			layout.setColumnStretch(i,1)

		self.quoteBtn=QPushButton("添加",self,clicked=lambda _:self.edit_quote(-1))
		layout.addWidget(self.quoteBtn,0,0,1,5)

		self.quoteTable=QTableWidget(self)
		self.quoteTable.setColumnCount(5)
		self.quoteTable.setHorizontalHeaderLabels(["摘录","标签","时间","编辑","删除"])
		width=[268,60,80,50,50]
		for i in range(5):
			self.quoteTable.setColumnWidth(i,width[i])
		layout.addWidget(self.quoteTable,1,0,1,5)

		return widget

	def show_quote(self):
		self.quoteTable.setRowCount(0)
		labels={}
		for i in cur.execute("SELECT * FROM labels").fetchall():
			labels[i[0]]=i[1]
		for k,v in enumerate(cur.execute("SELECT * FROM quotes").fetchall()):
			self.quoteTable.insertRow(k)
			quote=QLabel(v[1].replace("\n"," "),self)
			quote.setContentsMargins(5,0,5,0)
			quote.setToolTip(v[1])
			label=QLabel(labels[v[2]],self)
			label.setToolTip(labels[v[2]])
			time=QLabel(v[3][:10],self)
			time.setToolTip(v[3])
			items=[quote,label,time]
			items.append(QPushButton("编辑",self,clicked=lambda _,id=v[0]:self.edit_quote(id)))
			items.append(QPushButton("删除",self,clicked=lambda _,id=v[0]:self.delete_quote(id)))

			for i in range(5):
				if i in [1,2]: items[i].setAlignment(Qt.AlignmentFlag.AlignCenter)
				self.quoteTable.setCellWidget(k,i,items[i])

	def edit_quote(self,id):
		Edit_Quote(id).exec()
		self.update_show()

	def delete_quote(self,id):
		if not confirm(self,"删除","确定删除？"): return
		cur.execute("DELETE FROM quotes WHERE id=?",(id,))
		con.commit()
		self.update_show()

	def search(self):
		widget=QWidget(self)
		layout=QGridLayout()
		widget.setLayout(layout)
		for i in range(5):
			layout.setColumnStretch(i,1)

		self.searchTxt=QLineEdit(self)
		self.searchBtn=QPushButton("搜索",self,clicked=self.search)
		self.searchTxt.returnPressed.connect(self.searchBtn.click)
		layout.addWidget(self.searchTxt,0,0,1,4)
		layout.addWidget(self.searchBtn,0,4,1,1)

		self.searchTable=QTableWidget(self)
		self.searchTable.setColumnCount(5)
		self.searchTable.setHorizontalHeaderLabels(["摘录","标签","时间","编辑","删除"])
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

		self.labelBtn=QPushButton("添加",self,clicked=lambda _:self.edit_label(-1))
		layout.addWidget(self.labelBtn,0,0,1,5)

		self.labelTable=QTableWidget(self)
		self.labelTable.setColumnCount(4)
		self.labelTable.setHorizontalHeaderLabels(["标签","计数","编辑","删除"])
		width=[200,60,50,50]
		for i in range(4):
			self.labelTable.setColumnWidth(i,width[i])
		layout.addWidget(self.labelTable,1,0,1,5)

		return widget

	def show_label(self):
		self.labelTable.setRowCount(0)
		for k,v in enumerate(cur.execute("SELECT * FROM labels").fetchall()):
			self.labelTable.insertRow(k)
			count=cur.execute("SELECT COUNT(*) FROM quotes WHERE label=?",(v[0],)).fetchone()[0]
			items=[QLabel(v[1],self),QLabel(str(count),self)]
			items.append(QPushButton("编辑",self,clicked=lambda _,id=v[0]:self.edit_label(id)))
			items.append(QPushButton("删除",self,clicked=lambda _,id=v[0]:self.delete_label(id)))

			for i in range(4):
				if i in [0,1]: items[i].setAlignment(Qt.AlignmentFlag.AlignCenter)
				self.labelTable.setCellWidget(k,i,items[i])

	def edit_label(self,id):
		if not id: return QMessageBox.information(self,"提示","禁止编辑默认标签")
		Edit_Label(id).exec()
		self.update_show()

	def delete_label(self,id):
		if not id: return QMessageBox.information(self,"提示","禁止删除默认标签")
		if not confirm(self,"删除","确定删除？"): return
		cur.execute("UPDATE quotes SET label=0 WHERE label=?",(id,))
		cur.execute("DELETE FROM labels WHERE id=?",(id,))
		con.commit()
		self.update_show()

	def update_show(self):
		self.show_quote()
		self.show_label()

	def preference(self):
		widget=QWidget(self)
		layout=QGridLayout()
		widget.setLayout(layout)
		return widget

if __name__=="__main__":
	app=QApplication(sys.argv)
	ex=Sentences()
	ex.show()
	app.exec()
	con.close()
	sys.exit()
