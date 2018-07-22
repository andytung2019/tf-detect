from tkinter import *
import tkinter.messagebox
import csv
import cv2 as cv
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
import argparse
import os

class Rect:
    idx = -1
    x = None
    y = None
    w = None
    h = None

    def str2float(self, s):
        def char2num(s):
            return {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9}[s]
            # 这事实上是一个字典

        index_point = s.find('.')
        if index_point == -1:
            daichu = 1
        else:
            daichu = 0.1 ** (len(s) - 1 - index_point)
            s = s[0:index_point] + s[index_point + 1:]  # 这里是除去小数点
        from functools import reduce
        result1 = reduce(lambda x, y: x * 10 + y, map(char2num, s))
        return result1 * daichu

    def __init__(self, idx, str):
        self.idx = idx
        l = str.split('_')
        # print(l)
        self.x = int(self.str2float(l[0]))
        self.y = int(self.str2float(l[1]))
        self.w = int(self.str2float(l[2]))
        self.h = int(self.str2float(l[3]))

    def draw_me(self, image, c1,c2,c3):
        cv.rectangle(image, (self.x, self.y), (self.x + self.w, self.y + self.h), (c1,c2,c3))

        font = cv.FONT_HERSHEY_SIMPLEX
        cv.putText(image, str(self.idx), (self.x + int(self.w / 2), self.y + int(self.h / 2)), font, 1, (0, 250, 0), 1,
                   cv.LINE_AA)

    def print_me(self):
        print("x,y, w, h: %d, %d, %d, %d" % (self.x, self.y, self.w, self.h))

class App:
	def __init__(self, csv_name,ck_name, img_dir):
		self.csv_name = csv_name,
		self.ck_name = ck_name
		self.img_dir = img_dir
		master = Tk()
		master.title('label me')


		self.label =''
		self.img_list=[]
		self.ck_list=[]
		self.label_list=[]
		self.cur_idx = 0
		self.img_on_canvas = None

		self.frame = Frame(master)
		self.canvas = Canvas(self.frame, width=1100, height = 520)
		self.canvas.pack(side=LEFT)


		self.frame2 = Frame(master)
		self.frame2.pack()
		self.btn_next = Button(
			self.frame2, text="下一个",width=15, height=3, fg="red", command=self.next_pic
		)

		self.btn_prev = Button(
			self.frame2, text="上一个", width=15, height=3, fg="red", command=self.prev_pic
		)

		frame2 = Frame(master)
		frame2.pack()
		self.label_idx = Label(frame2, text="No.")

		self.label_now = StringVar(value='3:1,4:2')
		self.ent_label=Entry(frame2,textvariable=self.label_now,font=('Verdana',18))
		self.btn_submit = Button(
			frame2, text="保存 ", width=15,height=3,fg="red", command=self.submit_label
		)

		self.btn_save = Button(
			frame2, text="导出", width=15,height=3,fg="red", command=self.write_csv
		)

		self.btn_prev.grid(row=1, column=1)
		self.btn_next.grid(row=1, column=2)
		self.label_idx.grid(row=2, column=1)
		self.ent_label.grid(row=2,column=2)
		self.btn_submit.grid(row=3,column=2)
		self.btn_save.grid(row=3,column= 1)
		
		#read csv, load first image
		self.load_csv(csv_name)
		self.load_ck(ck_name)
		#self.load_image(0)

		master.mainloop()

	def put_image(self, master, idx):
		if idx >= len(self.img_list):
			return
		name = os.path.join(self.img_dir ,self.img_list[idx][0])

		img = cv.imread(name)
		b, g, r = cv.split(img)
		img = cv.merge((r, g, b))

		im = Image.fromarray(img)
		tk_im = ImageTk.PhotoImage(image = im)

		self.label_pic = Label(master, image=tk_im)
		self.label_pic.pack()
		#canvas.create_image(1100, 500, tk_im)


	def load_ck(self, path):
		with open(path) as csv_input:
			fields = ['name', 'bbox']
			reader = csv.DictReader(csv_input, fieldnames=fields)
			for row in reader:
				tp_img = (row['name'], row['bbox'])
				self.ck_list.append(tp_img)

	def load_csv(self, path):
		with open(path) as csv_input:
			fields = ['name', 'bbox']
			reader = csv.DictReader(csv_input, fieldnames=fields)
			for row in reader:
				tp_img = (row['name'], row['bbox'])
				self.img_list.append(tp_img)
	def write_csv(self,):
		
		tkinter.messagebox.showinfo('导出将重写out_label.csv')
		path ="out_label.csv"	
		kwargs = { 'newline':''}
		mode = 'w'
		with open(path, mode, **kwargs) as fp:
			writer = csv.writer(fp, delimiter=str(','))
			for item in self.label_list: 
				writer.writerow(item)

		tkinter.messagebox.showinfo('导出成功到:out_label.csv')

	def ios_of_ck(self, f_name):
		for item in self.ck_list:
			if item[0] == f_name:
				return item[1]
		return ''

	def load_image(self, idx):
		
		if idx >= len(self.img_list):
			return
		self.label_idx.configure(text=str(idx))

		item = self.img_list[idx]
		print(os.path.join(self.img_dir,item[0]))
		img = cv.imread(os.path.join(self.img_dir,item[0])
)
		cv.namedWindow("image")
		cv.imshow("image", img)

		strios  = item[1].rstrip(';')
		l_objs = strios.split(';')
		for i in range(len(l_objs)):
			rect = Rect(i, l_objs[i])
			rect.draw_me(img,0, 250,0)

		ios = self.ios_of_ck(item[0])
		ios = ios.rstrip(';')
		l_objs_ck = ios.split(';')
		for i in range(len(l_objs_ck)):
			rect = Rect(i, l_objs_ck[i])
			rect.draw_me(img, 0,0,250)
			
		cv.imshow("image", img)
		cv.waitKey(20)

	def next_pic(self):
		if self.cur_idx >=len(self.img_list)-1:
			tkinter.messagebox.showinfo('没有了')
			return
		self.cur_idx += 1
		self.ent_label.delete(0, 'end')

		self.load_image(self.cur_idx)

	def prev_pic(self):
		if self.cur_idx <= 0:
			tkinter.messagebox.showinfo('到头了')
			return
		self.cur_idx -= 1
		self.ent_label.delete(0, 'end')

		self.load_image(self.cur_idx)

	def submit_label(self):
		
		item = [self.img_list[self.cur_idx][0],self.img_list[self.cur_idx][1], 
				self.ent_label.get()]
		self.label_list.append(item)

def parse_args():
	"""Parse input arguments."""
	parser = argparse.ArgumentParser(description='dhp label show ')
	parser.add_argument('--csv', dest='csv_name', help='.csv file for input images label', default='test.csv')
	parser.add_argument('--ck', dest='ck_name', help='.csv file for check images label', default='test_ck.csv')
	parser.add_argument('--dir', dest='img_dir', help='images dir ', default='images')
	args = parser.parse_args()
	
	return args

if __name__ == '__main__':
	args = parse_args()
	csv_name  = args.csv_name
	ck_name  = args.ck_name
	img_dir  = args.img_dir
	app = App(csv_name, ck_name,img_dir)
