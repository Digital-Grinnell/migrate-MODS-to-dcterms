
#set global parameters
bookstore = "bookstore_list.csv"
marcxml = "marcxml.xml"
newlist = "newlist.csv"
picklist = "Textbooks_physical_holdings.csv"
physlist = "Textbooks_physical_holdings_with_course_info.csv"
ebook = "Textbooks_electronic_holdings.csv"
ebooklist = "Textbooks_electronic_holdings_with_course_info.csv"
buylist = "Textbooks_to_Purchase.csv"
purchaselist = "Textbooks_to_Purchase_with_course_info.csv"
finalbuylist = "Final_Textbooks_to_Purchase.csv"
dayone = "Day_One_Access_Textbooks.csv"
cleanuplist = "worldcat_failures.csv"
requerylist = "requery_list.csv"

#imports
import csv
import unicodecsv
import requests
import pymarc
import json
import re

def createNewList(fromlist,tolist,mode):
    #open the bookstore list and find the ISBNs in column 3
    with open(fromlist) as file:
      with open(tolist, mode) as z:
        reader = csv.reader(file)
        writer = unicodecsv.writer(z)
        for row in reader:
          if row[0] == 'Dept / Course':
            coursenum = row[2][-7:]
          if row[0] == 'Section':
            section = row[1]
          if len(row[3]) > 7:
            url = "http://www.worldcat.org/webservices/catalog/content/isbn/" + row[3].replace('-','') + "?wskey=2NQNwAJYyRVPrj0bCsnaSQURQsbLCoOmRYNHmwjAG7NtuMabYzw6BxZjU3PZfDNrEiTGKRzkRwjulnCE"
            try:
              r = requests.get(url)
              #print(r.status_code)
              #print(r.text)
            except:
              print("Connection failed.")
              row.extend(["Querying WorldCat failed for this record."])
              writer.writerow(row)
              continue
            record = r.content
            xml = open(marcxml,"wb")
            xml.write(record)
            xml.close()
            from pymarc import parse_xml_to_array
            #try:
            with open(marcxml) as marc:
              marcx = parse_xml_to_array(marc)
              for x in marcx:
                title = x.title()
                #title = unicode(title, "utf-8")
                if x.author():
                  author = x.author()
                  #author = unicode(author, "utf-8")
            #If it's an edited volume -- which a lot of our textbooks
            #are -- then the 100 is empty. But there's usually still
            #something meaningful and useful in the 245c.
                elif x['245']['c']:
                  author = x['245']['c']
                #  author = unicode(author[0],"utf-8")
                else:
                  author = ""
                isbn = x.isbn()
                print(author)
                del row[1:4]           
                row.extend([title, author, isbn, coursenum, section])
                writer.writerow(row)
            #except:
              #row.extend(["WorldCat record invalid."])
            #writer.writerow(row)
#            elif re.match("[0A-Z]{3,4}",row[1]):
#              course = row
#              writer.writerow(course)
#createNewList(bookstore,newlist,'wb+')

def talkToAlma(file,mode):
  with open(file, encoding='utf-8') as infile:
    with open(buylist, mode, encoding='utf-8') as buy_outfile:
      with open(picklist, mode, encoding='utf-8') as phys_outfile:
        with open(ebook, mode, encoding='utf-8') as e_outfile:
         with open(dayone, mode, encoding='utf-8') as dayone_outfile:
          phys_writer = csv.writer(phys_outfile)
          e_writer = csv.writer(e_outfile)
          buy_writer = csv.writer(buy_outfile)
          dayone_writer = csv.writer(dayone_outfile)
          reader = csv.reader(infile)
          for row in reader:
            if len(row[0]) > 3:
                  title = row[1]
                  author = row[2]
            e = 0
            b = 0
            title = re.sub(r'[\+&\|!,\()\{\}\[\]\^"~\*\?:\\\/;]', '', title)
            title = title.rstrip("'").lstrip("'")
            if author:
              author = re.sub(r'[\+&\|!,\.()\{\}\[\]\^"~\*\?:\\;]', '', author)
              author = re.sub(r'[0-9]', '', author)
              author = author.replace("-", " ") # replace with a space rather than nothing
              author = author.replace("author","")
              author = author.rstrip("'").lstrip("'")
              almaurl = "https://api-na.hosted.exlibrisgroup.com/primo/v1/search?vid=01GCL_INST:GCL&q=title,equals,\"" + title + "\",AND;creator,contains," + author + "&tab=books_grinnell&scope=all_books_grinnell&lang=eng&offset=0&limit=10&sort=rank&pcAvailability=true&getMore=0&conVoc=true&apikey=l7xxd2eb671cc50943b5a3318ee3238ed8b8"
            else:
              almaurl = "https://api-na.hosted.exlibrisgroup.com/primo/v1/search?vid=01GCL_INST:GCL&q=title,contains,\"" + title + "\"&tab=books_grinnell&scope=all_books_grinnell&lang=eng&offset=0&limit=10&sort=rank&pcAvailability=true&getMore=0&conVoc=false&apikey=l7xxd2eb671cc50943b5a3318ee3238ed8b8"
            print(almaurl)
            response = requests.get(almaurl)
            if response.status_code == 200:
          #For some reason the Alma query totally fails and returns
          #an error on some entries, including "Master & Margarita 
          #(Russian)." At some point we should probably figure those
          #out and fix them, but for now, this keeps the script 
          #running when it hits one of those.
              k = json.loads(response.text)
              print(k['info']['total'])
              if k['info']['total'] > 0:
                for a in k["docs"]:
                  if a["delivery"]["bestlocation"]:
                    row.extend([a["delivery"]["bestlocation"]["subLocation"].encode('ascii','ignore'),a["delivery"]["bestlocation"]["callNumber"].encode('ascii','ignore'),a["delivery"]["bestlocation"]["availabilityStatus"]])
                    phys_writer.writerow(row)
                    if row[0][0:6] == "DAY-ONE":
                      dayone_writer.writerow(row)
#                   del row[5:8]
                    del row[6:9]
                  if a["delivery"]["deliveryCategory"][0] == "Alma-E" and e == 0:
                    row.extend(["https://grinnell.primo.exlibrisgroup.com/discovery/fulldisplay?docid=alma" + a["pnx"]["display"]["mms"][0] + "&context=L&vid=01GCL_INST:GCL&search_scope=all_books_grinnell&tab=books_grinnell&lang=en"])
                    e_writer.writerow(row)
                    if row[0][0:6] == "DAY-ONE":
                      dayone_writer.writerow(row)
#                   del row[5]
                    del row[6]
                    e = 1
              elif b==0:
                  buy_writer.writerow(row)
                  if row[0][0:6] == "DAY-ONE":
                    dayone_writer.writerow(row)
                  b = 1
              else:
                pass
talkToAlma(newlist,'w+')

# Take the spreadsheet from the previous step and add course numbers
# for the courses each book is going on reserve for.
def addCourseInfo(inlist,outlist):
    with open(newlist) as infile_1: 
        with open(inlist) as infile_2:
            with open(outlist, 'wb+') as outfile:
                writer = unicodecsv.writer(outfile)
                reader_1 = unicodecsv.reader(infile_1)
                reader_2 = unicodecsv.reader(infile_2)
                for row_2 in reader_2:
                    match = 'no match'
                    infile_1.seek(0)
                    for row_1 in reader_1:
                        if row_1[0] == row_2[0]:
                          match = 'match'
              #  continue
                        elif match == 'match' and re.match("[0A-Z]{4}$",row_1[1]):
                            row_2.extend([row_1[2]+ '-' + row_1[4]])
                        elif match == 'match' and row_1[1][:3] == "TUT":
                            row_2.extend([row_1[1] + '-' + row_1[2] + ' ' + row_1[4]])
                        elif match == 'match':
                            writer.writerow(row_2)
                            match = 'no match'
                            break

#Because all of the WorldCat fails wind up in the buylist
def cleanup():
  with open(buylist) as infile:
    with open(finalbuylist,'wb+') as buy:
      with open(cleanuplist, 'wb+') as requery:
        reader = unicodecsv.reader(infile)
        cleanup_writer = unicodecsv.writer(requery)
        okay_writer = unicodecsv.writer(buy)
        for row in reader:
         if len(row) > 5 and row[5] == "Querying WorldCat failed for this record.":
           cleanup_writer.writerow(row)
         else:
           okay_writer.writerow(row)
 
#cleanup()
#createNewList(cleanuplist,requerylist,'wb+')
#talkToAlma(requerylist,'ab')
#addCourseInfo(picklist, physlist)
#addCourseInfo(ebook, ebooklist)
#addCourseInfo(finalbuylist, purchaselist)

