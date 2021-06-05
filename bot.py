import hashlib
import telebot
import pickle
import time
import random

wallets = dict()
codes = dict()
block = []
bot = telebot.TeleBot("TOKEN")
chanel_id = -1001303239825


def read_file(name_file):
    with open((name_file + '.pickle'), 'rb') as f:
        a = pickle.load(f)
    f.close()
    return a


def save_file(var, name_file):
    with open((name_file + '.pickle'), 'wb') as f:
        pickle.dump(var, f)
    f.close()
    with open(('backup/' + name_file + '_backup.pickle'), 'wb') as f:
        pickle.dump(var, f)
    f.close()


def mega_hash(stringa):
    sha = hashlib.sha256()
    sha.update(str(stringa).encode('utf-8'))
    hash_ = sha.hexdigest()
    return hash_


def check_block():
    global block
    if len(block) == 25:
        bot.send_message(chanel_id, "\n".join([" ".join([str(j) for j in i]) for i in block]) )
        block = [(mega_hash(block))]
    save_file(block, "block")
 
       
def get_wallet_adrees(n):
        shaa = hashlib.md5()
        shaa.update(str(n).encode('utf-8'))
        return shaa.hexdigest()


def random_posled(n):
    return "".join([random.choice(tuple("abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")) for _ in range(n)])


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


class Code:
    def __init__(self, from_, n, password):
        self.n = n
        sha_ = hashlib.md5()
        sha_.update((str(n) + str(from_.adrees) + random_posled(12)).encode('utf-8'))
        self.code = sha_.hexdigest()
        sha = hashlib.sha256()
        sha.update(password.encode('utf-8'))
        self.password = sha.hexdigest()
        self.owner = from_.adrees
        self.is_active = True
        from_.send(wallets["code"], n)
    
    def get_dict(self):
        return self.__dict__


def save_wallets(w, name="wallets"):
    dict_wallets = dict()
    for k in w:
        dict_wallets[k] = w[k].get_dict()
    save_file(dict_wallets, name)


def load_wallets(name="wallets"):
    a = read_file(name)
    w = dict()
    for k in a:
        b = Wallet(0)
        for i in a[k]:
            b.__dict__[i] = a[k][i]
        w[k] = b
    return w

wallets["rezerv"] = Wallet("rezerv", 10000, True)
wallets["code"] = Wallet("code", 0, True)

# save_wallets(codes, "codes")

if True:
    wallets = load_wallets()
    block = read_file("block")
    codes = load_wallets("codes")
else:
    print(wallets)
    save_wallets(wallets)
    save_file(block, "block")
    save_file(codes, "codes")
# wallets["code"] = Wallet("code", 0, True)

def send_message(*args, **kwargs):
    try:
        bot.send_message(*args, **kwargs)
    except:
        pass


@bot.message_handler(commands=["info"])
def info(message):
    rezerv = wallets["rezerv"] 
    user_wallet = wallets[get_wallet_adrees(message.chat.id)]
    message_text = """Принимать ты можешь на этот адрес: `{}`
Цена за один фарм: {}
всего сейчас в резерве: {}
1 туглик стоит {} рублей
твой баланс сейчас: {}""".format(user_wallet.adrees,
                                 round((2/3) ** (19 - (rezerv.balance // 500)), 5),
                                 round(rezerv.balance, 5),
                                 round(0.0043895747599451305 * 1.5 ** (19 - (rezerv.balance // 500)), 5),
                                 round(user_wallet.balance, 5))
    send_message(message.chat.id, message_text, parse_mode="Markdown")


@bot.message_handler(commands=["start"])
def start(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('/info', '/farm')
    
    if get_wallet_adrees(message.chat.id) not in wallets.keys():
        user_wallet = Wallet(message.chat.id)
        wallets[user_wallet.adrees] = user_wallet
        
    save_wallets(wallets)
    send_message(message.chat.id, """
Это бот представляет собой типа блокчейн систему  криптовалюты
Всего будет выпущено 10000 тугликов
Каждые 500 тугликов вознаграждение уменьшается вполтора раза
все туглики, отправленные не по тем адресам улетают в резерв
отправлять с помощью команды /send (адрес кошелька другого человека) (количество монет)
фармить командой /farm
""", reply_markup=keyboard)
    info(message)


@bot.message_handler(commands=["send"])
def send(message):
    try:
        a = message.text.split()
        to_, n = a[1], float(a[2])
    except:
        send_message(message.chat.id, "Что-то ввёл некорректно")
        return None
    
    my_wallet = wallets[get_wallet_adrees(message.chat.id)]
    if to_ in wallets.keys():
        to_wallet = wallets[to_]
    else:
        to_wallet = wallets["rezerv"]
    if 0 <= n <= my_wallet.balance:
        my_wallet.send(to_wallet, n)
        send_message(my_wallet.user_id, "Успешно")
        send_message(to_wallet.user_id, "Пришёл перевод на сумму {} от `{}`".format(n, my_wallet.adrees), parse_mode="Markdown")
    else:
        send_message(message.chat.id, "Сумма не та")
    save_wallets(wallets)


@bot.message_handler(commands=["farm"])
def farm(message):
    rezerv = wallets["rezerv"]
    if rezerv.balance <= 0:
        send_message(message.chat.id, "Денег нема")
    else:
        my_wallet = wallets[get_wallet_adrees(message.chat.id)]
        n = (2/3) ** (19 - (rezerv.balance // 500))
        try:
            if time.time() - my_wallet.last_farm <= (10/60):
                my_wallet.sum_farm += n
        except:
            my_wallet.sum_farm = n
            my_wallet.last_farm = time.time() 
        
        rezerv.send(my_wallet, n)
         
        
        if my_wallet.allow_delete:
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except:
                pass
        elif time.time() - my_wallet.last_farm > 1:
            send_message(my_wallet.user_id, "Нафармил {} туглика".format(round(my_wallet.sum_farm, 4)))
            my_wallet.sum_farm = n
        my_wallet.last_farm = time.time()
        
    save_wallets(wallets)


@bot.message_handler(commands=["log"])
def log(message):
#    send_message(message.chat.id, "по техпричинам не работает")
    my_wallet = wallets[get_wallet_adrees(message.chat.id)]
    log = reversed(my_wallet.zhur[:50])
    log = [" ".join([str(j) for j in i]) for i in log]
    log = "\n".join(log)
    if log == "":
        log = "История пуста"
    send_message(message.chat.id, log)
#    bot.send_message(message.chat.id, "\n".join([" ".join([str(j) for j in my_wallet.zhur[-1*i]]) for i in range(50)]))


@bot.message_handler(commands=["allow_log"])
def allow_log(message):
    my_wallet = wallets[get_wallet_adrees(message.chat.id)]
    if my_wallet.allow_delete is False:
        my_wallet.allow_delete = True
        send_message(message.chat.id, "Выключена отправка сообщений о фарме и включено удаление сообщений")
    else:
        my_wallet.allow_delete = False
        send_message(message.chat.id, "Включена отправка сообщений о фарме и выключено удаление сообщений")
    save_wallets(wallets)


@bot.message_handler(commands=["disable_key"])
def key_dis(message):
    send_message(message.chat.id, "клава убрана", reply_markup=telebot.types.ReplyKeyboardRemove())


@bot.message_handler(commands=["make_code"])
def make_code(message):
    try:
        a = message.text.split()
        n = float(a[1])
    except:
        send_message(message.chat.id, "Что-то ввёл некоректно\nправильно /make_code количество_тугликов")
        return None
    
    my_wallet = wallets[get_wallet_adrees(message.chat.id)]
    
    if 0 <= n <= my_wallet.balance:
        ps = random_posled(12)
        a = Code(my_wallet, n, ps)
        codes[a.code] = a
        send_message(message.chat.id, "Код: {}\nПароль: {}\nСохраните код и пароль!".format(a.code, ps))
        save_wallets(codes, "codes")
    else:
        send_message(message.chat.id, "Неверная сумма")


@bot.message_handler(commands=["get_code"])
def get_code(message):
    try:
        a = message.text.split()
        login = a[1]
        try:
            password = a[2]
        except:
            password = ""
    except:
        send_message(message.chat.id, "Что-то ввёл некоректно\nправильно /get_code код пароль(необязательно)")
        return None
    
    if login not in codes:
        send_message(message.chat.id, "Нет такого кода")
    else:
        code_ = codes[login]
        message_text = """
Информация об этом коде:

Активный: {}
Адрес кода: `{}`
Количество тугликов: {}
Создатель: `{}`""".format(code_.is_active, code_.code, code_.n, code_.owner)
        send_message(message.chat.id, message_text, parse_mode="Markdown")
        sha = hashlib.sha256()
        sha.update(password.encode('utf-8'))
        password_hash = sha.hexdigest()
        if password_hash == code_.password and code_.is_active:
            my_wallet = wallets[get_wallet_adrees(message.chat.id)]
            wallets["code"].send(my_wallet, code_.n)
            code_.is_active = False
            save_wallets(wallets)
            save_wallets(codes, "codes")
            send_message(message.chat.id, "Код подучен")
        else:
            send_message(message.chat.id, "Неверный пароль или код недействителен")


@bot.message_handler(commands=["admin_info"])
def hh(message):
    try:
        a = message.text.split()
        b = wallets[a[1]]
        dicr = b.__dict__.copy()
    #    dicr["zhur"] = "..."
        send_message(message.chat.id, str(dicr))
    except:
        pass


bot.polling()
