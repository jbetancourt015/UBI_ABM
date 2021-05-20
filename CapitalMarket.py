import Parameters
import random
import numpy as np
import Statistics
import Transaction

#C firms choose their K supplier
def matching(Kfirms, Cfirms):
    random.shuffle(Cfirms)
    N_partners = Parameters.N_partners_K_market
    e_K = Parameters.Choice_intensity_K_market
    
    for cfirm in Cfirms:
        if cfirm.K_demand > 0:
            cfirm.supplier_list = []
            opt = []
            random.shuffle(Kfirms)
            
            for kfirm in Kfirms:
                if kfirm != cfirm.old_supplier:
                    opt.append(kfirm)
                if len(opt)==N_partners:
                    break
            
            options = []
            for kfirm in opt:
                options.append([kfirm.price,kfirm])
            options.sort(key=lambda x: int(x[0]),reverse=True)
            
            new_supplier_list = options.pop()
            new_supplier = new_supplier_list[1]
            
            while new_supplier.preliminary_inventories <= 0:
                try:
                    new_supplier_list = options.pop()
                except IndexError:
                    new_supplier = None
                    break
                else:
                    new_supplier = new_supplier_list[1]
            
            if cfirm.old_supplier.preliminary_inventories > 0:
                if new_supplier != None:
                    diff = new_supplier.price/cfirm.old_supplier.price-1
                    if diff < 0:
                        p_switch = 1 - np.exp(e_K*diff)
                        switch = np.random.choice([0,1],p=[1-p_switch,p_switch])
                        if switch == 1:
                            cfirm.supplier_list.append([new_supplier])
                        else:
                            cfirm.supplier_list.append([cfirm.old_supplier])
                    else:
                        cfirm.supplier_list.append([cfirm.old_supplier])
                else:
                    cfirm.supplier_list.append([cfirm.old_supplier])
            else:
                if new_supplier != None:
                    cfirm.supplier_list.append([new_supplier])
                else:
                    cfirm.supplier_list = None
            
            if cfirm.supplier_list != None:
                if cfirm.supplier_list[0][0].preliminary_inventories < cfirm.K_demand:
                    cfirm.supplier_list[0].append(cfirm.supplier_list[0][0].preliminary_inventories)
                    cfirm.supplier_list[0][0].preliminary_inventories = 0
                    residual_demand = cfirm.K_demand - cfirm.supplier_list[0][0].preliminary_inventories
                    assert residual_demand >= - Parameters.Precision
                    residual_demand = max(0, residual_demand)
                    
                    if cfirm.old_supplier.preliminary_inventories and cfirm.old_supplier!=cfirm.supplier_list[0][0]:
                        options.append([cfirm.old_supplier.price,cfirm.old_supplier])
                        options.sort(key=lambda x: int(x[0]),reverse=True)
                    
                    while residual_demand > 0:
                        try:
                            new_supplier_list = options.pop()
                        except IndexError:
                            break
                        else:
                            new_supplier = new_supplier_list[1]
                            if new_supplier.preliminary_inventories >= residual_demand:
                                cfirm.supplier_list.append([new_supplier,residual_demand])
                                new_supplier.preliminary_inventories -= residual_demand
                                residual_demand = 0
                            elif new_supplier.preliminary_inventories > 0:
                                cfirm.supplier_list.append([new_supplier,new_supplier.preliminary_inventories])
                                new_supplier.preliminary_inventories = 0
                                residual_demand -= new_supplier.preliminary_inventories
                                assert residual_demand >= - Parameters.Precision
                                residual_demand = max(0, residual_demand)
                else:
                    cfirm.supplier_list[0][0].preliminary_inventories -= cfirm.K_demand
                    cfirm.supplier_list[0].append(cfirm.K_demand)

#C firms purchase from K firms
def purchase(Kfirms, Cfirms, data):
    data['aggregates']['Y_cap'] = 0
    data['aggregates']['Y_cap_r'] = 0
    data['aggregates']['available_deposits'] = 0

    for kfirm in Kfirms:
        kfirm.revenue = 0
        kfirm.sales = 0
    
    random.shuffle(Cfirms)
    
    for cfirm in Cfirms:
        K_bought = 0
        
        if cfirm.supplier_list != None:
            assert cfirm.deposits >= - Parameters.Precision
            cfirm.deposits = max(0, cfirm.deposits)
            available_deposits = max(0, cfirm.deposits + cfirm.exp_OCF)
            data['aggregates']['available_deposits'] += available_deposits

            for element in cfirm.supplier_list:
                assert element[0].inventories >= - Parameters.Precision
                element[0].inventories = max(0, element[0].inventories)
                assert element[0].price > 0
                units = min(element[1], available_deposits/element[0].price,
                            element[0].inventories)
                assert units >= - Parameters.Precision
                units = max(0, units)
                
                if units > 0:
                    amount = units*element[0].price
                    if cfirm.deposits - amount >= - Parameters.Precision:
                        amount = min(amount, cfirm.deposits)
                    amount = Transaction.transaction(amount, payer = cfirm, receiver = element[0], output = True)
                    available_deposits -= amount
                    
                    element[0].inventories -= units
                    assert element[0].inventories >= - Parameters.Precision
                    element[0].inventories = max(0, element[0].inventories)
                    
                    element[0].sales += units
                    
                    cfirm.K_sheet.append([units,0,element[0].price,
                                          units*element[0].price,element[0]])
                    K_bought += units
                    data['aggregates']['Y_cap'] += amount
                    data['aggregates']['Y_cap_r'] += units
                    
                assert available_deposits >= - Parameters.Precision
                available_deposits = max(0, available_deposits)
                    
                if available_deposits == 0:
                    break
        
        cfirm.supplier_list = None
        assert cfirm.deposits >= - Parameters.Precision
        cfirm.deposits = max(0, cfirm.deposits)

    Statistics.K_nominal_output(data)
    Statistics.producer_price_index(data)
    Statistics.K_real_output(data)
    data['Available_deposits'].append(data['aggregates']['available_deposits'])
                    
























                