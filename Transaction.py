import Parameters
import Households
import KFirms
import CFirms
import Banks
import Government

def transaction(amount, payer, receiver, output = True):
    """
    

    Parameters
    ----------
    amount : float
        DESCRIPTION.
    output : The default is True.

    Returns
    -------
    amount : float

        This function allows for transactions were the payer and/or the reciever
        is nor a bank, nor the government, nor the commercial bank.

    """
    
    assert amount >= - Parameters.Precision
    amount = max(0, amount)
    
    # Transactions 1, 3:
    if ((type(payer) == Households.Household or type(payer) == KFirms.KFirm or type(payer) == CFirms.CFirm)
        and (type(receiver) == Households.Household or type(receiver) == KFirms.KFirm or type(receiver) == CFirms.CFirm)):
        
        assert amount >= 0
        assert amount <= payer.deposits
        
        payer.deposits -= amount
        assert payer.deposits >= 0
        payer.deposits_bank.reserves -= amount
        
        receiver.deposits += amount
        assert receiver.deposits >= 0
        receiver.deposits_bank.reserves += amount
    
    
    elif ((type(payer) == Banks.Bank or type(payer) == Government.Gov)
        and (type(receiver) == Households.Household or type(receiver) == KFirms.KFirm or type(receiver) == CFirms.CFirm)):
        
        payer.reserves -= amount
        
        receiver.deposits += amount
        assert receiver.deposits >= 0
        receiver.deposits_bank.reserves += amount

    
    elif ((type(payer) == Households.Household or type(payer) == KFirms.KFirm or type(payer) == CFirms.CFirm)
        and (type(receiver) == Banks.Bank or type(receiver) == Government.Gov)):
        
        assert amount >= 0
        assert amount <= payer.deposits
        
        payer.deposits -= amount
        assert payer.deposits >= 0
        payer.deposits_bank.reserves -= amount
        
        receiver.reserves += amount
    

    elif ((type(payer) != Households.Household and type(payer) != KFirms.KFirm and type(payer) != CFirms.CFirm) 
          and (type(receiver) != Households.Household and type(receiver) != KFirms.KFirm and type(receiver) != CFirms.CFirm)):
        print("incorrect input")
        assert True == False
    

    if output == True:
        return amount