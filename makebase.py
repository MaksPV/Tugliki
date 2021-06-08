import pickle
import time


def save_file(var, name_file):
    with open((name_file + '.pickle'), 'wb') as f:
        pickle.dump(var, f)
    f.close()
    with open(('backup/' + name_file + '_backup.pickle'), 'wb') as f:
        pickle.dump(var, f)
    f.close()


def save_wallets(w, name="wallets"):
    dict_wallets = dict()
    for k in w:
        dict_wallets[k] = w[k].get_dict()
    save_file(dict_wallets, name)


wallets = dict()
codes = dict()


class Wallet():
    def __init__(self, user_id, balance=0, is_rezerv=False):
        self.balance = balance
        self.user_id = user_id
        if is_rezerv:
            self.adrees = user_id
        else:
            self.adrees = get_wallet_adrees(user_id)
        self.zhur = []
        self.last_farm = time.time()
        self.sum_farm = 0
        self.allow_delete = True
    
    def add(self, from_, n):
        self.balance += n
        if from_.adrees != "rezerv":
            self.zhur.append(("Пополнение", from_.adrees, n))
    
    def send(self, to_, n):
#        global block
        self.balance -= n
        to_.add(self, n)
        if self.adrees != "rezerv":
            self.zhur.append(("Перевод", to_.adrees, n))
#        block.append(("Перевод", self.adrees, to_.adrees, n))
#        check_block()
    
    def get_dict(self):
        return self.__dict__
 
wallets["rezerv"] = Wallet("rezerv", 10000, True)
wallets["code"] = Wallet("code", 0, True)

save_wallets(wallets)
save_wallets(codes, "codes")
