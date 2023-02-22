from flask import Flask, request, render_template, session, redirect, url_for
import pyodbc as pdb
from datetime import timedelta
import datetime
import sys
import io

app = Flask(__name__)

app.secret_key = 'secret'
app.permanent_session_lifetime = timedelta(days=5)

def login_con():
    driver = "{SQL Server}"
    server = "DESKTOP-9UHN239¥SQLEXPRESS"
    database = "householdDB"
    trusted_connection = "yes"

    cnxn = pdb.connect("DRIVER=" + driver + ";SERVER=" + server + ";DATABASE=" + database + ";Trusted_Connection=" + trusted_connection + ";")
    cursor = cnxn.cursor()
    print("Database Connected!")
    return cnxn, cursor

cn, cur = login_con()

def closeSQL(_cursor, _cnxn):
    _cursor.close()
    _cnxn.close()
    print("Database closed...")
    return None

def submit_sql(user_id, user_name):
    today = datetime.date.today()
    month = '{0:%Y%m}'.format(today)
    sql_count = "select max(commodity_No) as number\
                from money_history \
                where ID = '{}' and FORMAT(buy_date, 'yyyyMM')='{}'".format(user_id, month)
    print("sql_count:{}".format(sql_count))
    cur.execute(sql_count)
    count_array = cur.fetchall()
    commodity_No = count_array[0].number
    if commodity_No != None:
        commodity_No = count_array[0].number
    else:
        commodity_No = "{}000".format(month)
    print("commodity_No:{}".format(commodity_No))
    count_data = 0
    for i in range(1,6):
        i = str(i)
        if request.form['purchase_amount_'+i] != "":
            commodity_No = int(commodity_No) + 1
            print("商品No：{}".format(commodity_No))
            category_cd = '01'
            category_name = '食費'
            commodity = request.form['purchase_name_'+i]
            print("商品名：{}".format(commodity))
            cost = request.form['purchase_amount_'+i]
            comment = request.form['purchase_comment_'+i]

            insert_sql = "insert into dbo.money_history(ID ,name, commodity_No ,category_cd, category_nm, commodity, cost, buy_date, comment)\
                values('{}', '{}', '{}', '{}', '{}', '{}', {}, GETDATE(), '{}')".format(user_id, user_name, commodity_No, category_cd, category_name, commodity, cost, comment)
            cur.execute(insert_sql)
            cn.commit()

            count_data += 1

    for i in range(6,11):
        i = str(i)
        if request.form['purchase_amount_'+i] != "":
            commodity_No = int(commodity_No) + 1
            print("商品No：{}".format(commodity_No))
            category_cd = '02'
            category_name = '消耗品'
            commodity = request.form['purchase_name_'+i]
            print("商品名：{}".format(commodity))
            cost = request.form['purchase_amount_'+i]
            comment = request.form['purchase_comment_'+i]

            insert_sql = "insert into dbo.money_history(ID ,name, commodity_No ,category_cd, category_nm, commodity, cost, buy_date, comment)\
                values('{}', '{}', '{}', '{}', '{}', '{}', {}, GETDATE(), '{}')".format(user_id, user_name, commodity_No, category_cd, category_name, commodity, cost, comment)
            cur.execute(insert_sql)
            cn.commit()

            count_data += 1

    for i in range(11,16):
        i = str(i)
        if request.form['purchase_amount_'+i] != "":
            commodity_No = int(commodity_No) + 1
            print("商品No：{}".format(commodity_No))
            category_cd = '03'
            category_name = 'サービス、その他'
            commodity = request.form['purchase_name_'+i]
            print("商品名：{}".format(commodity))
            cost = request.form['purchase_amount_'+i]
            comment = request.form['purchase_comment_'+i]

            insert_sql = "insert into dbo.money_history(ID ,name, commodity_No ,category_cd, category_nm, commodity, cost, buy_date, comment)\
                values('{}', '{}', '{}', '{}', '{}', '{}', {}, GETDATE(), '{}')".format(user_id, user_name, commodity_No, category_cd, category_name, commodity, cost, comment)
            cur.execute(insert_sql)
            cn.commit()

            count_data += 1

    print("{}件登録したぞ！".format(count_data))

    return count_data


@app.route('/leadlogin')
def access_denined():
    return render_template('please_login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_income', None)

    return render_template('logout.html')

@app.route('/', methods=['GET', 'POST'])
def form():
    if session.get('user_id', None) == None:
        if request.method == 'POST':
            user_id = str(request.form['ID'])
            user_pwd = str(request.form['pwd'])
            cur.execute('SELECT * FROM USER_MST WHERE ID='+user_id)
            rows = cur.fetchall()
            row = rows[0]
            user_data = [row.ID, row.NAME, row.PASSWORD, row.MONTHLY_INCOME]
            user_name = user_data[1]
            user_income = user_data[3]

            session['user_id'] = user_id
            session['user_name'] = user_name
            session['user_income'] = user_income

            if user_data[2] == user_pwd:
                return redirect(url_for('main_menu', user_id=user_id))
            else:
                return render_template('index_household.html')

        else:
            return render_template('index_household.html')
    else:
        user_id = session.get('user_id')
        user_name = session.get('user_name')
        user_income = session.get('user_income')

        return redirect(url_for('main_menu', user_id=user_id))

@app.route('/main/<user_id>')
def main_menu(user_id):
    user_id = session.get('user_id')
    user_name = session.get('user_name')
    date = datetime.date.today()
    date_currender = "{0:%Y年%#m月%#d日}".format(date)

    if user_id == None:
        return redirect('/')

    return render_template('main_page.html', user_id=user_id, user_name=user_name, date=date_currender)


@app.route('/main/household/<user_id>')
def household(user_id):
    user_id = session.get('user_id', None)
    user_name = session.get('user_name', None)
    user_income = session.get('user_income', None)
    page_id = "page1"
    print("user_id:{}".format(user_id))
    print("user_income:{}".format(user_income))

    if user_id == None:
        return redirect('/')

    date = datetime.date.today()

    total_sql = "select convert(int, sum(A.cost)) as cost from money_history A where A.ID = '{}' and month(A.buy_date) = '{}' group by A.ID".format(user_id, date.month)
    cur.execute(total_sql)
    rows = cur.fetchall()
    if rows != []:
        total_all = rows[0].cost
        print("総額：{}".format(total_all))
        cost_per_day = round(total_all/date.day)
        cost_income_rate = round(total_all/float(user_income)*100, 1)
    else:
        total_all = 0
        cost_per_day = 0
        cost_income_rate = 0

    foodcost_sql = "select convert(int, sum(A.cost)) as food_cost from money_history A where A.ID = '{}' and month(A.buy_date) = '{}' and A.category_cd = '01' group by A.ID".format(user_id, date.month)
    cur.execute(foodcost_sql)
    rows_food = cur.fetchall()
    if rows_food != []:
        food_all = rows_food[0].food_cost
        food_cost_per_day = round(food_all/date.day)
        food_income_rate = round(food_all/float(user_income)*100, 1)
    else:
        food_all = 0
        food_cost_per_day = 0
        food_income_rate = 0

    cnsmblcost_sql = "select convert(int, sum(A.cost)) as consumable_cost from money_history A where A.ID = '{}' and month(A.buy_date) = '{}' and A.category_cd = '02' group by A.ID".format(user_id, date.month)
    cur.execute(cnsmblcost_sql)
    rows_cnsmbl = cur.fetchall()
    if rows_cnsmbl != []:
        consumable_all = rows_cnsmbl[0].consumable_cost
        cnsmbl_cost_per_day = round(consumable_all/date.day)
        cnsmbl_income_rate = round(consumable_all/float(user_income)*100, 1)

    else:
        consumable_all = 0
        cnsmbl_cost_per_day = 0
        cnsmbl_income_rate = 0

    servicecost_sql = "select convert(int, sum(A.cost)) as service_cost from money_history A where A.ID = '{}' and month(A.buy_date) = '{}' and A.category_cd = '03' group by A.ID".format(user_id, date.month)
    cur.execute(servicecost_sql)
    rows_service = cur.fetchall()
    if rows_service != []:
        service_all = rows_service[0].service_cost
        service_cost_per_day = round(service_all/date.day)
        service_income_rate = round(service_all/float(user_income)*100, 1)
    else:
        service_all = 0
        service_cost_per_day = 0
        service_income_rate = 0


    return render_template('household_main.html',user_id=user_id, user_name=user_name
    , total_all=total_all, cost_per_day=cost_per_day, cost_income_rate=cost_income_rate
    , food_all=food_all, food_cost_per_day=food_cost_per_day, food_income_rate=food_income_rate
    , consumable_all=consumable_all, cnsmbl_cost_per_day=cnsmbl_cost_per_day, cnsmbl_income_rate=cnsmbl_income_rate
    ,service_all=service_all, service_cost_per_day=service_cost_per_day, service_income_rate=service_income_rate
    )

@app.route('/main/household/submit/<user_id>', methods=['GET', 'POST'])
def submit_data(user_id):
    user_id = session.get('user_id', None)
    user_name = session.get('user_name', None)

    if request.method == 'POST':
        submit_list = [request.form['purchase_amount_'+str(i)] for i in range(1,16)]
        print(submit_list)
        check_list = [x for x in submit_list if x is not '']
        print(check_list)

        if check_list != []:
            count_data = submit_sql(user_id, user_name)
            print(count_data)

            return redirect(url_for('submit_done',user_id=user_id, count_data=count_data))
        
        else:
            return render_template('submit_purchase.html', user_id=user_id, user_name=user_name)
    else:
        return render_template('submit_purchase.html', user_id=user_id, user_name=user_name)

@app.route('/main/household/submit/done/<user_id>/<count_data>')
def submit_done(user_id, count_data):
    print(count_data)
    user_id = session.get('user_id', None)

    return render_template('submit_done.html', user_id=user_id, count_data=count_data)

@app.route('/main/household/data_detail/page<p>/<user_id>', methods=['GET', 'POST'])
def data_manage(p, user_id):
    print("p:{}".format(p))
    user_id = session.get('user_id', None)
    user_name = session.get('user_name', None)
    
    page_no = []

    if p == '1' or p == '2':
        pb2 = 1
        pb1 = 2
        pn = 3
        pa1 = 4
        pa2 = 5
    
    else:
        for i in range(5):
            page_no.append(int(p) + i - 2)

        print(page_no)
        pb2 = str(page_no[0])
        pb1 = str(page_no[1])
        pn = str(page_no[2])
        pa1 = str(page_no[3])
        pa2 = str(page_no[4])


    sql_history = "select commodity_No, category_nm, commodity, cost, buy_date, comment from money_history where ID = '{}' order by commodity_No desc".format(user_id)
    cur.execute(sql_history)
    history_data = cur.fetchall()
    data_number = len(history_data)
    print("データ件数：{}".format(data_number))

    if data_number == (int(p) - 1) * 10 and data_number != 0:
        return redirect('/main/household/data_detail/page{}/{}'.format(int(p)-1, user_id))
    
    commodity_No_history = []
    category_history = []
    commodity_history = []
    cost_history = []
    buy_date_history = []
    comment_history = []

    data_from = (int(p) - 1) * 10
    data_to = int(p) * 10
    print("from {} to {}".format(data_from, data_to))

    if data_number-1 >= data_from and data_number < data_to:
        for i in range(data_from, data_number):
            if  history_data[i] != None:
                commodity_No_history.append(history_data[i].commodity_No)
                category_history.append(history_data[i].category_nm)
                commodity_history.append(history_data[i].commodity)
                cost_history.append(history_data[i].cost)
                buy_date_history.append(history_data[i].buy_date)
                comment_history.append(history_data[i].comment)
        
        for i in range(data_number, data_to):
            commodity_No_history.append(None)
            category_history.append(None)
            commodity_history.append(None)
            cost_history.append(None)
            buy_date_history.append(None)
            comment_history.append(None)
    
    elif data_number >= data_to:
        for i in range(data_from, data_to):
            if  history_data[i] != None:
                commodity_No_history.append(history_data[i].commodity_No)
                category_history.append(history_data[i].category_nm)
                commodity_history.append(history_data[i].commodity)
                cost_history.append(history_data[i].cost)
                buy_date_history.append(history_data[i].buy_date)
                comment_history.append(history_data[i].comment)
    
    elif data_number-1 < data_from:
        for i in range(data_from, data_to):
            commodity_No_history.append(None)
            category_history.append(None)
            commodity_history.append(None)
            cost_history.append(None)
            buy_date_history.append(None)
            comment_history.append(None)

    if request.method == 'POST':
        for i in range(1,11):
            i = str(i)
            try:
                if request.form['category_{}'.format(i)]:
                    commodity_No = request.form['commodity_No_{}'.format(i)]
                    commodity = request.form['commodity_{}'.format(i)]
                    cost = request.form['cost_{}'.format(i)]
                    buy_date = request.form['submit_day_{}'.format(i)]
                    comment = request.form['comment_{}'.format(i)]
                    category_nm = request.form['category_{}'.format(i)]
                    if category_nm == '食費':
                        category_cd = "01"
                    elif category_nm == '消耗品':
                        category_cd = "02"
                    else:
                        category_cd = "03"

                    sql_edit = "update money_history set category_cd='{}', category_nm='{}', commodity='{}', cost={}, buy_date='{}', comment='{}' where ID ='{}' and commodity_No='{}'"\
                    .format(category_cd, category_nm, commodity, cost, buy_date, comment, user_id, commodity_No)
                    print("sql_edit:{}".format(sql_edit))
                    cur.execute(sql_edit)
                    cn.commit()

                    i = int(i) - 1
                    commodity_No_history[i] = commodity_No
                    category_history[i] = category_nm
                    commodity_history[i] = commodity
                    cost_history[i] = cost
                    buy_date_history[i] = buy_date
                    comment_history[i] = comment

                    break
            except:
                print("情報を受け取っていません。")           

    return render_template('edit_data.html', user_id=user_id, pb2=pb2, pb1=pb1, pn=pn, pa1=pa1, pa2=pa2, data_number=data_number, p=p,
    commodity_history_No_1 = commodity_No_history[0], category_history_1=category_history[0], commodity_history_1=commodity_history[0], cost_history_1=cost_history[0],buy_date_history_1=buy_date_history[0], comment_history_1=comment_history[0],
    commodity_history_No_2 = commodity_No_history[1], category_history_2=category_history[1], commodity_history_2=commodity_history[1], cost_history_2=cost_history[1],buy_date_history_2=buy_date_history[1], comment_history_2=comment_history[1],
    commodity_history_No_3 = commodity_No_history[2], category_history_3=category_history[2], commodity_history_3=commodity_history[2], cost_history_3=cost_history[2],buy_date_history_3=buy_date_history[2], comment_history_3=comment_history[2],
    commodity_history_No_4 = commodity_No_history[3], category_history_4=category_history[3], commodity_history_4=commodity_history[3], cost_history_4=cost_history[3],buy_date_history_4=buy_date_history[3], comment_history_4=comment_history[3],
    commodity_history_No_5 = commodity_No_history[4], category_history_5=category_history[4], commodity_history_5=commodity_history[4], cost_history_5=cost_history[4],buy_date_history_5=buy_date_history[4], comment_history_5=comment_history[4],
    commodity_history_No_6 = commodity_No_history[5], category_history_6=category_history[5], commodity_history_6=commodity_history[5], cost_history_6=cost_history[5],buy_date_history_6=buy_date_history[5], comment_history_6=comment_history[5],
    commodity_history_No_7 = commodity_No_history[6], category_history_7=category_history[6], commodity_history_7=commodity_history[6], cost_history_7=cost_history[6],buy_date_history_7=buy_date_history[6], comment_history_7=comment_history[6],
    commodity_history_No_8 = commodity_No_history[7], category_history_8=category_history[7], commodity_history_8=commodity_history[7], cost_history_8=cost_history[7],buy_date_history_8=buy_date_history[7], comment_history_8=comment_history[7],
    commodity_history_No_9 = commodity_No_history[8], category_history_9=category_history[8], commodity_history_9=commodity_history[8], cost_history_9=cost_history[8],buy_date_history_9=buy_date_history[8], comment_history_9=comment_history[8],
    commodity_history_No_10 = commodity_No_history[9], category_history_10=category_history[9], commodity_history_10=commodity_history[9], cost_history_10=cost_history[9],buy_date_history_10=buy_date_history[9], comment_history_10=comment_history[9]
    )

@app.route('/main/household/data_detail/page<p>/<user_id>/delete', methods=['GET', 'POST'])
def delete_data(user_id, p):
    if request.method == 'POST':
        for i in range(1,11):
            i = str(i)
            try:
                if request.form['category_{}'.format(i)]:
                    commodity_No = request.form['commodity_No_{}'.format(i)]

                    sql_check = "select commodity_No, category_nm, commodity, cost, buy_date, comment from money_history where ID = '{}' and commodity_No = '{}'"\
                        .format(user_id, commodity_No)
                    cur.execute(sql_check)
                    data_check = cur.fetchall()

                    commodity = data_check[0].commodity
                    cost = data_check[0].cost
                    buy_date = data_check[0].buy_date
                    comment = data_check[0].comment
                    category_nm = data_check[0].category_nm

                    sql_delete = "delete from money_history where ID = '{}' and commodity_No = '{}'"\
                    .format(user_id, commodity_No)
                    print("sql_delete:{}".format(sql_delete))
                    cur.execute(sql_delete)
                    cn.commit()

                    break
            except:
                    print("情報を受け取っていません。")
        return render_template('data_deleted.html', user_id=user_id, p=p,
                        commodity_No=commodity_No, category=category_nm, commodity=commodity, cost=cost, buy_date=buy_date, comment=comment)
    else:
        return redirect('/main/household/<user_id>')


if __name__ == '__main__':
    app.run(port=8000, debug=True)