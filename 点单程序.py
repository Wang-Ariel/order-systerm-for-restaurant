menu=open("吉野家菜单.txt","r")
menu=menu.read()
html=open("./templates/getOrder.html","r",encoding="utf-8")
html=html.read()  # 获得网页整体样式
html=html[:html.index("""    <div style="top:100px;text-align: center">""")].replace("{{searchResult}}","")+"</body>"
foodList=menu[menu.find("单点主食")+5:menu.find("单点小食")-2].split("\n")  # 建立单点主食的list
priceDict={}
for food in foodList:
    foodName=food.split(" ")[0]  # 单点主食的名称
    foodList[foodList.index(food)]=foodName
    foodPrice=float(food.split(" ")[1])  # 单点主食的价格
    priceDict[foodName]=foodPrice  # 将菜品名称与菜品价格加入词典中对应起来

snackList=menu[menu.find("单点小食")+5:menu.find("单点饮品")-2].split("\n")   # 建立单点饮品的list
for snack in snackList:
    snackName=snack.split(" ")[0]
    snackList[snackList.index(snack)] = snackName
    snackPrice=float(snack.split(" ")[1])
    priceDict[snackName]=snackPrice

drinkList=menu[menu.find("单点饮品")+5:menu.find("套餐/组合")-2].split("\n")  # 建立套餐中可选饮品的list
for drink in drinkList:
    drinkName=drink.split(" ")[0]
    drinkList[drinkList.index(drink)] = drinkName
    drinkPrice=float(drink.split(" ")[1])
    priceDict[drinkName]=drinkPrice

snackInSetList=menu[menu.find("套餐中可选小食")+8:menu.find("套餐中可选饮品")-2].split("\n")  # 建立套餐中可选小食的list
snackInSetDict={}
allSnack=[]  # 记录所有可选小食的名称
for snack in snackInSetList:
    snack=snack.split(" ")
    snackName=snack[0]
    allSnack.append(snackName)
    snackPrice=float(snack[1])
    snackInSetDict[snackName]=snackPrice

drinkInSetList=menu[menu.find("套餐中可选饮品")+8:].split("\n")  # 建立套餐中可选饮品的list
drinkInSetDict={}
allDrink=[]  # 记录所有可选饮品的名称
for drink in drinkInSetList:
    drink=drink.split(" ")
    drinkName=drink[0]
    allDrink.append(drinkName)
    drinkPrice=float(drink[1])
    drinkInSetDict[drinkName]=drinkPrice

setMealList=menu[menu.find("套餐/组合")+6:menu.find("套餐中可选小食")-2].split("\n")  # 建立套餐的list
setMealDict={}
selectableSetList=[]
for setMeal in setMealList:
    setMealName=setMeal.split("：")[0]  # 套餐的名称
    setMealList[setMealList.index(setMeal)]=setMealName
    setFood=str(setMeal.split("：")[1]).split(" ")[:-1]  # 套餐中包含的单品
    setMealPrice=float(str(setMeal).split(" ")[-1])  # 套餐的价格
    priceDict[setMealName]=setMealPrice
    setMealDict[(setMealName,setMealPrice)]=setFood
    if "可选小食" in setFood:
        if "（" in setMealName:
            selectableSetList.append(setMealName)
        else:
            selectableSetList.append(setMealName[:setMealName.index("饭")-1])


allMenu=foodList+snackList+drinkList+setMealList  # 建立包含所有单品与套餐的list，即菜单中所有可点菜品
transDict={"主食":foodList,"小食":snackList,"饮品":drinkList,"套餐组合":setMealList}
selectableSnack = str(allSnack[:-1])[1:-1].replace(",", "/").replace("'", "")
selectableDrink = str(allDrink[:-1])[1:-1].replace(",", "/").replace("'", "")


def recommendSet(orderList):  # 向客人推荐菜品，使其凑成菜单
    recommendList = []
    recommend = ""
    orderList=makeSetGetPrice(orderList)[0]
    tmpList=orderList[:]
    for order in tmpList:
        if order in allSnack:
            tmpList[tmpList.index(order)]="可选小食"
        elif order in allDrink:
            tmpList[tmpList.index(order)]="可选饮品"
    for allSetMeal in setMealDict.items():
        counter=0
        for food in allSetMeal[1]:  # allSetMeal[1]：套餐中包含的菜品
            if food in tmpList:
                counter+=1
        if counter>=len(allSetMeal[1])/3*2:  # 与优惠套餐相近的计算方式，按符合
            recommendList.append(allSetMeal[0][0])  # 可能的推荐套餐

    label = "点单中无饭"
    for order in orderList:
        if order in selectableSetList:
            label = "点单中有饭"
            break

    if label=="点单中无饭":  # 如一位客人只点了小食和饮品，没有点可凑成套餐的米饭，则不向其推荐米饭套餐
        for recommend in recommendList:
            if "可选小食" in setMealDict[(recommend,priceDict[recommend])]:
                recommendList.remove(recommend)

    if recommendList!=[]:
        recommendList.sort(key=lambda x:abs(priceDict[x]-makeSetGetPrice(orderList)[1]))
        # 排序后，recommendList中的第一个套餐为可凑成的最便宜的套餐
        recommendMenu=setMealDict[(recommendList[0],priceDict[recommendList[0]])]  # 推荐的优惠套餐中包含的单品
        recommendFood=str(set(recommendMenu)-set(tmpList))
        if "可选小食" not in recommendMenu:
            extraPrice=priceDict[recommendList[0]]+-makeSetGetPrice(orderList)[1]  # 为了凑成套餐需要额外加的钱
            for food in orderList not in recommendMenu:
                extraPrice+=priceDict[food]
        else:
            if "可选小食" not in tmpList:
                tmpList=orderList[:]
                tmpList.append("黄瓜")
            # 假定加入可凑成套餐的最便宜的小食，以凑成套餐后的价格减去当前价格得到需额外加的价格，下面饮品同理
            elif "可选饮品" not in tmpList:
                tmpList=orderList[:]
                tmpList.append("可乐")
            extraPrice=makeSetGetPrice(tmpList)[1]-makeSetGetPrice(orderList)[1]
        recommend="""<p style="text-align:center;color:#8e4820">只需加"""+str(extraPrice)+"元（起）可凑成优惠套餐"+"“"\
                  +str(recommendList[0])+"”，套餐中还包括："+recommendFood.replace("{'可选小食'}", selectableSnack)\
                      .replace("{'可选饮品'}",selectableDrink)+"</p>"
    return recommend


def makeSetGetPrice(orderList):  # 将单品凑成套餐，并计算总价
    tmpList=orderList[:]
    tmpSnackList=[]
    tmpDrinkList=[]
    counter=0
    extraPrice = 0  # 计算套餐中可选小食及可选饮料带来的额外加价

    for order in tmpList:
        if order in allSnack:
            tmpList[tmpList.index(order)]="可选小食"
            tmpSnackList.append(order)
        elif order in allDrink:
            tmpList[tmpList.index(order)]="可选饮品"
            tmpDrinkList.append(order)
        elif "饭" in order:
            counter+=1

    if "可选小食" and "可选饮品" in tmpList and counter != 0:  # 凑成包含可选小食和可选饮品的套餐
        counter=0
        for allSetMeal in setMealDict.items():
            while True:
                if set(allSetMeal[1]) & set(tmpList)==set(allSetMeal[1]):  # 将所点菜品与套餐中的菜品进行比对
                    for food in allSetMeal[1]:
                        tmpList.remove(food)
                        if "可选" not in food:
                            orderList.remove(food)
                    orderList.append(allSetMeal[0][0])
                    counter += 1  # 记录凑成的套餐数
                else:
                    break

        tmpSnackList.sort(key=lambda x:snackInSetDict[x],reverse=True)  # 将价格最高的小食饮品算入套餐中
        tmpSnackList=tmpSnackList[:counter]
        tmpDrinkList.sort(key=lambda x:drinkInSetDict[x],reverse=True)
        tmpDrinkList=tmpDrinkList[:counter]

        for snack in tmpSnackList:
            orderList.remove(snack)  # 可选小食已经被计入了套餐中，因此将其从点单列表中删除。下面对可选饮品进行同样的操作
            extraPrice+=snackInSetDict[snack]
        for drink in tmpDrinkList:
            orderList.remove(drink)
            extraPrice+=drinkInSetDict[drink]

    else:
        for allSetMeal in setMealDict.items():  # 凑成不包含可选小食和可选饮品的套餐
            while True:
                if set(allSetMeal[1]) & set(orderList) == set(allSetMeal[1]):  # 将所点菜品与套餐中的菜品进行比对
                    for food in allSetMeal[1]:
                        orderList.remove(food)
                    orderList.append(allSetMeal[0][0])
                else:
                    break

    price=0  # 计算订单总价
    for food in orderList:
        price+=priceDict[food]
    price+=extraPrice
    return orderList,price


from flask import Flask,render_template,request
app=Flask(__name__)


def Index():
    return app.send_static_file("getOrder.html")


@app.route("/")
@app.route("/<category>")
def root(category="主食"):  # 首页、主食、小食、饮品、套餐/组合，点击后可跳转到主页或菜单中所有的主食、小食、饮品或套餐/组合
    if category=="首页":  # 制作首页图片切换及滚动效果
        content="""
        <div style="text-align:center">
            <br><img src="./static/1.png" width=800px id="pic"><br>
            <span id="homepage" class="selectedDot" No="1">●</span>
            <span id="homepage" No="2">●</span>
            <span id="homepage" No="3">●</span>
            <span id="homepage" No="4">●</span>
            <script type="text/javascript">
                $("#homepage").click(function(){
                    imgNo=$(this).attr("No");
                    $("#pic").attr("src","./static/"+imgNo+".png");
                    $(".selectedDot").removeClass("selectedDot");
                    $(this).addClass("selectedDot");
                });
                var cycleImg=setInterval("changeImg()",3000);
                function changeImg(){
                    var nowImgNo=$(".selectedDot").attr("No");
                    nowImgNo++;
                    if(nowImgNo>4){
                        nowImgNo=1;
                    }
                    $("#pic").attr("src","./static/"+nowImgNo+".png");
                    $(".selectedDot").removeClass("selectedDot");
                    $("#homepage[No='"+nowImgNo+"']").addClass("selectedDot");
                }
                $("#pic").mouseover(function(){
                    clearInterval(cycleImg);
                })
                $("#pic").mouseout(function(){
                    cycleImg=setInterval("changeImg()",3000);
                })
            </script>
        </div>
        """
    else:  # 对主食、小食、饮品、套餐/组合的处理
        counter = 0
        content = """    <div style="width:100%;background-color:#FF6600;margin:0px;height:2px"></div>
        <table cellpadding=8px cellspacing=8px width=100% style="table-layout:fixed;text-align:center;
        color:#8e4820;line-height:40px;background-color:#fff6f0">"""  # 设定显示菜品的表格的样式
        for food in transDict[category]:
            if category=="套餐组合":
                foodInSet=str(setMealDict[(food,priceDict[food])])[1:-1].replace("'","").replace("可选小食", "<br>"+selectableSnack).replace("可选饮品","<br>"+selectableDrink)
                content += """<td>""" + food + "<br>" +foodInSet+"<br>"+str(priceDict[food]) + "</br></td>"
                # 第一行显示菜品名称，第二行显示套餐/组合中包含的单品，第三行显示菜品价格
            else:
                content+="""<td>"""+food+"<br>"+str(priceDict[food])+"</br></td>"  # 第一行显示菜品名称，第二行显示菜品价格
            counter+=1
            if counter>5:
                content+="""</tr><tr>"""
                counter=0
        content+="""</tr></table><div style="width:100%;background-color:#FF6600;margin:0px;height:2px"></div>"""

    return render_template("getOrder.html", foodList=content)


@app.route("/getOrder/",methods=["get","post"])
def getOrder():  # 获取客人点单信息
    order=request.form["orderText"].split(" ")
    if " " in order:
        order=order.remove(" ")  # 防止点单时多输入空格
    wrongList=[]
    wrongReply="""<p style="text-align:center"><br>您所输入的下列菜品不存在：<br><br>
            <div style="width:100%;background-color:#FF6600;margin:0px;height:2px"></div>"""+"</p>"
    for food in order:  # 排除输错名称的菜品
        if food not in allMenu:
            order.remove(food)
            wrongList.append(food)
    if wrongList!=[]:
        wrongReply=wrongReply[:wrongReply.index("<div")]+str(wrongList)[1:-1].replace("'","").replace(",","<br>")\
                   +wrongReply[wrongReply.index("<div"):]  # 将输错名称的菜品加入wrongReply中
    if wrongReply=="""<p style="text-align:center"><br>您所输入的下列菜品不存在：<br><br>
            <div style="width:100%;background-color:#FF6600;margin:0px;height:2px"></div>"""+"</p>":
        wrongReply=""  # 如果没有输错名称的菜品，则不再显示“菜品不存在”

    reply=html+wrongReply
    price=str(makeSetGetPrice(order)[1])
    reply+="""<p style="text-align:center;font-size:20px;color:#FF6600">您所点的菜品有：<br>
    <br>"""+str(makeSetGetPrice(order)[0])[1:-1].replace("'","")\
        .replace(",","<br>").replace("[","").replace("]","")\
          +"</p>"+"""<br><div style="width:100%;background-color:#FF6600;margin:0px;height:2px"></div>
          <br>"""+"""<p style="text-align:center;font-size:20px;color:#FF6600">总价为"""+ price + "元</p><br>"+"""<div style="width:100%;
          background-color:#FF6600;margin:0px;height:2px"></div><br>"""  # 显示客人点的所有菜品（已被自动凑成套餐）及总价
    recommend=recommendSet(order)  # 显示向客人推荐的套餐
    returnHomepage="""<br><div style="text-align: center;color:#8e4820">是否返回继续点餐？<br><br><button><a href="/首页">是
    </a></button><button>否</button></div>"""  # 选择回到主页继续点餐或留在当前页面
    return reply+recommend+returnHomepage


@app.route("/searchFood/",methods=["get","post"])  # 搜索某件商品，关键词以空格分开，获得包括所有关键词的结果
def searchFood():
    searchText=request.form["searchText"].split(" ")
    searchResult=html+"""<div style="text-align:center;font-size:20px;color:#8e4820"><br><br>我们为您搜索到了以下商品:"""+"<br><br>"
    for menu in allMenu:
        for word in searchText:  # 将顾客输入的各个关键词与菜品名称进行比对
            tmp=searchText[:]
            if word in menu:
                tmp.remove(word)
            if tmp==[]:
                searchResult +=menu+"<br>"

    if searchResult==html+"""<div style="text-align:center;font-size:20px;color:#8e4820"><br><br>我们为您搜索到了以下商品:"""+"<br><br>":
        searchResult = html+"""<div style="text-align:center;font-size:20px;color:#8e4820"><br>很抱歉，我们没有搜索到相关商品"""
    return searchResult+"</div>"


if __name__=="__main__":
    app.run(host="0.0.0.0",port=80,debug=True)


#eof
