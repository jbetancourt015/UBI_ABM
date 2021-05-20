import Parameters
import random

def bonds_payment(banks, CB, gov):
    for bank in banks:
        interest = Parameters.Bonds_price*bank.bonds*Parameters.Gov_r_bonds
        assert interest >= - Parameters.Precision
        interest = max(0, interest)
        
        repayment = Parameters.Bonds_price*bank.bonds
        assert repayment >= - Parameters.Precision
        repayment = max(0, repayment)
        
        amount = interest + repayment
        gov.reserves -= amount
        gov.bond_payment += interest
        gov.bonds -= bank.bonds
        
        bank.reserves += amount
        bank.interests_on_bonds = interest
        bank.bonds = 0
    
    
    repayment = CB.bonds*Parameters.Bonds_price
    assert repayment >= - Parameters.Precision
    repayment = max(0, repayment)
    
    gov.reserves -= repayment
    gov.bonds -= CB.bonds
    CB.bonds = 0
    
    assert abs(gov.bonds) <= Parameters.Precision
    gov.bonds = 0

def bonds_buying(gov, CB, banks):
    random.shuffle(banks)
    demand_banks = []
    
    for bank in banks:
        if bank.liquidity_ratio != 'no deposits' and bank.bond_demand > 0:
            demand_banks.append(bank)
    
    bonds_remaining = gov.bonds
    
    for bank in demand_banks:
        bank.bonds = min(bonds_remaining, bank.bond_demand)
        assert bank.bonds >= 0
        
        bank.reserves -= bank.bonds*Parameters.Bonds_price
        gov.reserves += bank.bonds*Parameters.Bonds_price
        
        bonds_remaining -= bank.bonds
        assert bonds_remaining >= - Parameters.Precision
        bonds_remaining = max(0, bonds_remaining)
    
    if bonds_remaining > 0:
        CB.bonds = bonds_remaining
        assert CB.bonds > 0
        gov.reserves += CB.bonds*Parameters.Bonds_price
                