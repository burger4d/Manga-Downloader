from tkinter import *
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import os
import threading

tk = Tk()
tk.resizable(True, True)
screen_width = tk.winfo_screenwidth()*0.9
screen_height = tk.winfo_screenheight()*0.8
w = Canvas(tk, width=screen_width, height=screen_height, bg="#282828")
w.pack()

typeface=round(screen_width*0.0341-27)

mangas=[]
if "mangas.txt" in os.listdir():
    with open("mangas.txt", "r") as file:
        content=file.read()
        content=content.replace("\n", " ")
        mangas=content.split()
        mangas.sort()
        file.close()

mangas.append("not in the list")


def make_request(url, special=False):
    #ssl._create_default_https_context=ssl._create_unverified_context
    try:
        try:
            request=Request(url, headers={"User-Agent": "Mozilla/5.0"})
        except:
            request=Request(url)
        if special:
            content = urlopen(request).read().decode("utf-8")
        else:
            content = urlopen(request).read()
        return content
    except Exception as err:
        print_error(str(err)+"\n"+url)
        raise Exception


def download_file(url, name="test", manga="vanpanchmen"):
    #download the image
    content=make_request(url)
    if content!=None:
        with open(manga+"/"+name+".png", "b+w") as file:
            file.write(content)
            file.close()
    else:
        print(404)


def search_chapter(chapter, name="chernyy-klever-abs3TPx", extension=""):
    #searching one specific chapter
    url="https://mangapoisk.org/manga/"+name+"/chapter/"+str(chapter)+extension
    #print(url)
    content = str(make_request(url))
    return content


def get_pages(page):
    #getting pages from the website
    List = []
    #print(page)
    start = "https://static2.mangapoisk.org/pages"
    soup=BeautifulSoup(page, features="html.parser")
    interest=soup.find_all("img")
    links=[]
    for line in interest:
        l1=line.get("src")
        l2=line.get("data-src")
        if start in l1 and l1 not in links:
            links.append(l1)
        if l2 is not None:
            if start in l2 and l2 not in links:
                links.append(l2)
    return links


def print_text(Text):
    #showing text on gui
    text2 = Text.split()
    Text = ""
    spaces=round(0.006779*screen_width-2.37)
    for i in range(len(text2)):
        Text+=text2[i]
        if (i+1)%spaces==0:
            Text+="\n"
        else:
            Text+=" "
    w.create_text(screen_width/2, screen_height/2, text=Text, fill="#afafaf", font="Times "+str(typeface), tag="text")


def print_error(Text):
	#showing error on the gui
	w.create_text(screen_width/2, screen_height/4, text=Text, fill="red", font="Times "+str(int(typeface/2)), tag="error")


def select():
    #one button
    global enter, btn
    option=variable.get()
    print(option)
    opt.destroy()
    btn.destroy()
    w.itemconfigure("text", state="hidden")
    if option == "not in the list":
        enter=Entry(tk)
        enter.place(y=0)
        print_text("Name of the manga:")
        btn=Button(text="Confirm", command=select2)
        btn.place(y=0, x=screen_width*0.9/2)
    else:
        select_chapter1(option)


def select2():
    #other button
    global opt, btn, variable
    name=str(enter.get())
    btn.destroy()
    enter.destroy()
    w.itemconfigure("text", state="hidden")
    name=name.replace(" ", "+")
    try:
        request=make_request("https://mangapoisk.org/manga/"+name)
    except:
        w.itemconfigure("error", state="hidden")
        request = None
    if request is None:
        request=make_request("https://mangapoisk.org/search?q="+name)
        soup=BeautifulSoup(request, features="html.parser")
        links=soup.find_all("a")
        names = []
        for line in links:
            new_name=line.get("href")
            if "/manga/" in new_name:
                new_name=new_name[new_name.find("/manga/")+7:]
                if not "/" in new_name and new_name not in names:
                    names.append(new_name)
        if len(names)==0:
            print_text("no results")
            raise TypeError
        elif len(names)==1:
            name=names[0]
            name=verify_title(name)
            select_chapter1(name)
        else:
            variable = StringVar()
            variable.set(names[0])
            opt = OptionMenu(tk, variable, *names)
            opt.place(y=0)
            btn=Button(text="Confirm", command=select3)
            btn.place(y=0, x=screen_width*1.7/2)
            print_text("Select the exactly name of the manga")
    else:
        name=verify_title(name)
        select_chapter1(name)


def select3():
    #another button
    btn.destroy()
    name=variable.get()
    opt.destroy()
    w.itemconfigure("text", state="hidden")
    print_text("searching...")
    tk.update()
    select_chapter1(name)


def verify_title(name):
	"""because sometimes there is a difference"""
	req=urlopen(Request("https://mangapoisk.org/manga/"+name, headers={"User-Agent":"Mozilla/5.0"}))
	url=req.geturl()
	name=url[url.find("manga/")+6:]
	return name


def select_chapter1(name):
    global FirstChapter, btn, last_chapter, NAME, chapterList
    NAME = name
    string='<li class="page-item"><a class="page-link"'
    w.itemconfigure("text",state="hidden")
    print_text("loading...")
    tk.update()
    if name not in mangas:
        with open("mangas.txt", "a") as file:
            file.write("\n"+name)
            file.close()
    os.makedirs(name, exist_ok=True)
    #os.makedirs(name+"_pdf", exist_ok=True)
    word="Глава"  # sometimes there is a mistake in the number of chapters, so let's find the last chapter released!
    request=make_request("https://mangapoisk.org/manga/"+NAME, True)
    soup=BeautifulSoup(request, features="html.parser")
    links=soup.find_all("meta")
    request=str(request)
    #print(request)
    chaptersLists = request.count(string)+1
    chapterList=[]
    for i in range(1, chaptersLists+1):
        req=str(make_request("https://mangapoisk.org/manga/"+NAME+"/chaptersList?infinite=1&page="+str(i)))
        while "/manga/"+NAME+"/chapter/" in req:
            req=req[req.find("/manga/"+NAME+"/chapter/"):]
            chap="https://mangapoisk.org"+req[:req.find('" ')]
            chap=chap[::-1]
            chap=chap[:chap.find("-")]+chap[chap.find("/"):]
            chap=chap[::-1]
            #print(chap)
            chapterList.append(chap)
            req=req[req.find("class"):]
    chapterList=chapterList[::-1]
    last_chapter = int(request[request.find(word):].split()[1])
    summary="."
    for line in links:
        if "description" in str(line):
            summary = line.get("content")
            break
    w.itemconfigure("text", state="hidden")
    print_text("CHAPTERS: "+str(last_chapter)+" -  "+summary)
    FirstChapter = Scale(tk, orient="horizontal", from_=1, to=last_chapter, resolution=1, tickinterval=last_chapter/5, length=screen_width, label="First chapter to download")
    FirstChapter.pack()
    btn=Button(text="Confirm", command=select_chapter2)
    btn.place(x=screen_width*0.9/2, y=0)


def select_chapter2():
    global btn, LastChapter, first_chapter
    first_chapter = FirstChapter.get()
    FirstChapter.destroy()
    btn.destroy()
    if first_chapter < last_chapter:
        LastChapter = Scale(tk, orient="horizontal", from_=first_chapter, to=last_chapter, resolution=1, tickinterval=last_chapter/5, length=screen_width, label="Last chapter to download")
        LastChapter.pack()
        btn=Button(text="Confirm", command=download_it)
        btn.place(x=screen_width*0.9/2, y=0)
    else:
    	download_it()


def download_it():
    #downloading procedure
    global last_chapter, chapterList
    btnq.destroy()
    if first_chapter != last_chapter:
        last_chapter = LastChapter.get()
        LastChapter.destroy()
        btn.destroy()
        w.itemconfigure("text", state="hidden")
        print_text("Starting the download")
        tk.update()
    for chapter in range(first_chapter, last_chapter+1):
        if chapter == 1:
            page = search_chapter(str("1-1"), NAME)
        else:
            chap="https://mangapoisk.org/manga/"+NAME+"/chapter/"+str(chapter)
            for i in range(len(chapterList)):
                chapt=chapterList[i]
                if chap in chapt:
                    chaptersList=chapterList[i+1:]
                    break
            if "_" in chapt:
                extension=chapt[chapt.find("_"):]
                #print(extension)
                page=search_chapter(str(chapter), NAME, extension)
            else:
                page = search_chapter(str(chapter), NAME)
        l=get_pages(page)
        threads=[]
        for i in range(len(l)):
            t=threading.Thread(target=download_file, args=(l[i], NAME+"_"+str(chapter)+"_"+str(i), NAME))
            threads.append(t)
            t.start()        
        for i in range(len(l)):
            threads[i].join()
            w.itemconfigure("text", state="hidden")
            print_text("downloading chapter "+str(chapter)+" (on "+str(last_chapter)+"), "+str(i+1)+"pages downloaded on "+str(len(l)))
            tk.update()
    '''
    w.itemconfigure("text", state="hidden")
    print_text("Creating PDF file(s)...")
    tk.update()
    '''
    files = os.listdir(NAME)
    imagelist=[]
    for chapter in range(first_chapter, last_chapter+1):
        start=NAME+"_"+str(chapter)
        for page in range(200):
            #print(NAME+"/"+start+"_"+str(page)+".png")
            if start+"_"+str(page)+".png" not in files:
                """
                with open(NAME+"_pdf/"+start+".pdf","wb") as f:
                    f.write(img2pdf.convert(imagelist))
                    imagelist=[]
                    f.close()
                    w.itemconfigure("text", state="hidden")
                    print_text("PDF chapter "+str(chapter)+" created")
                    tk.update()
                break
            else:
                """
                imagelist.append(NAME+"/"+start+"_"+str(page)+".png")
    w.itemconfigure("text", state="hidden")
    print_text("Task Finished")


if __name__ == "__main__":
    #print(screen_width)
    variable = StringVar()
    variable.set(mangas[-1])
    opt = OptionMenu(tk, variable, *mangas)
    opt.place(y=0)
    btn = Button(tk, text="Confirm", command=select)
    btn.place(x=screen_width*0.9/2, y=0)
    print_text("Choose one manga.")
    btnq=Button(tk, text="quit", command=quit)
    btnq.pack()
    tk.mainloop()
