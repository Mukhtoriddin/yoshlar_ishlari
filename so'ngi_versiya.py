import random
import time
import openpyxl
import logging as log
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


log.basicConfig(level=log.DEBUG, filename="logs.txt")

# PWD: 49529617


buttons = {
    "So‘rovnoma qo‘shish": "/html/body/div/div[1]/div[2]/div/div[1]/div/div[1]/div/div[2]/div/button",
    "Qidirish": "/html/body/div[1]/div[1]/div[2]/div/div[3]/div/div/section/div/form/button",
    "Saqlash va kirish": "/html/body/div[1]/div[1]/div[2]/div/div[3]/div/div/section/div/form/div[9]/button",
    "So‘rovnoma yopish": "/html/body/div[1]/div[1]/div[2]/div/div[3]/div/div/header/button",
    "Yakunlash tugmasi": "/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[12]/button",
    "Saqlash": "/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[1]/form/div[2]/button",
    "Unknown 1": "/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[1]/div[2]/div/button"
}

inputs = {
    "Pasport": "/html/body/div[1]/div[1]/div[2]/div/div[3]/div/div/section/div/form/div[2]/div/div[1]/input",
    "Tug‘ilgan sana": "/html/body/div[1]/div[1]/div[2]/div/div[3]/div/div/section/div/form/div[3]/div/input",
    "Kocha": "/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[1]/form/div[1]/div[1]/div[3]/div[7]/div/div/div/div[1]/input",
    "Uy raqami": "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/"
                 "div[1]/form/div[1]/div[1]/div[3]/div[8]/div/div/div/input",
    "Telefon": "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/"
               "div[1]/form/div[1]/div[1]/div[3]/div[9]/div/div/div[1]/input"
}

options = {
    "Soy yoli": "/html/body/div[2]/div[1]/div[1]/ul/li[1]"
}

checkers = {
    "Fuqaro qo‘shish": "/html/body/div[1]/div[1]/div[2]/div/div[3]/div/div",
    "Qidirish xatoligi": "//*[@id=\"app\"]/div[1]/div[2]/div/div[3]/div/div/section/div/form/div[9]/p",
    "Qidirish xatoligi 1": "/html/body/div[3]/p"
}


class Web:
    def __init__(self):
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        self.driver.maximize_window()
        self.driver.get("https://yoshlarbalansi.uz/")

        self.wb = openpyxl.load_workbook('q.xlsx')
        self.sheet = self.wb["рўйхат"]
        self.working_on = 0

    def pass_if_exists(self, by, value):
        WebDriverWait(self.driver, 10).until_not(
            EC.invisibility_of_element_located((by, value))
        )

    def pass_if_non_exists(self, by, value):
        WebDriverWait(self.driver, 10).until(
            EC.invisibility_of_element_located((by, value))
        )

    def execute_if_exists(self, by, value, func, num):
        for i in range(num):
            if EC.visibility_of_element_located((by, value)):
                func()
        return False

    def execute_if_value_equals(self, by, value, func, num, value2):
        for i in range(num):
            try:
                val = " ".join(self.driver.find_element(by, value).text.split())
                if val == value2:
                    func()
                return True
            except Exception as error:
                log.info(f"Checked for {value}; select error {error}")
            self.wait(1)
        return False

    def select_box(self, by0, value0, by1, value1):
        self.driver.find_element(by0, value0).click()
        self.driver.find_element(by1, value1).click()

    def press_exists(self, by, value, num):
        for i in range(num):
            try:
                self.driver.find_element(by, value).click()
            except:
                pass

    def process(self, idx):
        self.working_on = idx
        passport = self.sheet[f"d{idx}"].value
        birth_date = self.sheet[f"i{idx}"].value
        year = int(birth_date[-4:])
        phone_number = self.sheet[f"k{idx}"].value

        log.info(f"Loaded: <Data d{idx}={passport} i{idx}={year} k{idx}={phone_number}>")

        self.driver.find_element(By.XPATH, buttons["So‘rovnoma qo‘shish"]).click()

        self.wait(1)

        self.pass_if_exists(By.XPATH, checkers['Fuqaro qo‘shish'])

        self.driver.find_element(By.XPATH, inputs['Pasport']).send_keys(passport)

        self.wait()

        self.driver.find_element(By.XPATH, inputs['Tug‘ilgan sana']).send_keys(birth_date)

        self.wait(1)
        self.driver.find_element(By.XPATH, buttons['Qidirish']).click()

        self.wait(1)
        self.pass_if_non_exists(By.CLASS_NAME, 'el-loading-mask')

        self.wait()

        resp = self.execute_if_exists(By.XPATH, checkers['Qidirish xatoligi 1'], self.go_next, 5)
        if resp:
            log.warning("Going to next because of error")
            return

        resp = self.execute_if_exists(By.XPATH, checkers['Qidirish xatoligi'], self.go_next, 5)
        if resp:
            log.warning("Going to next because of error")
            return
        self.pass_if_non_exists(By.CLASS_NAME, 'el-loading-mask')

        self.wait(1)

        self.pass_if_exists(By.XPATH, buttons['Saqlash va kirish'])
        self.wait(5)

        while True:
            try:
                self.driver.find_element(By.XPATH, buttons['Saqlash va kirish']).click()
                log.error(f"Saqlash pressed")
            except:
                self.restart()
                return

        self.pass_if_non_exists(By.CLASS_NAME, 'el-loading-mask')

        self.wait()

        resp = self.execute_if_value_equals(By.XPATH, buttons['Yakunlash tugmasi'], self.restart, 3, "Yakunlash")
        if resp:
            log.warning(f"Refreshing page")
            return

        self.select_box(
            By.XPATH, inputs['Kocha'],
            By.XPATH, options['Soy yoli']
        )

        self.wait(1)

        self.driver.find_element(By.XPATH, inputs['Uy ramqami']).send_keys(random.randint(0, 100))
        self.wait()

        self.driver.find_element(By.XPATH, inputs['Telefon']).send_keys(phone_number)
        self.wait()

        self.driver.find_element(By.XPATH, buttons['Saqlash']).click()
        self.wait()

        self.pass_if_non_exists(By.CLASS_NAME, 'el-loading-mask')

        self.fill_form()

    def go_next(self):
        self.driver.refresh()
        self.wait(5)
        self.process(self.working_on + 1)

    def restart(self):
        self.driver.refresh()
        self.wait(1)
        self.process(self.working_on)

    @staticmethod
    def wait(seconds=0.5):
        time.sleep(seconds)

    def quit(self):
        self.driver.close()

    def fill_form(self):
        try:
            self.driver.find_element(By.XPATH, buttons['Unknownn 1']).click()
        except:
            pass

        run_f = [
            self.bandlik_holati,
            self.talim_malumoti,
            self.oilaviy_holat,
            self.ijtimoiy_holat,
            self.erishgan_yutuqlar,
            self.qiziqishlari,
            self.taklif_etilgan_loyihalar,
            self.aniqlangan_muommolar,
            self.yoshlar_daftari
        ]

        for func in run_f:
            try:
                func()
            except:
                pass

    def bandlik_holati(self):
        self.driver.find_element(By.XPATH,'//*[@id="app"]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[2]/div/div[1]/div/div/label[4]/span[1]/span').click()
        self.wait(1)
        self.driver.find_element(By.XPATH,'//*[@id="app"]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[2]/div/div[2]/form/div/div/div/div[2]/div/div/div/div/div[3]/div[2]/label/span[1]/span').click()
        self.wait(1)
        self.driver.find_element(By.XPATH,"/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[2]/div/div[3]/button").click()
        log.info("Bandlik xolati tugadi")

    def talim_malumoti(self):
        self.driver.find_element(By.XPATH, "/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[3]/form/div[3]/div/div/div/div/div/div/label[1]/span[1]/span").click()
        self.wait()
        self.driver.find_element(By.XPATH, "/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[3]/form/div[4]/div[1]/div/div/div/div[1]/input").click()
        self.wait()
        self.driver.find_element(By.XPATH, "/html/body/div[2]/div[1]/div[1]/ul/li[1]").click()
        self.wait()

        #muassasa toifasi
        self.driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[3]/form/div[4]/div[2]/div/div/div/div[1]/input").click()
        self.wait()
        self.driver.find_element(By.XPATH, "/html/body/div[3]/div[1]/div[1]/ul/li[1]").click()
        self.wait()

        #shakli
        self.driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[3]/form/form/div[1]/div/div[1]/div/div/div/label[1]/span[1]/span").click()
        self.wait()

        #ta'lim muassasasi nomi
        self.driver.find_element(By.XPATH,"/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[3]/form/form/div[1]/div/div[2]/div/div/div/input").send_keys("maktab")
        self.wait()

        self.driver.find_element(By.XPATH,"/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[3]/form/form/div[2]/div[2]/div/div/div/div[1]/input").send_keys(f"{yil+18}")
        log.info("tamomlagan yili kiritildi")

        self.driver.find_element(By.XPATH,"/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[3]/form/div[6]/button").click()

        log.info("saqlash bosildi")

        # time.sleep(5)
        # driver.find_element(By.XPATH, "/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[3]/form/div[4]/div[1]/div/div/div/div[1]/input").click()
        # driver.find_element(By.XPATH, "/html/body/div[2]/div[1]/div[1]/ul/li[1]").click()
        # time.sleep(2)
        # driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[3]/form/div[4]/div[2]/div/div/div/div/input").click()
        # time.sleep(2)
        # driver.find_element(By.XPATH, "/html/body/div[3]/div[1]/div[1]/ul/li[1]").click()
        # time.sleep(2)
        # driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[3]/form/form/div[1]/div/div[1]/div/div/div/label[1]/span[2]").click()
        # driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[3]/form/form/div[1]/div/div[1]/div/div/div/label[1]/span[2]").send_keys(input("muassasa: "))
        # input("saqlash: ")
        # # driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[3]/form/div[6]/button").click()
        # print("tugadi 2")
        # time.sleep(0.5)


    def oilaviy_holat(self):
        self.driver.find_element(By.XPATH,"/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[4]/form/div[2]/div/div/div/div/label[1]/span[1]/span").click()
        self.wait(1)
        self.driver.find_element(By.XPATH,"/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[4]/form/div[3]/button").click()
        self.wait()

    def salomatlik_holati(self):
        self.driver.find_element(By.XPATH,'//*[@id="app"]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[5]/form/div[2]/div/div/div/div/label[1]/span[1]/span').click()
        self.wait(1)
        self.driver.find_element(By.XPATH,'//*[@id="app"]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[5]/form/div[3]/button').click()

    def ijtimoiy_holat(self):
        self.driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[6]/form/div[4]/div/label/span[1]/span').click()
        self.wait(1)
        self.driver.find_element(By.XPATH, "/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[6]/form/div[3]/button").click()
        self.wait(5)

    def erishgan_yutuqlar(self):
        self.driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[7]/form/div[4]/div/label/span[1]/span').click()
        self.wait(1)
        self.driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[7]/form/div[2]/button').click()
        self.wait(5)

    def qiziqishlari(self):
        self.driver.find_element(By.XPATH, "/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[8]/form/div[3]/div/label/span[1]/span").click()
        self.wait(1)
        self.driver.find_element(By.XPATH, "/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[8]/form/div[2]/button").click()
        self.wait(5)

    def taklif_etilgan_loyihalar(self):
        self.driver.find_element(By.XPATH,'//*[@id="app"]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[9]/form/div[3]/div/label/span[1]/span').click()
        self.wait(1)
        self.driver.find_element(By.XPATH,'//*[@id="app"]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[9]/form/div[2]/button').click()
        self.wait(1)

    def aniqlangan_muommolar(self):
        self.driver.find_element(By.XPATH,'//*[@id="app"]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[10]/form/div[2]/div/label/span[1]/span').click()
        self.wait(1)
        self.driver.find_element(By.XPATH,'//*[@id="app"]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[10]/form/div[2]/button').click()
        self.wait(5)

    def yoshlar_daftari(self):
        self.driver.find_element(By.XPATH, "/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[11]/div/form/div[1]/div/div/div/div/label[2]/span[1]/span").click()
        self.wait(1)
        self.driver.find_element(By.XPATH, "/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[11]/div/form/div[2]/button").click()
        self.wait(5)


web = Web()
input()
web.process(941)

web.quit()

#
# input()
# def surovnoma_qushish(i):
#     print(yil)
#     #so'rovnoma qo'shish
#     #malumotlarni kiritish
#
#     # yil=input("yilni kiriting: ")
#     time.sleep(1)
#
#     input()
#
#     # time.sleep(1)
#     #qidirish tugmasini bosish
#     # time.sleep(1)
#     input()
#     # try:
#     #     driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[2]/div/div[3]/div/div/section/div/form/div[9]/p')
#     #     print("bor")
#     #     driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div[2]/div/div[3]/div/div/header/button").click()
#     #     time.sleep(1)
#     #     surovnoma_qushish(i+1)
#
#
#     except:
#
#         #saqlash va kiritish
#         # driver.find_element(By.XPATH,"/html/body/div[1]/div[1]/div[2]/div/div[3]/div/div/section/div/form/div[9]/button").click()
#         # time.sleep(1)
#         # input()
#         # surovnoma_qushish()
#         # try:
#         #     yakunlash_tugmasi=driver.find_element(By.XPATH,).text
#         #     if yakunlash_tugmasi=="Yakunlash":
#         #         surovnoma_qushish()
#         # except:
#             # input("anketa to'ldirishni boshlash")
#             # driver.find_element(By.XPATH,"/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[1]/form/div[1]/div[1]/div[3]/div[7]/div/div/div/div/input").click()
#             #                             /html/body/div[4]/div[1]/div[1]/ul/li[1]
#             # driver.find_element(By.XPATH,"/html/body/div[2]/div[1]/div[1]/ul/li[1]").click()
#             # input()
#             # driver.find_element(By.XPATH,"/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[1]/form/div[1]/div[1]/div[3]/div[8]/div/div/div/input").send_keys(f"{random.randint(1,100)}")
#             # input()
#             # driver.find_element(By.XPATH,"").send_keys(tel)
#             # input()
#             # driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[1]/form/div[2]/button").click()
#             # input()
#             # try:
#             #     driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[1]/div[2]/div/button").click()
#             #     input("Fuqaro malumotlarini to'ldirishni tekshirish")
#             # except:
#             #     pass
#
#             def bandlik_holati():
#                 driver.find_element(By.XPATH,'//*[@id="app"]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[2]/div/div[1]/div/div/label[4]/span[1]/span').click()
#                                                     # '//*[@id="app"]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[2]/div/div[1]/div/div/label[5]/span[1]/span'
#
#                 time.sleep(1)
#                 driver.find_element(By.XPATH,'//*[@id="app"]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[2]/div/div[2]/form/div/div/div/div[2]/div/div/div/div/div[3]/div[2]/label/span[1]/span').click()
#                 time.sleep(1)
#                 driver.find_element(By.XPATH,"/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[2]/div/div[3]/button").click()
#                 input('Bandlik holati tugadi')
#
#             def talim_malumoti():
#                 driver.find_element(By.XPATH, "/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[3]/form/div[3]/div/div/div/div/div/div/label[1]/span[1]/span").click()
#                 time.sleep(0.5)
#                 driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[3]/form/div[4]/div[1]/div/div/div/div[1]/input").click()
#                 time.sleep(0.5)
#                 # if 1994<=yil<=2000: ta'lim tanlash jarayoni
#
#                 driver.find_element(By.XPATH,"/html/body/div[2]/div[1]/div[1]/ul/li[1]").click()
#                 time.sleep(0.5)
#
#                 #muassasa toifasi
#                 driver.find_element(By.XPATH,"/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[3]/form/div[4]/div[2]/div/div/div/div[1]/input").click()
#                 time.sleep(0.5)
#                 driver.find_element(By.XPATH,"/html/body/div[3]/div[1]/div[1]/ul/li[1]").click()
#                 time.sleep(0.5)
#
#                 #shakli
#                 driver.find_element(By.XPATH,"/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[3]/form/form/div[1]/div/div[1]/div/div/div/label[1]/span[1]/span").click()
#                 time.sleep(0.5)
#
#                 #ta'lim muassasasi nomi
#                 driver.find_element(By.XPATH,"/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[3]/form/form/div[1]/div/div[2]/div/div/div/input").send_keys("maktab")
#                 time.sleep(0.5)
#
#                 driver.find_element(By.XPATH,"/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[3]/form/form/div[2]/div[2]/div/div/div/div[1]/input").send_keys(f"{yil+18}")
#                 input("tamomlagan yili kiritildi")
#
#                 driver.find_element(By.XPATH,"/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[3]/form/div[6]/button").click()
#
#                 input("saqlash bosildi")
#
#
#
#                 # time.sleep(5)
#                 # driver.find_element(By.XPATH, "/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[3]/form/div[4]/div[1]/div/div/div/div[1]/input").click()
#                 # driver.find_element(By.XPATH, "/html/body/div[2]/div[1]/div[1]/ul/li[1]").click()
#                 # time.sleep(2)
#                 # driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[3]/form/div[4]/div[2]/div/div/div/div/input").click()
#                 # time.sleep(2)
#                 # driver.find_element(By.XPATH, "/html/body/div[3]/div[1]/div[1]/ul/li[1]").click()
#                 # time.sleep(2)
#                 # driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[3]/form/form/div[1]/div/div[1]/div/div/div/label[1]/span[2]").click()
#                 # driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[3]/form/form/div[1]/div/div[1]/div/div/div/label[1]/span[2]").send_keys(input("muassasa: "))
#                 # input("saqlash: ")
#                 # # driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[3]/form/div[6]/button").click()
#                 # print("tugadi 2")
#                 # time.sleep(0.5)
#
#
#             def oilaviy_holat():
#                 driver.find_element(By.XPATH,"/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[4]/form/div[2]/div/div/div/div/label[1]/span[1]/span").click()
#                 time.sleep(1)
#                 driver.find_element(By.XPATH,"/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[4]/form/div[3]/button").click()
#                 time.sleep(0.5)
#
#             def salomatlik_holati():
#                 driver.find_element(By.XPATH,'//*[@id="app"]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[5]/form/div[2]/div/div/div/div/label[1]/span[1]/span').click()
#
#                 input("salomatlik saqlash")
#                 time.sleep(1)
#                 driver.find_element(By.XPATH,'//*[@id="app"]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[5]/form/div[3]/button').click()
#                 input()
#
#             def ijtimoiy_holat():
#                 driver.find_element(By.XPATH,'//*[@id="app"]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[6]/form/div[4]/div/label/span[1]/span').click()
#
#                 time.sleep(1)
#                 driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[6]/form/div[3]/button").click()
#
#                 input()
#
#             def erishgan_yutuqlar():
#                 driver.find_element(By.XPATH,'//*[@id="app"]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[7]/form/div[4]/div/label/span[1]/span').click()
#                 time.sleep(1)
#                 driver.find_element(By.XPATH,'//*[@id="app"]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[7]/form/div[2]/button').click()
#
#                 input()
#
#
#             def qiziqishlari():
#                 driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[8]/form/div[3]/div/label/span[1]/span").click()
#
#                 time.sleep(1)
#                 driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[8]/form/div[2]/button").click()
#                 input()
#
#
#
#             def taklif_etilgan_loyihalar():
#                 driver.find_element(By.XPATH,'//*[@id="app"]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[9]/form/div[3]/div/label/span[1]/span').click()
#                 time.sleep(1)
#                 driver.find_element(By.XPATH,'//*[@id="app"]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[9]/form/div[2]/button').click()
#                 input()
#
#
#             def aniqlangan_muommolar():
#                 driver.find_element(By.XPATH,'//*[@id="app"]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[10]/form/div[2]/div/label/span[1]/span').click()
#                 time.sleep(1)
#                 driver.find_element(By.XPATH,'//*[@id="app"]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[10]/form/div[2]/button').click()
#                 input()
#
#
#             def yoshlar_daftari():
#                 driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[11]/div/form/div[1]/div/div/div/div/label[2]/span[1]/span").click()
#                 time.sleep(1)
#                 driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[11]/div/form/div[2]/button").click()
#                 input()
#
#
#
#
#
#
#             try:
#                 driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[2]/h4").find_element(By.TAG_NAME,"i")
#             except:
#                 bandlik_holati()
#
#             try:
#                 driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[3]/h4").find_element(By.TAG_NAME,"i")
#             except:
#                 talim_malumoti()
#
#             try:
#                 driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[4]/h4").find_element(By.TAG_NAME,"i")
#             except:
#                 oilaviy_holat()
#
#             try:
#                 driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[5]/h4").find_element(By.TAG_NAME,"i")
#             except:
#                 salomatlik_holati()
#
#             try:
#                 driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[6]/h4").find_element(By.TAG_NAME,"i")
#             except:
#                 ijtimoiy_holat()
#
#             try:
#                 driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[7]/h4").find_element(By.TAG_NAME,"i")
#             except:
#                 erishgan_yutuqlar()
#
#             try:
#                 driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[8]/h4").find_element(By.TAG_NAME,"i")
#             except:
#                 qiziqishlari()
#
#             try:
#                 driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[9]/h4").find_element(By.TAG_NAME,"i")
#             except:
#                 taklif_etilgan_loyihalar()
#
#             try:
#                 driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[10]/h4").find_element(By.TAG_NAME,"i")
#             except:
#                 aniqlangan_muommolar()
#
#             try:
#                 driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[11]/h4").find_element(By.TAG_NAME,"i")
#
#             except:
#                 yoshlar_daftari()
#
#
#             driver.find_element(By.XPATH,"/html/body/div/div[1]/div[2]/div/div[2]/div/div[2]/div/div[12]/button").click()
#
#             input("tugadi")
#             surovnoma_qushish(i+1)
#
#
# try:
#
#     surovnoma_qushish(951)
# except Exception as err:
#     print(err)
#     input()
# # Close the browser window
# driver.quit()
