from data import PdfList
pdfList = PdfList()
minute_list=pdfList.importPickle()
for i in range(len(minute_list)):
    for j in range(i+1,len(minute_list)):
        if minute_list[i]==minute_list[j]:
            print("Same Minute!")
