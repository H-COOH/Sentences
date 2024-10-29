import datetime
import os
import sqlite3
import sys

from PyQt6.QtCore import QDateTime,QSettings,Qt
from PyQt6.QtWidgets import QApplication,QButtonGroup,QCheckBox,QDateTimeEdit,QDialog,QFileDialog,QGridLayout,QHBoxLayout,QLabel,QLineEdit,QMainWindow,QMessageBox,QPlainTextEdit,QPushButton,QRadioButton,QTabWidget,QTableWidget,QWidget

con,cur=None,None
label_id=[]

def confirm(parent,title,text):
	res=QMessageBox.question(parent,title,text,QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)
	return res==QMessageBox.StandardButton.Yes

class View_Quote(QDialog):
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
		res=cur.execute("SELECT quote FROM quotes WHERE id=?",(id,)).fetchone()
		quoteEdit=QPlainTextEdit(res[0],self)
		quoteEdit.setReadOnly(True)
		layout.addWidget(quoteEdit,1,0,1,5)

		layout.addWidget(QPushButton("关闭",self,clicked=self.accept),2,0,1,5)
		layout.setSpacing(15)
		layout.setContentsMargins(15,15,15,15)

class Sel_Label(QDialog):
	def __init__(self,type):
		super().__init__()

		self.setWindowTitle("选择标签")
		self.setFixedWidth(215)
		layout=QGridLayout()
		self.setLayout(layout)
		for i in range(5):
			layout.setColumnStretch(i,1)

		self.btnGroup=QButtonGroup(self)
		self.btnGroup.setExclusive(not type)

		self.labelTable=QTableWidget(self)
		self.labelTable.setColumnCount(2)
		self.labelTable.setHorizontalHeaderLabels(["标签","选择"])
		width=[100,50]
		for i in range(2):
			self.labelTable.setColumnWidth(i,width[i])
		layout.addWidget(self.labelTable,0,0,1,5)

		if type:
			layout.addWidget(QPushButton("全选",self,clicked=lambda _:self.sel_all(True)),1,0,1,2)
			layout.addWidget(QPushButton("全不选",self,clicked=lambda _:self.sel_all(False)),1,3,1,2)
		save=QPushButton("确定",self,clicked=self.save)
		save.setDefault(True)
		layout.addWidget(save,type+1,0,1,2)
		layout.addWidget(QPushButton("取消",self,clicked=self.reject),type+1,3,1,2)
		layout.setSpacing(15)
		layout.setContentsMargins(15,15,15,15)

		labels=cur.execute("SELECT * FROM labels").fetchall()
		for k,v in enumerate(labels):
			self.labelTable.insertRow(k)
			label=QLabel(v[1],self)
			self.labelTable.setCellWidget(k,0,label)
			label.setAlignment(Qt.AlignmentFlag.AlignCenter)

			widget=QWidget(self)
			layout=QHBoxLayout()
			widget.setLayout(layout)
			layout.setContentsMargins(0,0,0,0)
			layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
			btn=QCheckBox(self) if type else QRadioButton(self)
			if v[0] in label_id: btn.setChecked(True)
			self.btnGroup.addButton(btn,v[0])
			layout.addWidget(btn)
			self.labelTable.setCellWidget(k,1,widget)

	def sel_all(self,type):
		for i in range(self.labelTable.rowCount()):
			self.btnGroup.button(i).setChecked(type)

	def save(self):
		global label_id
		label_id=[]
		labels=cur.execute("SELECT id FROM labels").fetchall()
		for i in labels:
			if self.btnGroup.button(i[0]).isChecked():
				label_id.append(i[0])
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

		save=QPushButton("确定",self,clicked=self.save)
		save.setDefault(True)
		layout.addWidget(save,3,0,1,2)
		layout.addWidget(QPushButton("取消",self,clicked=self.reject),3,3,1,2)
		layout.setSpacing(15)
		layout.setContentsMargins(15,15,15,15)

	def set_name(self):
		name=cur.execute("SELECT label FROM labels WHERE id=?",(self.label,)).fetchone()
		self.name.setText(name[0])

	def sel_label(self):
		global label_id
		label_id=[self.label]
		Sel_Label(False).exec()
		self.label=label_id[0]
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

		save=QPushButton("确定",self,clicked=self.save)
		layout.addWidget(save,1,0,1,2)
		layout.addWidget(QPushButton("取消",self,clicked=self.reject),1,3,1,2)
		layout.setSpacing(15)
		layout.setContentsMargins(15,15,15,15)

	def save(self):
		label=self.labelEdit.text()
		if ~self.id: cur.execute("UPDATE labels SET label=? WHERE id=?",(label,self.id))
		else: cur.execute("INSERT INTO labels (label) VALUES (?)",(label,))
		con.commit()
		self.accept()

class Search(QDialog):
	def __init__(self):
		super().__init__()

		self.setWindowTitle("搜索")
		self.resize(560,500)

		layout=QGridLayout()
		self.setLayout(layout)
		for i in range(8):
			layout.setColumnStretch(i,1)

		self.label=[i[0] for i in cur.execute("SELECT id FROM labels").fetchall()]
		layout.addWidget(QPushButton("选择标签",self,clicked=self.sel_label),0,6,1,2)
		fromLabel=QLabel("起始时间：",self)
		self.fromTime=QDateTimeEdit(self,calendarPopup=True,dateTime=QDateTime(2000,1,1,0,0))
		tillLabel=QLabel("结束时间：",self)
		self.tillTime=QDateTimeEdit(self,calendarPopup=True,dateTime=QDateTime.currentDateTime())
		fromLabel.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
		tillLabel.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
		layout.addWidget(fromLabel,1,0,1,1)
		layout.addWidget(self.fromTime,1,1,1,2)
		layout.addWidget(tillLabel,1,3,1,1)
		layout.addWidget(self.tillTime,1,4,1,2)

		self.searchTxt=QLineEdit(self,placeholderText="搜索内容")
		searchBtn=QPushButton("搜索",self,clicked=self.show_search)
		searchBtn.setDefault(True)
		self.searchTxt.returnPressed.connect(searchBtn.click)
		layout.addWidget(self.searchTxt,0,0,1,6)
		layout.addWidget(searchBtn,1,6,1,2)

		self.searchTable=QTableWidget(self)
		self.searchTable.setColumnCount(6)
		self.searchTable.setHorizontalHeaderLabels(["摘录","标签","时间","查看","编辑","删除"])
		width=[272,60,80,50,50,50]
		for i in range(6):
			self.searchTable.setColumnWidth(i,width[i])
		layout.addWidget(self.searchTable,2,0,1,8)
		layout.setContentsMargins(15,15,15,15)

	def sel_label(self):
		global label_id
		label_id=self.label
		Sel_Label(True).exec()
		self.label=label_id

	def show_search(self):
		self.searchTable.setRowCount(0)
		labels={}
		for i in cur.execute("SELECT * FROM labels").fetchall():
			labels[i[0]]=i[1]
		fromTime=self.fromTime.dateTime().toPyDateTime()
		tillTime=self.tillTime.dateTime().toPyDateTime()
		res=cur.execute("SELECT * FROM quotes ORDER BY time DESC").fetchall()
		for k,v in enumerate(res):
			if self.searchTxt.text() not in v[1]: continue
			if v[2] not in self.label: continue
			if not fromTime<=datetime.datetime.fromisoformat(v[3])<=tillTime: continue
			self.searchTable.insertRow(k)
			quote=QLabel(v[1].replace("\n"," "),self)
			quote.setContentsMargins(5,0,5,0)
			quote.setToolTip(v[1])
			label=QLabel(labels[v[2]],self)
			label.setToolTip(labels[v[2]])
			time=QLabel(v[3][:10],self)
			time.setToolTip(v[3])
			view_btn=QPushButton("查看",self,clicked=lambda _,id=v[0]:self.view_quote(id))
			edit_btn=QPushButton("编辑",self,clicked=lambda _,id=v[0]:self.edit_quote(id))
			delete_btn=QPushButton("删除",self,clicked=lambda _,id=v[0]:self.delete_quote(id))
			edit=QSettings("Mzxr","Sentences").value("edit")=="True"
			if edit:
				edit_btn.setEnabled(False)
				delete_btn.setEnabled(False)
			items=[quote,label,time,view_btn,edit_btn,delete_btn]

			for i in range(6):
				if i in [1,2]: items[i].setAlignment(Qt.AlignmentFlag.AlignCenter)
				self.searchTable.setCellWidget(k,i,items[i])

	def view_quote(self,id):
		View_Quote(id).exec()

	def edit_quote(self,id):
		Edit_Quote(id).exec()
		self.show_search()

	def delete_quote(self,id):
		if not confirm(self,"删除","确定删除？"): return
		cur.execute("DELETE FROM quotes WHERE id=?",(id,))
		con.commit()
		self.show_search()

class Sentences(QMainWindow):
	def __init__(self):
		super().__init__()

		self.setWindowTitle("Sentences")
		self.resize(500,500)

		setting=QSettings("Mzxr","Sentences")
		global con,cur
		if not setting.value("path"):
			QMessageBox.information(self,"提示","请选择数据的储存位置")
			path=str(QFileDialog.getExistingDirectory(self,"选择数据位置"))
			if not path: sys.exit()
			con=sqlite3.connect(path+"/sentences.db")
			cur=con.cursor()
			cur.execute("CREATE TABLE quotes (id INTEGER PRIMARY KEY AUTOINCREMENT, quote TEXT, label INTEGER, time TEXT)")
			cur.execute("CREATE TABLE labels (id INTEGER PRIMARY KEY AUTOINCREMENT, label TEXT)")
			cur.execute("INSERT INTO labels (id,label) VALUES (0,'None')")
			con.commit()
			setting.setValue("path",path)
		else:
			con=sqlite3.connect(setting.value("path")+"/sentences.db")
			cur=con.cursor()

		tab=QTabWidget(self)
		tab.addTab(self.quote(),"摘录")
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

		layout.addWidget(QPushButton("添加",self,clicked=lambda _:self.edit_quote(-1)),0,0,1,5)
		self.quoteTable=QTableWidget(self)
		self.quoteTable.setColumnCount(6)
		self.quoteTable.setHorizontalHeaderLabels(["摘录","标签","时间","查看","编辑","删除"])
		width=[268,60,80,50,50,50]
		for i in range(6):
			self.quoteTable.setColumnWidth(i,width[i])
		layout.addWidget(self.quoteTable,1,0,1,5)

		return widget

	def show_quote(self):
		self.quoteTable.setRowCount(0)
		labels={}
		for i in cur.execute("SELECT * FROM labels").fetchall():
			labels[i[0]]=i[1]
		for k,v in enumerate(cur.execute("SELECT * FROM quotes ORDER BY time DESC").fetchall()):
			self.quoteTable.insertRow(k)
			quote=QLabel(v[1].replace("\n"," "),self)
			quote.setContentsMargins(5,0,5,0)
			quote.setToolTip(v[1])
			label=QLabel(labels[v[2]],self)
			label.setToolTip(labels[v[2]])
			time=QLabel(v[3][:10],self)
			time.setToolTip(v[3])
			view_btn=QPushButton("查看",self,clicked=lambda _,id=v[0]:self.view_quote(id))
			edit_btn=QPushButton("编辑",self,clicked=lambda _,id=v[0]:self.edit_quote(id))
			delete_btn=QPushButton("删除",self,clicked=lambda _,id=v[0]:self.delete_quote(id))
			edit=QSettings("Mzxr","Sentences").value("edit")=="True"
			if edit:
				edit_btn.setEnabled(False)
				delete_btn.setEnabled(False)
			items=[quote,label,time,view_btn,edit_btn,delete_btn]

			for i in range(6):
				if i in [1,2]: items[i].setAlignment(Qt.AlignmentFlag.AlignCenter)
				self.quoteTable.setCellWidget(k,i,items[i])

	def view_quote(self,id):
		View_Quote(id).exec()

	def edit_quote(self,id):
		Edit_Quote(id).exec()
		self.update_show()

	def delete_quote(self,id):
		if not confirm(self,"删除","确定删除？"): return
		cur.execute("DELETE FROM quotes WHERE id=?",(id,))
		con.commit()
		self.update_show()

	def label(self):
		widget=QWidget(self)
		layout=QGridLayout()
		widget.setLayout(layout)
		for i in range(5):
			layout.setColumnStretch(i,1)

		layout.addWidget(QPushButton("添加",self,clicked=lambda _:self.edit_label(-1)),0,0,1,5)
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
			edit=QSettings("Mzxr","Sentences").value("edit")=="True"
			edit_btn=QPushButton("编辑",self,clicked=lambda _,id=v[0]:self.edit_label(id))
			delete_btn=QPushButton("删除",self,clicked=lambda _,id=v[0]:self.delete_label(id))
			if edit:
				edit_btn.setEnabled(False)
				delete_btn.setEnabled(False)
			items=items+[edit_btn,delete_btn]

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
		for i in range(6):
			layout.setColumnStretch(i,1)

		layout.addWidget(QLabel("搜索摘录：",self),0,1,1,1)
		layout.addWidget(QPushButton("搜索",self,clicked=lambda _:self.search()),0,2,1,2)
		layout.addWidget(QLabel("数据位置：",self),1,1,1,1)
		layout.addWidget(QPushButton("移动",self,clicked=lambda _:self.set_path()),1,2,1,2)
		layout.addWidget(QLabel("编辑状态：",self),2,1,1,1)
		self.editBtn=QPushButton("",self,clicked=lambda _:self.set_edit())
		layout.addWidget(self.editBtn,2,2,1,2)
		layout.setAlignment(Qt.AlignmentFlag.AlignTop)
		self.show_preference()

		return widget

	def show_preference(self):
		edit=QSettings("Mzxr","Sentences").value("edit")=="True"
		text="禁止" if edit else "允许"
		self.editBtn.setText(text)

	def search(self):
		Search().exec()
		self.update_show()

	def set_path(self):
		path1=QSettings("Mzxr","Sentences").value("path")
		path2=str(QFileDialog.getExistingDirectory(self,"选择数据位置"))
		if not path2 or path1==path2: return
		global con,cur
		con.close()
		try: os.rename(path1+"/sentences.db",path2+"/sentences.db")
		except: return QMessageBox.critical(self,"错误","数据移动失败")
		QSettings("Mzxr","Sentences").setValue("path",path2)
		con=sqlite3.connect(path2+"/sentences.db")
		cur=con.cursor()

	def set_edit(self):
		edit=QSettings("Mzxr","Sentences").value("edit")=="True"
		text="允许" if edit else "禁止"
		if not confirm(self,text+"编辑","是否"+text+"编辑？"): return
		QSettings("Mzxr","Sentences").setValue("edit",str(not edit))
		self.update_show()
		self.show_preference()

if __name__=="__main__":
	app=QApplication(sys.argv)
	ex=Sentences()
	ex.show()
	app.exec()
	sys.exit()
