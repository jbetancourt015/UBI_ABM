import Parameters
import random
import numpy as np
import Statistics
import Transaction

N_partners = Parameters.N_partners_C_market
e_C = Parameters.Choice_intensity_C_market

#Expectations function
def expectation(actual, exp=None):
    phi = Parameters.Adaptative_expectations
    if exp==None:
        exp = actual
    return phi*exp + (1-phi)*actual

#Households choose their supplier
def matching_and_transactions(households, Cfirms, data):
    data['aggregates']['Y_cons'] = 0
    data['aggregates']['Y_cons_r'] = 0

    for firm in Cfirms:
        firm.revenue = 0
        firm.sales = 0
        
    random.shuffle(households)
    
    for household in households:
        opt = []
        random.shuffle(Cfirms)
        
        for firm in Cfirms:
            if firm != household.old_supplier:
                opt.append(firm)
            if len(opt) == N_partners:
                break
        
        options = []
        
        for firm in opt:
            options.append([firm.price, firm])
        
        options.sort(key=lambda x: int(x[0]),reverse = True)
        
        quantities = 0
        while quantities == 0:
            new_supplier_list = options.pop()
            new_supplier = new_supplier_list[1]
            quantities = new_supplier.inventories
            if len(options) == 0:
                if quantities == 0:
                    new_supplier = None
                break
        
        if household.old_supplier.inventories > 0:
            if new_supplier != None:
                diff = new_supplier.price/household.old_supplier.price - 1
                if diff < 0:
                    p_switch = 1 - np.exp(e_C*diff)
                    switch = np.random.choice([0,1],p=[1-p_switch,p_switch])
                    if switch == 1:
                        supplier = new_supplier
                    else:
                        supplier = household.old_supplier
                else:
                    supplier = household.old_supplier
            else:
                supplier = household.old_supplier
        else:
            if new_supplier != None:
                supplier = new_supplier
            else:
                supplier = None

        if supplier != None:
            household.last_price = supplier.price
            consumption = min(household.desired_consumption,
                              household.deposits/supplier.price,
                              supplier.inventories)
            assert consumption >= - Parameters.Precision
            consumption = max(0, consumption)
            assert supplier.price > 0
            
            amount = consumption*supplier.price
            if household.deposits - amount >= - Parameters.Precision:
                amount = min(amount, household.deposits)
            amount = Transaction.transaction(amount, payer = household, receiver = supplier, output = True)
            
            supplier.inventories -= consumption
            assert firm.inventories >= - Parameters.Precision
            firm.inventories = max(0, firm.inventories)
            supplier.sales += consumption
            supplier.revenue += amount
            
            assert household.deposits >= - Parameters.Precision
            household.deposits = max(0, household.deposits)
            
            residual = household.desired_consumption - consumption
            assert residual >= - Parameters.Precision
            residual = max(0, residual)
            
            residual = max(0, residual)
            data['aggregates']['Y_cons'] += amount
            data['aggregates']['Y_cons_r'] += consumption
            
            if residual > 0 and household.deposits > 0:
                if household.old_supplier!=supplier and household.old_supplier.inventories>0:
                    options.append([household.old_supplier.price,household.old_supplier])
                    options.sort(key=lambda x: int(x[0]))
                    for firm_list in options:
                        firm = firm_list[1]
                        
                        consumption = min(residual, household.deposits/firm.price,
                                          firm.inventories)
                        assert consumption >= - Parameters.Precision
                        consumption = max(0, consumption)
                        
                        if consumption > 0:
                            residual -= consumption
                            assert residual >= 0
                            assert firm.price > 0
                            
                            amount = consumption*firm.price
                            if household.deposits - amount >= - Parameters.Precision:
                                amount = min(amount, household.deposits)
                            amount = Transaction.transaction(amount, payer = household, receiver = firm, output = True)
                            
                            consumption = amount/firm.price
                            assert consumption >= - Parameters.Precision
                            consumption = max(0, consumption)
                            
                            firm.inventories -= consumption
                            assert firm.inventories >= - Parameters.Precision
                            firm.inventories = max(0, firm.inventories)
                            firm.sales += consumption
                            firm.revenue += amount
                            
                            assert household.deposits >= - Parameters.Precision
                            household.deposits = max(0, household.deposits)

                            data['aggregates']['Y_cons'] += amount
                            data['aggregates']['Y_cons_r'] += consumption
                        
                        if household.deposits == 0 or residual == 0:
                            break
            
            household.old_supplier = supplier
        
        assert household.deposits >= - Parameters.Precision
        household.deposits = max(0, household.deposits)

    Statistics.C_nominal_output(data)
    Statistics.consumer_price_index(data)
    Statistics.C_real_output(data) 
            


















