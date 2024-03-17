import json
import uuid
from flask_sqlalchemy import SQLAlchemy
from flask import abort
from datetime import datetime
from sqlalchemy.exc import IntegrityError


from app.extensions import db


class Mortgage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    principal = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    loan_term = db.Column(db.Integer, nullable=False)
    monthly_escrow = db.Column(db.Float, default=0.0)

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)
    
    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
    
    @staticmethod
    def get_all():
        return Mortgage.query.all()
    
    @staticmethod
    def get_by_id(mortgage_id):
        return Mortgage.query.get(mortgage_id)

    @staticmethod
    def create_from_json(json_data):
        new_mortgage = Mortgage(**json_data)
        db.session.add(new_mortgage)
        try:
            db.session.commit()
            return new_mortgage
        except IntegrityError:
            db.session.rollback()
            return None

    @staticmethod
    def update_by_id(mortgage_id, json_data):
        mortgage = Mortgage.get_by_id(mortgage_id)
        if mortgage:
            for key, value in json_data.items():
                setattr(mortgage, key, value)
            db.session.commit()
            return mortgage
        return None

    @staticmethod
    def delete_by_id(mortgage_id):
        mortgage = Mortgage.get_by_id(mortgage_id)
        if mortgage:
            db.session.delete(mortgage)
            db.session.commit()
            return True
        return False
    
    @classmethod
    def clear_and_load(cls, json_file_path):
        # Clear existing data
        cls.query.delete()
        db.session.commit()

        # Load new data from JSON file
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            mortgage_data = data['mortgage']
            new_mortgage = cls(
                principal=mortgage_data['principal'],
                interest_rate=mortgage_data['interest_rate'],
                start_date=mortgage_data['start_date'],
                loan_term=mortgage_data['loan_term'],
                monthly_escrow=mortgage_data['monthly_escrow']
            )
            db.session.add(new_mortgage)
            db.session.commit()

class BonusPayment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bonus_type = db.Column(db.String(50), nullable=False)  # 'cash' or 'rsu'
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, nullable=False)
    year_assigned = db.Column(db.Integer, nullable=False)

    # Function to add a bonus payment to the database
    def add_bonus_payment(bonus_type, amount, payment_date, year_assigned):
        try:
            new_bonus_payment = BonusPayment(
                bonus_type=bonus_type,
                amount=amount,
                payment_date=payment_date,
                year_assigned=year_assigned
            )
            db.session.add(new_bonus_payment)
            db.session.commit()
            return new_bonus_payment  # Return the newly created BonusPayment object
        except Exception as e:
            db.session.rollback()
            abort(500, description=str(e))  # Use Flask's abort to return an error

    def get_cash_bonus(self, year):
        # Assuming the cash bonus is received every December
        return self.cash_bonus if year == self.year_assigned else 0

    def get_rsu_payment(self, year, month):
        # Assuming RSUs pay out 1/6th in June and December, starting the year after they're assigned
        if year > self.year_assigned and month in [6, 12]:
            return self.rsu_value / 6
        return 0

    def calculate_upcoming_rsu_payouts(self):
        # This method assumes RSUs pay out 1/6th in June and December, starting the year after they're assigned
        if self.bonus_type != 'rsu':
            return []

        payouts = []
        current_year = datetime.now().year
        current_month = datetime.now().month
        payouts_remaining = 6  # Total number of payouts for RSUs

        # Calculate the payouts starting from the June following the assignment year
        for year in range(self.year_assigned + 1, self.year_assigned + 10):
            for month in [6, 12]:
                if year > current_year or (year == current_year and month >= current_month):
                    payouts.append({
                        'year': year,
                        'month': month,
                        'amount': self.amount / 6
                    })
                    payouts_remaining -= 1
                    if payouts_remaining == 0:
                        return payouts  # Stop after 6 payouts
        return payouts

    @staticmethod
    def find_all_rsu_payments():
        return BonusPayment.query.filter_by(bonus_type='rsu').all()