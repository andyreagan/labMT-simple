# coding: utf-8
import xml.etree.ElementTree as etree
tree = etree.parse('en-sentiment.xml')
root = tree.getroot()
print(root)
# for child in root:
#     print(child)
#     print(child.tag)
#     print(child.form)
#     print(child.attrib['form'])
    
my_dict = {}
for child in root:
    my_dict[child.attrib['form']] = dict()
    
print(len(my_dict))
print(root[0].attrib)
for i,child in enumerate(root):
    my_dict[child.attrib['form']] = (i,float(child.attrib['polarity']))
    
print(len(my_dict))
my_dict['13th']
pos_words = [word for word in my_dict if my_dict[word][1] > 0]
print(len(pos_words))
neg_words = [word for word in my_dict if my_dict[word][1] < 0]
print(len(neg_words))
