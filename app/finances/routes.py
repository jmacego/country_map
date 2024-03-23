from flask import Flask, jsonify, render_template, request, Blueprint, redirect, url_for, session, make_response, session, current_app, abort
from datetime import datetime

from ..models.finances import Mortgage, BonusPayment, Savings
from ..models.auth import require_email_authorization

from app.finances import bp


@bp.route('/mortgages')
@require_email_authorization
def mortgage():
    return render_template('finances/mortgages.html', title='Mortgage Details')

@bp.route('/savings')
@require_email_authorization
def savings():
    return render_template('finances/savings.html', title='Savings Details')

@bp.route('/api/mortgage', methods=['GET'])
def get_mortgages():
    mortgages = Mortgage.get_all()
    mortgages_list = []
    for mortgage in mortgages:
        mortgage_dict = mortgage.to_dict()  # Assuming a to_dict() method exists
        # Add the monthly payment details to the dictionary
        monthly_payment = mortgage.calculate_monthly_payment()
        mortgage_dict['monthly_payment'] = monthly_payment
        mortgages_list.append(mortgage_dict)
    return jsonify(mortgages_list)

@bp.route('/api/mortgage/<int:mortgage_id>', methods=['GET'])
def get_mortgage(mortgage_id):
    mortgage = Mortgage.get_by_id(mortgage_id)
    if mortgage:
        return jsonify(mortgage.to_dict())  # Assuming a to_dict() method exists
    else:
        abort(404, description="Mortgage details not found.")

@bp.route('/api/mortgage', methods=['POST'])
def create_mortgage():
    data = request.get_json()
    new_mortgage = Mortgage.create_from_json(data)
    if new_mortgage:
        return jsonify(new_mortgage.to_dict()), 201
    else:
        abort(400, description="Error creating mortgage.")

@bp.route('/api/mortgage/<int:mortgage_id>', methods=['PUT'])
def update_mortgage(mortgage_id):
    data = request.get_json()
    mortgage = Mortgage.update_by_id(mortgage_id, data)
    if mortgage:
        return jsonify(mortgage.to_dict())
    else:
        abort(404, description="Mortgage details not found.")

@bp.route('/api/mortgage/<int:mortgage_id>', methods=['DELETE'])
def delete_mortgage(mortgage_id):
    if Mortgage.delete_by_id(mortgage_id):
        return jsonify({"status": "success", "message": "Mortgage details deleted."})
    else:
        abort(404, description="Mortgage details not found.")

@bp.route('/api/bonus_payment', methods=['POST'])
def create_bonus_payment():
    data = request.get_json()
    bonus_type = data.get('bonus_type')
    amount = data.get('amount')
    payment_date = datetime.strptime(data.get('payment_date'), '%Y-%m-%d')
    year_assigned = data.get('year_assigned')
    bonus_payment = BonusPayment.add_bonus_payment(bonus_type, amount, payment_date, year_assigned)
    return {'id': bonus_payment.id, 'message': 'Bonus payment added successfully'}, 201

@bp.route('/api/aggregated_rsu_payouts', methods=['GET'])
def get_aggregated_rsu_payouts():
    rsu_payments = BonusPayment.query.filter_by(bonus_type='rsu').all()
    all_upcoming_payouts = []
    for rsu_payment in rsu_payments:
        all_upcoming_payouts.extend(rsu_payment.calculate_upcoming_rsu_payouts())
    
    # Aggregate payouts by month using a standard dictionary
    payouts_by_month = {}
    for payout in all_upcoming_payouts:
        key = (payout['year'], payout['month'])
        if key in payouts_by_month:
            payouts_by_month[key] += payout['amount']
        else:
            payouts_by_month[key] = payout['amount']
    
    # Convert the dictionary to a sorted list of dictionaries
    aggregated_payouts = sorted(
        [{'year': year, 'month': month, 'amount': amount}
         for (year, month), amount in payouts_by_month.items()],
        key=lambda x: (x['year'], x['month'])
    )
    
    return jsonify(aggregated_payouts)

@bp.route('/api/savings', methods=['POST'])
@require_email_authorization
def create_savings():
    data = request.get_json()
    new_savings = Savings.create(balance=data['balance'])
    return jsonify(new_savings.to_dict()), 201

@bp.route('/api/savings/latest', methods=['GET'])
@require_email_authorization
def get_latest_savings():
    latest_savings = Savings.get_latest()
    if latest_savings:
        return jsonify(latest_savings.to_dict())
    else:
        return jsonify({'error': 'No savings account data found.'}), 404

@bp.route('/api/savings', methods=['GET'])
@require_email_authorization
def get_savings():
    all_savings = Savings.get_all()
    return jsonify([savings.to_dict() for savings in all_savings])

@bp.route('/api/savings/<int:savings_id>', methods=['PUT'])
@require_email_authorization
def update_savings(savings_id):
    data = request.get_json()
    savings = Savings.update(savings_id, balance=data['balance'])
    if savings:
        return jsonify(savings.to_dict())
    else:
        return jsonify({'error': 'Savings entry not found.'}), 404

@bp.route('/api/savings/<int:savings_id>', methods=['DELETE'])
@require_email_authorization
def delete_savings(savings_id):
    if Savings.delete(savings_id):
        return jsonify({'message': 'Savings entry deleted.'}), 200
    else:
        return jsonify({'error': 'Savings entry not found.'}), 404


@bp.route('/clearall')
def clear_all():
    Mortgage.clear_and_load('instance/finances.json')
    return jsonify({"status": "success", "message": "Mortgage details have been reset."})