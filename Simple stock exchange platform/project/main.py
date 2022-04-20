from flask import Blueprint, render_template, request
from flask_wtf import FlaskForm
from flask_login import login_required, current_user
from wtforms import SelectField, IntegerField
from wtforms.validators import NumberRange
from sqlalchemy import desc
import traceback

from project.models import Company, Shareholder, ShareForSale, ShareForPurchase, Activity
from . import db


main = Blueprint('main', __name__)

class BuyForm(FlaskForm):
    company_to_buy = SelectField('Company:', choices=[], validate_choice=False)
    ammount_to_buy = IntegerField('Ammount:', validators=[NumberRange(min=1)], default='1')
    price_to_buy = IntegerField('Price:', validators=[NumberRange(min=1)], default='1')
    buy_flag = ''

class SellForm(FlaskForm):
    company_to_sell = SelectField('Company:', choices=[], validate_choice=False)
    ammount_to_sell = IntegerField('Ammount:', validators=[NumberRange(min=1)], default='1')
    price_to_sell = IntegerField('Price:', validators=[NumberRange(min=1)], default='1')
    buy_sell = ''

def buy_transaction(list_of_offers, company_to_buy, ammount_to_buy, price_to_buy, enough):
    db.session.remove()
    db.session.begin()
    bought_ammount = 0
    list_prices = []
    list_shares = []
    try:
        if list_of_offers != [None]:
            for i in range (len(list_of_offers)):
                if list_of_offers[i].user_id == current_user.id:
                    del list_of_offers[i]
        if list_of_offers == [None]:
            new_share_for_purchase = ShareForPurchase(
                                     user_id=current_user.id,
                                     company_id=company_to_buy,
                                     ammount_to_buy=ammount_to_buy,
                                     ammount_bought=bought_ammount,
                                     price=price_to_buy
            )

            db.session.add(new_share_for_purchase)
            db.session.commit()
            return 3

        else:
            for cur in list_of_offers:
                if int(cur.ammount_to_sell - cur.ammount_sold) == int(ammount_to_buy) - bought_ammount:
                
                    list_prices.append(cur.price)
                    list_shares.append(int(cur.ammount_to_sell) - int(cur.ammount_sold))
                    final_price = 0

                    for i in range(len(list_prices)):
                        final_price += list_prices[i] * list_shares[i]
                    final_price = round(final_price/ammount_to_buy)
                    
                    new_shareholder = Shareholder(
                                      user_id=current_user.id,
                                      company_id=cur.company_id,
                                      order_share_ammount=ammount_to_buy,
                                      order_share_price=final_price
                    )

                    new_activity_buyer = Activity(
                                         user_id=current_user.id,
                                         operration='bought',
                                         ammount=ammount_to_buy,
                                         company_id=cur.company_id,
                                         price=final_price
                    )

                    new_activity_seller = Activity(
                                          user_id=cur.user_id,
                                          operration='sold',
                                          ammount=cur.ammount_to_sell - cur.ammount_sold,
                                          company_id=cur.company_id,
                                          price=cur.price
                    )

                    db.session.delete(cur)
                    db.session.add(new_shareholder)
                    db.session.add(new_activity_buyer)
                    db.session.add(new_activity_seller)
                    db.session.commit()

                    return 1

                elif int(cur.ammount_to_sell - cur.ammount_sold) > int(ammount_to_buy) - bought_ammount:

                    list_prices.append(cur.price)
                    list_shares.append(int(ammount_to_buy) - bought_ammount)
                    final_price = 0

                    for i in range(len(list_prices)):
                        final_price += list_prices[i] * list_shares[i]
                    final_price = round(final_price/ammount_to_buy)

                    ShareForSale.query.filter_by(id=cur.id).delete()
                    update_share_for_sale = ShareForSale(
                                            user_id=cur.id,
                                            company_id=cur.company_id,
                                            ammount_to_sell=cur.ammount_to_sell,
                                            ammount_sold=cur.ammount_sold + (int(ammount_to_buy) - bought_ammount),
                                            price=cur.price
                    )

                    new_shareholder = Shareholder(
                                      user_id=current_user.id,
                                      company_id=cur.company_id,
                                      order_share_ammount=ammount_to_buy,
                                      order_share_price=final_price
                    )
                                      
                    new_activity_buyer = Activity(
                                         user_id=current_user.id,
                                         operration='bought',
                                         ammount=ammount_to_buy,
                                         company_id=cur.company_id,
                                         price=final_price
                    )

                    new_activity_seller = Activity(
                                         user_id=cur.user_id,
                                         operration='sold',
                                         ammount=int(ammount_to_buy) - bought_ammount,
                                         company_id=cur.company_id,
                                         price=cur.price
                    )

                    db.session.add(new_shareholder)
                    db.session.add(new_activity_buyer)
                    db.session.add(new_activity_seller)
                    db.session.add(update_share_for_sale)
                    db.session.commit()
                    
                    return 1

                elif int(cur.ammount_to_sell - cur.ammount_sold) < int(ammount_to_buy) - bought_ammount:
                    bought_ammount += int(cur.ammount_to_sell - cur.ammount_sold)
                    list_prices.append(cur.price)
                    list_shares.append(int(cur.ammount_to_sell - cur.ammount_sold))

                    new_activity_seller = Activity(
                                         user_id=cur.user_id,
                                         operration='sold',
                                         ammount=cur.ammount_to_sell,
                                         company_id=cur.company_id,
                                         price=cur.price
                    )

                    db.session.delete(cur)
                    db.session.add(new_activity_seller)
                    db.session.commit()
        
        if enough == False:
            final_price = 0

            for i in range(len(list_prices)):
                final_price += list_prices[i] * list_shares[i]
            final_price = round(final_price/ammount_to_buy)

            if bought_ammount == 0:
                operration = 'waiting for offers'
                price = price_to_buy
                ammount = ammount_to_buy
                to_return = 3
            else:
                operration = 'partially bought'
                price = final_price
                ammount = bought_ammount
                to_return = 2            

            new_activity_buyer = Activity(
                                user_id=current_user.id,
                                operration=operration,
                                ammount=ammount,
                                company_id=company_to_buy,
                                price=price
            )

            new_share_for_purchase = ShareForPurchase(
                                     user_id=current_user.id,
                                     company_id=company_to_buy,
                                     ammount_to_buy=ammount_to_buy,
                                     ammount_bought=bought_ammount,
                                     price=price_to_buy
            )

            db.session.add(new_activity_buyer)
            db.session.add(new_share_for_purchase)
            db.session.commit()
            return to_return
    except:
        traceback.print_exc()
        db.session.rollback()
        return 4
    return 5




def sell_transaction(list_of_offers, company_to_sell, ammount_to_sell, price_to_sell, enough):
    db.session.remove()
    db.session.begin()
    sold_ammount = 0
    list_prices = []
    list_shares = []
    try:
        if list_of_offers != [None]:
            for i in range (len(list_of_offers)):
                if list_of_offers[i].user_id == current_user.id:
                    del list_of_offers[i]
        check_share = None
        check_share = Shareholder.query.filter_by(user_id=current_user.id)\
                         .filter_by(company_id=company_to_sell)\
                         .filter(Shareholder.order_share_ammount>ammount_to_sell)\
                         .first()
        if check_share is None:
            to_kill = Shareholder.query.filter_by(user_id=current_user.id)\
                            .filter_by(company_id=company_to_sell)\
                            .filter_by(order_share_ammount=ammount_to_sell)\
                            .first()
            if to_kill is not None:
                Shareholder.query.filter_by(id=to_kill.id).delete()
                db.session.commit()
        else:
            check_share = Shareholder.query.filter_by(user_id=current_user.id)\
                                           .filter_by(company_id=company_to_sell)\
                                           .filter(Shareholder.order_share_ammount>ammount_to_sell)\
                                           .first()
            if check_share is not None:
                current_share = check_share.order_share_ammount
                current_price = check_share.order_share_price
                Shareholder.query.filter_by(id=check_share.id).delete()
                new_shareholder = Shareholder(
                                  user_id=current_user.id,
                                  company_id=company_to_sell,
                                  order_share_ammount=current_share - ammount_to_sell,
                                  order_share_price=current_price
                )
                db.session.add(new_shareholder)
                db.session.commit()


        if len(list_of_offers) == 0:

            new_share_for_sale = ShareForSale(
                                 user_id=current_user.id,
                                 company_id=company_to_sell,
                                 ammount_to_sell=ammount_to_sell,
                                 ammount_sold=sold_ammount,
                                 price=price_to_sell
            )

            new_activity = Activity(
                           user_id=current_user.id,
                           operration='waiting to be sold',
                           ammount=ammount_to_sell,
                           company_id=company_to_sell,
                           price=price_to_sell
            )
            db.session.add(new_activity)
            db.session.add(new_share_for_sale)
            db.session.commit()
            return 3
        else:
            for cur in list_of_offers:
                if int(cur.ammount_to_buy - cur.ammount_bought) == int(ammount_to_sell) - sold_ammount:
                
                    list_prices.append(cur.price)
                    list_shares.append(int(ammount_to_sell) - sold_ammount)
                    final_price = 0

                    for i in range(len(list_prices)):
                        final_price += list_prices[i] * list_shares[i]
                    final_price = round(final_price/ammount_to_sell)
                    
                    new_shareholder = Shareholder(
                                      user_id=cur.user_id,
                                      company_id=cur.company_id,
                                      order_share_ammount=ammount_to_sell,
                                      order_share_price=cur.price
                    )

                    new_activity_buyer = Activity(
                                         user_id=cur.user_id,
                                         operration='bought',
                                         ammount=int(ammount_to_sell) - sold_ammount,
                                         company_id=cur.company_id,
                                         price=cur.price
                    )

                    new_activity_seller = Activity(
                                          user_id=current_user.id,
                                          operration='sold',
                                          ammount=ammount_to_sell,
                                          company_id=cur.company_id,
                                          price=final_price
                    )

                    db.session.delete(cur)
                    db.session.add(new_shareholder)
                    db.session.add(new_activity_buyer)
                    db.session.add(new_activity_seller)
                    db.session.commit()

                    return 1

                elif int(cur.ammount_to_buy - cur.ammount_bought) > int(ammount_to_sell) - sold_ammount:

                    list_prices.append(cur.price)
                    list_shares.append(int(ammount_to_sell) - sold_ammount)
                    final_price = 0

                    for i in range(len(list_prices)):
                        final_price += list_prices[i] * list_shares[i]
                    final_price = round(final_price/ammount_to_sell)
                                      
                    new_activity_buyer = Activity(
                                         user_id=cur.user_id,
                                         operration='bought',
                                         ammount=int(ammount_to_sell) - sold_ammount,
                                         company_id=cur.company_id,
                                         price=cur.price
                    )

                    new_activity_seller = Activity(
                                         user_id=current_user.id,
                                         operration='sold',
                                         ammount=ammount_to_sell,
                                         company_id=cur.company_id,
                                         price=final_price
                    )

                    db.session.add(new_activity_buyer)
                    db.session.add(new_activity_seller)
                    cur.ammount_bought = {'ammount_bought': int(cur.ammount_bought) + int(new_activity_seller.ammount)}
                    db.session.commit()
                    
                    return 1
                
                elif int(cur.ammount_to_buy - cur.ammount_bought) < int(ammount_to_sell) - sold_ammount:
                    sold_ammount += int(cur.ammount_to_buy - cur.ammount_bought)
                    list_prices.append(cur.price)
                    list_shares.appned(int(cur.ammount_to_buy - cur.ammount_bought))

                    new_activity_seller = Activity(
                                         user_id=cur.User.id,
                                         operration='sold',
                                         ammount=cur.ammount_to_buy,
                                         company_id=cur.company_id,
                                         price=cur.price
                    )

                    new_shareholder = Shareholder(
                            user_id=cur.id,
                            company_id=cur.company_id,
                            order_share_ammount=int(cur.ammount_to_buy - cur.ammount_bought),
                            order_share_price=cur.price
                    )

                    db.session.delete(cur)
                    db.session.add(new_activity_seller)
                    db.session.commit()
        
        if enough == False:
            final_price = 0

            for i in range(len(list_prices)):
                final_price += list_prices[i] * list_shares[i]
            final_price = round(final_price/ammount_to_sell)
                                        
            new_activity_buyer = Activity(
                                user_id=current_user.id,
                                operration='sold',
                                ammount=sold_ammount,
                                company_id=cur.company_id,
                                price=final_price
            )

            new_share_for_sell = ShareForSale(
                                     user_id=current_user.id,
                                     company_id=company_to_sell,
                                     ammount_to_sell=ammount_to_sell,
                                     ammount_seold=sold_ammount,
                                     price=price_to_sell
            )

            db.session.add(new_activity_buyer)
            db.session.add(new_share_for_sell)
            db.session.commit()
            return 2


    except:
        traceback.print_exc()
        db.session.rollback()
        return 4
    return 5

def update_your_shares_table():
    db.session.remove()
    db.session.begin()
    try:
        for temp_company in range(1,3):

            update_list = []
            list_shares = []
            list_prices = []
            final_price = 0
            final_share_ammount = 0
            update_list = Shareholder.query.filter_by(user_id=current_user.id)\
                                           .filter_by(company_id=temp_company)\
                                           .order_by(Shareholder.order_date)\
                                           .all()
            for cur in update_list:
                list_shares.append(cur.order_share_ammount)
                list_prices.append(cur.order_share_price)
                date = cur.order_date
                db.session.delete(cur)

            for i in range(len(list_shares)):
                final_price += list_shares[i] * list_prices[i]
                final_share_ammount += list_shares[i]
            
            if final_share_ammount != 0:
                final_price = round(final_price/final_share_ammount)

                updated_shareholder = Shareholder(
                                    user_id=current_user.id,
                                    company_id=temp_company,
                                    order_share_ammount=final_share_ammount,
                                    order_share_price=final_price,
                                    order_date=date
                )

                db.session.add(updated_shareholder)
                db.session.commit()
    except:
        traceback.print_exc()
        db.session.rollback()


@main.route('/')
def index():
    from project.models import Company, Shareholder, ShareForSale, ShareForPurchase, Activity, db

    db.session.query(ShareForPurchase).delete()
    db.session.query(ShareForSale).delete()
    db.session.query(Activity).delete()
    db.session.query(Shareholder).delete()
    First = Shareholder(user_id=1, company_id=1, order_share_ammount=100, order_share_price=120)
    Second = Shareholder(user_id=1, company_id=2, order_share_ammount=150, order_share_price=110)
    db.session.add(First)
    db.session.add(Second)
    db.session.commit()
    class Form(FlaskForm): pass
    form = Form()
    return render_template('index.html', query=Company.query.all(), form=form)

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    buy_form = BuyForm(request.form)
    sell_form = SellForm(request.form)
    buy_form.buy_flag = ''
    sell_form.sell_flag = ''
    activities = Activity.query.filter_by(user_id=current_user.id)

    if request.method == 'POST' and request.form['Submit'] == 'Buy':
        if type(buy_form.ammount_to_buy.data) == type(None):
            buy_form.buy_flag = 'No shares to buy'
        else:
            company_to_buy = int(buy_form.company_to_buy.data)
            ammount_to_buy = int(buy_form.ammount_to_buy.data)
            price_to_buy = int(buy_form.price_to_buy.data)
            list_of_offers = []
            current_ammount = 0
            enough = False
            for cur in ShareForSale.query.filter_by(company_id=company_to_buy)\
                                         .filter(ShareForSale.price<=price_to_buy)\
                                         .order_by(ShareForSale.price).all():
                if current_ammount < ammount_to_buy:
                    current_ammount += int(cur.ammount_to_sell) - int(cur.ammount_sold)
                    list_of_offers.append(cur)
                else:
                    enough = True
            flag = buy_transaction(list_of_offers, company_to_buy, ammount_to_buy, price_to_buy, enough)
            if flag == 1:
                buy_form.buy_flag = 'bought'
            elif flag == 2:
                buy_form.buy_flag = 'partially bought'
            elif flag == 3:
                buy_form.buy_flag = 'waiting for offers'
            elif flag == 4:
                buy_form.buy_flag = 'transaction faild'
            elif flag == 5:
                buy_form.sell_flag = 'well thats imposible but who knows'

    elif request.method == 'POST' and request.form['Submit'] == 'Sell':
        if type(sell_form.ammount_to_sell.data) == type(None)\
            or type(Shareholder.query.filter_by(user_id=current_user.id).first()) == type(None):
            sell_form.sell_flag = 'No shares to sell'
        else:
            company_to_sell = int(sell_form.company_to_sell.data)
            ammount_to_sell = int(sell_form.ammount_to_sell.data)
            price_to_sell = int(sell_form.price_to_sell.data)
            list_of_offers = []
            current_ammount = 0
            enough = False
            check_list = []
            check_list.append(Shareholder.query.filter_by(user_id=current_user.id)\
                                               .filter_by(company_id=company_to_sell)\
                                               .filter(Shareholder.order_share_ammount>=ammount_to_sell)\
                                               .first())
            if check_list != [None]:
                for cur in ShareForPurchase.query.filter_by(company_id=company_to_sell)\
                                                .filter(ShareForPurchase.price>=price_to_sell)\
                                                .order_by(desc(ShareForPurchase.price)).all():
                    if current_ammount < ammount_to_sell:
                        current_ammount += int(cur.ammount_to_buy) - int(cur.ammount_bought)
                        list_of_offers.append(cur)
                    else:
                        enough = True
                flag = sell_transaction(list_of_offers, company_to_sell, ammount_to_sell, price_to_sell, enough)
                if flag == 1:
                    sell_form.sell_flag = 'sold'
                elif flag == 2:
                    sell_form.sell_flag = 'partially sold'
                elif flag == 3:
                    sell_form.sell_flag = 'waiting for offers'
                elif flag == 4:
                    sell_form.sell_flag = 'transaction failed'
                elif flag == 5:
                    sell_form.sell_flag = 'well thats imposible but who knows'
            else:
                sell_form.sell_flag = 'you dont have these'
        
    update_your_shares_table()

    buy_form.company_to_buy.choices = [(company.id, company.name) for company in Company.query.all()]
    sell_form.company_to_sell.choices = [(shareholder.Company.id, shareholder.Company.name) for shareholder in Shareholder.query.filter_by(user_id=current_user.id)]
    
    query_my_shares = Shareholder.query.filter_by(user_id=current_user.id).order_by(Shareholder.company_id.name)
    qury_my_shares_for_sale = ShareForSale.query.filter_by(user_id=current_user.id)
    qury_my_sahres_to_buy = ShareForPurchase.query.filter_by(user_id=current_user.id)
    
    return render_template('profile.html', name=current_user.name,
                                         query_my_shares=query_my_shares,
                                         qury_my_shares_for_sale= qury_my_shares_for_sale,
                                         qury_my_sahres_to_buy=qury_my_sahres_to_buy,
                                         buy_form=buy_form,
                                         sell_form=sell_form,
                                         activities=activities)
