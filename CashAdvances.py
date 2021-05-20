import Parameters
import random

def advances_payment(banks, CB, gov):
    for bank in banks:
        interest = bank.cash_advances*Parameters.CB_r_advances
        assert interest >= - Parameters.Precision
        interest = max(0, interest)
        
        repayment = bank.cash_advances
        assert repayment >= - Parameters.Precision
        repayment = max(0, repayment)
        
        amount = interest + repayment
        
        gov.reserves += interest
        gov.cash_advances_payment += interest
        
        bank.reserves -= amount
        bank.interests_on_cash_transfers = interest
        
        CB.cash_advances -= bank.cash_advances
        bank.cash_advances = 0
    
    assert abs(CB.cash_advances) <= 0.1
    CB.cash_advances = 0

def advances_requests(banks, CB):
    random.shuffle(banks)
    demand_banks = []
    
    for bank in banks:
        if bank.liquidity_ratio != 'no deposits' and bank.cash_demand > 0:
            demand_banks.append(bank)
            
    for bank in demand_banks:
        bank.cash_advances = bank.cash_demand
        bank.reserves += bank.cash_advances
        CB.cash_advances += bank.cash_advances