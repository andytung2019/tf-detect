
from xml.etree.ElementTree import Element, SubElement, tostring
from lxml.etree import Element, SubElement, tostring
import pprint
from xml.dom.minidom import parseString
import csv



class CreateXML(object):
    def __init__(self, f_name,data_name,folder_name):
        self.list_img  = []
        self.list_xml = []
        self._csv_name = f_name
        self._dataset_name = data_name
        self._folder = folder_name
        self._width ='1069'
        self._height = '500'

    def load_csv(self):
        with open(self._csv_name) as csv_input:
            fields = ['idx','name', 'out']
            reader = csv.DictReader(csv_input, fieldnames=fields)
            for row in reader:
                tp_img = (row['idx'], row['name'], row['out'])
                self.list_img.append(tp_img)

    def out_xml(self):
        for idx in range(len(self.list_img)):
            str = self.create_xml(idx)
            self.list_xml.append(str)
        for idx in range(len(self.list_xml)):
            print (self.list_xml[idx])

            f_name = self.list_img[idx][0].rstrip('.jpg')
            f_name = f_name +'.xml'
            with open('Annotations/'+f_name, 'wb') as f:
                f.write(self.list_xml[idx])



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

    def load_bbox(self, img_idx):

        l_bbox = []
        img = self.list_img[img_idx]
        l_objs = img[2].rstrip(';').split(';')
        for i in range(len(l_objs)):
            l = l_objs[i].split('_')
            # print(l)
            x = int(self.str2float(l[0]))
            y = int(self.str2float(l[1]))
            w = int(self.str2float(l[2]))
            h = int(self.str2float(l[3]))
            bbox =(x,y, x+w,y+h)
            l_bbox.append(bbox)

        return l_bbox

    def create_xml(self,file_index):
        node_root = Element('annotation')
        node_folder = SubElement(node_root,'folder')
        node_folder.text = self._folder


        node_filename = SubElement(node_root, 'filename')
        node_filename.text = self.list_img[file_index][0]

        node_size = SubElement(node_root, 'size')
        node_width = SubElement(node_size, 'width')
        node_width.text = self._width
        node_height = SubElement(node_size, 'height')
        node_height.text = self._height
        node_depth = SubElement(node_size, 'depth')
        node_depth.text = '3'


        #create bbox
        l_bbox = self.load_bbox(file_index)
        for coord in l_bbox:

            node_object = SubElement(node_root, 'object')
            node_name = SubElement(node_object, 'name')
            node_name.text = 'car'

            node_pose = SubElement(node_object, 'pose')
            node_pose.text = 'Unspecified'


            node_trunc = SubElement(node_object, 'truncated')
            node_trunc.text = '0'
            if 0 in coord:
                node_trunc.text = '1'
            if coord[2] == 1069 or coord[3] == 500:
                node_trunc.text = '1'

            node_difficult = SubElement(node_object, 'difficult')
            node_difficult.text = '0'

            node_bndbox = SubElement(node_object, 'bndbox')
            node_xmin = SubElement(node_bndbox, 'xmin')
            node_xmin.text = '{}'.format(coord[0])
            node_ymin = SubElement(node_bndbox, 'ymin')
            node_ymin.text = '{}'.format(coord[1])
            node_xmax = SubElement(node_bndbox, 'xmax')
            node_xmax.text = '{}'.format(coord[2])
            node_ymax = SubElement(node_bndbox, 'ymax')
            node_ymax.text = '{}'.format(coord[3])

        str_xml = tostring(node_root, pretty_print=False)
        print (str_xml)
        return str_xml
cxml = CreateXML('test.csv', 'carcar_voc_2018', 'carcar2018')
cxml.load_csv()
cxml.out_xml()
