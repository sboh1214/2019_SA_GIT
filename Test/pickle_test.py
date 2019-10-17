from data import PdfList

pdfList = PdfList()

minute_list= pdfList.importPickle()
print(len(minute_list))
for minute in minute_list:
    print(len(minute))
    
