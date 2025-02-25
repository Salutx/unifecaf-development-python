from selenium import webdriver
from selenium.webdriver.common.by import By
from config import WEATHER_FORECAST_SITE
from datetime import datetime
import locale
import csv
import os
import tkinter as tk
import pandas as pd
import matplotlib.pyplot as plt

locale.setlocale(locale.LC_TIME, "Portuguese_Brazil.1252")


def configurar_driver():
    driver = webdriver.Chrome()
    return driver


def format_temp(temp):
    return temp.replace("°C", "").replace(",", ".")


def salvar_dados(dados, arquivo):
    arquivo_existe = os.path.isfile(arquivo)

    with open(arquivo, "a", newline="") as f:
        cabecalhos = ["data_hora", "temperatura_atual", "umidade", "registrado_em"]
        writer = csv.DictWriter(f, fieldnames=cabecalhos)

        if not arquivo_existe:
            writer.writeheader()

        writer.writerow(dados)


def get_data_from_csv(csv_filename):
    if not os.path.isfile(csv_filename):
        return None

    return pd.read_csv(csv_filename)


def update_table():
    driver = configurar_driver()
    driver.get(WEATHER_FORECAST_SITE)

    currentSubNavClass = "subnav-pagination"
    currentSubNavElement = driver.find_element(By.CLASS_NAME, currentSubNavClass)

    currentDateBySubNav = currentSubNavElement.find_element(By.TAG_NAME, "div")
    currentDate = currentDateBySubNav.text

    currentTimeHeaderClass = ".card-header.spaced-content"
    currentTimeHeaderElement = driver.find_element(
        By.CSS_SELECTOR, currentTimeHeaderClass
    )

    currentTimeElement = currentTimeHeaderElement.find_element(By.CLASS_NAME, "sub")
    currentTime = currentTimeElement.text

    currentTempClass = "display-temp"
    currentTemp = driver.find_element(By.CLASS_NAME, currentTempClass).text

    currentUmidityLabel = driver.find_element(By.XPATH, "//div[text()='Umidade']")
    currentUmidityValue = currentUmidityLabel.find_element(
        By.XPATH, "following-sibling::div"
    ).text

    # Formatando os dados
    formattedUmidity = currentUmidityValue.replace("%", "")
    formattedDate = currentDate.split(",")[1].strip()
    formattedDate = datetime.strptime(formattedDate, "%d DE %B")
    formattedDate = formattedDate.replace(year=datetime.now().year)
    formattedDate = datetime.strptime(
        f"{formattedDate.date()} {currentTime}", "%Y-%m-%d %H:%M"
    )
    formattedDate = formattedDate.strftime("%d/%m/%Y %H:%M")
    formattedTemp = format_temp(currentTemp)

    dados = {
        "data_hora": formattedDate,
        "temperatura_atual": formattedTemp,
        "umidade": formattedUmidity,
        "registrado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
    }

    salvar_dados(dados, f"dados_clima_{datetime.now().strftime('%Y%m%d')}.csv")

    input("Pressione Enter para fechar o navegador...")
    driver.quit()


def build_chart():
    csv_today = f"dados_clima_{datetime.now().strftime('%Y%m%d')}.csv"
    csv_data = get_data_from_csv(csv_today)

    if csv_data is not None and not csv_data.empty:
        # Build chart with x-axis with date and y-axis with umidity and temperature

        fig, ax1 = plt.subplots()

        ax2 = ax1.twinx()
        ax1.plot(csv_data["data_hora"], csv_data["temperatura_atual"], "g-")
        ax2.plot(csv_data["data_hora"], csv_data["umidade"], "b-")

        ax1.set_xlabel("Data e Hora")
        ax1.set_ylabel("Temperatura (°C)", color="g")
        ax2.set_ylabel("Umidade (%)", color="b")

        fig.autofmt_xdate()

        plt.show()
    else:
        print("Nenhum dado encontrado para gerar o gráfico.")


def build_screen():
    csv_today = f"dados_clima_{datetime.now().strftime('%Y%m%d')}.csv"
    csv_data = get_data_from_csv(csv_today)

    if csv_data is not None and not csv_data.empty:
        last_row = csv_data.iloc[-1]
        temperatura = last_row["temperatura_atual"]
        umidade = last_row["umidade"]
        horario = last_row["data_hora"]
    else:
        temperatura, umidade, horario = "N/A", "N/A", "N/A"

    root = tk.Tk()
    root.title("Atualizar Previsão do Tempo")
    root.geometry("400x300")

    btn_atualizar = tk.Button(
        root, text="Atualizar tabela", font=("Arial", 12), command=update_table
    )

    btn_grafico = tk.Button(
        root, text="Gerar gráfico", font=("Arial", 12), command=build_chart
    )

    lbl_titulo = tk.Label(
        root, text="Previsão do Tempo (último registro)", font=("Arial", 14)
    )
    lbl_temp = tk.Label(
        root, text=f"🌡️ Temperatura: {temperatura}°C", font=("Arial", 12)
    )
    lbl_umid = tk.Label(root, text=f"💧 Umidade: {umidade}%", font=("Arial", 12))
    lbl_hora = tk.Label(root, text=f"🕒 Horário: {horario}", font=("Arial", 12))
    lbl_rows = tk.Label(
        root, text=f"Total de registros: {len(csv_data)}", font=("Arial", 12)
    )

    lbl_titulo.pack(pady=10)
    lbl_temp.pack(pady=5)
    lbl_umid.pack(pady=5)
    lbl_hora.pack(pady=5)
    btn_atualizar.pack(pady=10)
    btn_grafico.pack(pady=10)
    lbl_rows.pack(pady=5)

    root.mainloop()


build_screen()
