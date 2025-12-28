# БАНКОВСКИЕ РЕСУРСЫ ПРОВАЙДЕРА GAREX
from typing import Dict


class BankResources:
    BANKS_RUS: Dict[str, str] = {
        "Сбер": "sber",
        "Т-банк": "t-bank",
        "Альфа-банк": "alfa-bank",
        "Юнистрим": "unistream",
        "Ренессанс": "renessans",
        "Яндекс банк": "yandex-bank",
        "ОТП Банк": "otp-bank",
        "Ингосстрах Банк": "ingosstrah",
        "Московский кредитный банк": "mkb",
        "Банк Приморье": "primore",
        "АК Барс Банк": "ak-bars",
        "Уралсиб": "uralsib",
        "Азиатско-Тихоокеанский Банк (АТБ)": "atb",
        "ВТБ": "vtb",
        "Газпромбанк": "gazprombank",
        "Совкомбанк": "sovcombank",
        "Промсвязьбанк (ПСБ)": "psbank",
        "МТС-деньги (Экси-банк)": "mtsdengi",
        "Почта Банк": "pochtabank",
        "Ozon Банк": "ozonbank",
        "Банк Пойдём": "poidem",
        "Банк Левобережный": "nskbl",
        "Вайлдберриз Банк": "wb-bank",
        "Райффайзен Банк": "raiffeisen",
        "БКС Банк": "bks-bank",
        "МТС Банк": "mts-bank",
        "ЭЛПЛАТ": "el-plat",
        "Россельхозбанк": "rshb",
        "АБ РОССИЯ": "abr",
        "КБ СОЛИДАРНОСТЬ": "solid",
        "КБ ДОЛИНСК": "dolinskbank",
        "Центр-инвест": "centrinvest",
        "ЧЕЛЯБИНВЕСТБАНК": "chelinvest",
        "Банк Русский Стандарт": "rsb",
        "Банк ЗЕНИТ": "zenit",
        "KWIKPAY": "kwikpay",
        "СДМ-Банк": "sdm-bank",
        "Открытие": "open",
        "Банк Авангард": "avangard",
        "РНКБ": "rncb",
        "Росбанк": "rosbank",
        "Хоумбанк": "homebank",
        "Примсоцбанк": "pskb",
        "Банк Хлынов": "bank-hlynov",
        "Банк Кузнецкий": "kuzbank",
        "ББР Банк": "bbr",
        "Транскапитал": "tkbbank",
        "Рокетбанк": "rocketbank",
        "Кошелек ЦУПИС": "cupis",
        "ЮMoney": "yoomoney",
        "Фора-банк": "forabank",
        "ДОМ.РФ": "domrfbank",
        "Банк Эсхата": "eskhata",
        "Международный банк Таджикистана": "ibt",
        "Банк Арванд": "arvand",
        "Ориёнбонк": "oriyonbonk",
        "Тавхидбанк": "tawhidbank",
        "Душанбе Сити": "dc_tj",
        "Qplus (Евроальянс банк)": "qplus"
    }
    BANKS_ABH: Dict[str, str] = {
        "Амра-банк (Абхазия)": "amra-bank",
        "А-Мобаил (Абхазия)": "a-mobile"
    }
    BANKS_TJS: Dict[str, str] = {
        "Амонатбанк (Таджикистан)": "amonatbank",
        "Алиф Банк (Таджикистан)": "alif-bank",
        "Душанбе Сити": "dc_tj",
        "Тавхидбанк": "tawhidbank",
        "Ориёнбонк": "oriyonbonk",
        "Банк Арванд": "arvand",
        "Международный банк Таджикистана": "ibt",
        "Банк Эсхата": "eskhata"
    }
    BANKS_AZN: Dict[str, str] = {
        "Kapital Bank": "kapitalbank-az",
        "Premium bank": "premiumbank-az",
        "Unibank": "unibank-az",
        "m10": "m10"
    }
    SIM_RUS: Dict[str, str] = {
        "МТС": "mts",
        "Билайн": "beeline",
        "МегаФон": "megafon",
        "Tele2": "t2"
    }


bank_res = BankResources
