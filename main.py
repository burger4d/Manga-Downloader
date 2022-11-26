from tkinter import *
from urllib.request import urlopen, Request
from fake_user_agent import user_agent
from bs4 import BeautifulSoup
import os

tk = Tk()
tk.resizable(True, True)
screen_width = tk.winfo_screenwidth()*1
screen_height = tk.winfo_screenheight()*0.7
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
    try:
        try:
            request=Request(url, headers={"User-Agent": user_agent()})
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
    content=make_request(url)
    if content!=None:
        with open(manga+"/"+name+".png", "b+w") as file:
            file.write(content)

            file.close()
    else:
        print(404)


def search_chapter(chapter, name="chernyy-klever-abs3TPx"):
    url="https://mangapoisk.ru/manga/"+name+"/chapter/"+str(chapter)
    content = str(make_request(url))
    return content


def get_pages(page):
    List = []
    start = "https://static2.mangapoisk.ru/pages"
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
	w.create_text(screen_width/2, screen_height/4, text=Text, fill="red", font="Times "+str(int(typeface/2)), tag="error")


def select():
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
    global opt, btn, variable
    name=str(enter.get())
    btn.destroy()
    enter.destroy()
    w.itemconfigure("text", state="hidden")
    name=name.replace(" ", "+")
    try:
        request=make_request("https://mangapoisk.ru/manga/"+name)
    except:
        w.itemconfigure("error", state="hidden")
        request = None
    if request is None:
        request=make_request("https://mangapoisk.ru/search?q="+name)
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
    btn.destroy()
    name=variable.get()
    opt.destroy()
    w.itemconfigure("text", state="hidden")
    print_text("searching...")
    tk.update()
    select_chapter1(name)


def verify_title(name):
	"""because sometimes there is a difference"""
	req=urlopen(Request("https://mangapoisk.ru/manga/"+name, headers={"User-Agent":"Mozilla/5.0"}))
	url=req.geturl()
	name=url[url.find("manga/")+6:]
	return name


def select_chapter1(name):
    global FirstChapter, btn, last_chapter, NAME
    NAME = name
    w.itemconfigure("text", state="hidden")
    if name not in mangas:
        with open("mangas.txt", "a") as file:
            file.write("\n"+name)
            file.close()
    os.makedirs(name, exist_ok=True)
    word="Глава"  # sometimes there is a mistake in the number of chapters, so let's find the last chapter released!
    request=make_request("https://mangapoisk.ru/manga/"+NAME, True)
    soup=BeautifulSoup(request, features="html.parser")
    links=soup.find_all("meta")
    request=str(request)
    last_chapter = int(request[request.find(word):].split()[1])
    for line in links:
        if "description" in str(line):
            summary = line.get("content")
            break
    print_text("CHAPTERS: "+str(last_chapter)+" -  "+summary)
    FirstChapter = Scale(tk, orient="horizontal", from_=1, to=last_chapter, resolution=1, tickinterval=last_chapter/5, length=screen_width, label="First chapter to download")
    FirstChapter.pack()
    btn=Button(text="Confirm", command=select_chapter2)
    btn.pack()


def select_chapter2():
    global btn, LastChapter, first_chapter
    first_chapter = FirstChapter.get()
    FirstChapter.destroy()
    btn.destroy()
    if first_chapter < last_chapter:
        LastChapter = Scale(tk, orient="horizontal", from_=first_chapter, to=last_chapter, resolution=1, tickinterval=last_chapter/5, length=screen_width, label="Last chapter to download")
        LastChapter.pack()
        btn=Button(text="Confirm", command=download_it)
        btn.pack()
    else:
    	download_it()


def download_it():
    global last_chapter
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
            page = search_chapter(str(chapter), NAME)
        l=get_pages(page)
        for i in range(len(l)):
            download_file(l[i], NAME+"_"+str(chapter)+"_"+str(i), NAME)
            w.itemconfigure("text", state="hidden")
            print_text("downloading chapter "+str(chapter)+" (on "+str(last_chapter)+"), page "+str(i+1)+" on "+str(len(l)))
            tk.update()
    w.itemconfigure("text", state="hidden")
    print_text("Task Finished")


if __name__ == "__main__":
    print(screen_width)
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

