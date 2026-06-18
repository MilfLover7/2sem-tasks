import tkinter as tk
from tkinter import messagebox
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Patch
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from Prodgect2semClasses import *

class Interface:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Фазовые переходы")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')

        # ввод
        self.widthVar = tk.StringVar(value="40")
        self.heightVar = tk.StringVar(value="30")
        self.moleculesVar = tk.StringVar(value="5000")
        self.temperatureVar = tk.StringVar(value="300")
        self.evaporationVar = tk.StringVar(value="2.5")
        self.condensationVar = tk.StringVar(value="0.8")
        self.startTempVar = tk.StringVar(value="100")
        self.endTempVar = tk.StringVar(value="500")
        self.durationVar = tk.StringVar(value="30")

        # состояние
        self.simulator = None
        self.isRunning = False
        self.animation = None
        self.lastFrameTime = 0
        self.frameCount = 0

        self.createWidgets()
        self.root.after(100, self.initSimulator)

    # интерфейс
    def createWidgets(self):
        controlFrame = tk.Frame(self.root, bg='#e0e0e0', relief='ridge', bd=2, height=65)
        controlFrame.pack(fill='x', padx=5, pady=5)
        controlFrame.pack_propagate(False)

        rowFrame = tk.Frame(controlFrame, bg='#e0e0e0')
        rowFrame.pack(fill='both', expand=True, padx=10, pady=3)

        tk.Label(rowFrame, text="ФАЗОВЫЙ ПЕРЕХОД", font=('Arial', 12, 'bold'),
                 bg='#e0e0e0').pack(side='left', padx=10)

        params = [("Ширина:", self.widthVar, 5),
                  ("Высота:", self.heightVar, 5),
                  ("Молекул:", self.moleculesVar, 6),
                  ("T:", self.temperatureVar, 5)]

        for label, var, w in params:
            tk.Label(rowFrame, text=label, bg='#e0e0e0', font=('Arial', 9)).pack(side='left', padx=2)
            tk.Entry(rowFrame, textvariable=var, width=w, bg='white',
                     relief='solid', bd=1).pack(side='left', padx=2)

        tk.Button(rowFrame, text="Старт", command=self.applyParams,
                  bg='#4CAF50', fg='white', font=('Arial', 9, 'bold')).pack(side='left', padx=5)
        tk.Button(rowFrame, text="Стоп", command=self.stopSimulation,
                  bg='#f44336', fg='white', font=('Arial', 9, 'bold')).pack(side='left', padx=5)

        # нагрев
        rampFrame = tk.Frame(self.root, bg='#d0d0d0', relief='ridge', bd=1, height=35)
        rampFrame.pack(fill='x', padx=5, pady=2)
        rampFrame.pack_propagate(False)

        rampRow = tk.Frame(rampFrame, bg='#d0d0d0')
        rampRow.pack(fill='both', expand=True, padx=10, pady=2)

        tk.Label(rampRow, text="НАГРЕВ:", font=('Arial', 9, 'bold'),
                 bg='#d0d0d0').pack(side='left', padx=5)
        tk.Label(rampRow, text="От:", bg='#d0d0d0', font=('Arial', 9)).pack(side='left')
        tk.Entry(rampRow, textvariable=self.startTempVar, width=5,
                 bg='white', relief='solid', bd=1).pack(side='left', padx=2)
        tk.Label(rampRow, text="До:", bg='#d0d0d0', font=('Arial', 9)).pack(side='left', padx=5)
        tk.Entry(rampRow, textvariable=self.endTempVar, width=5,
                 bg='white', relief='solid', bd=1).pack(side='left', padx=2)
        tk.Label(rampRow, text="За (сек):", bg='#d0d0d0', font=('Arial', 9)).pack(side='left', padx=5)
        tk.Entry(rampRow, textvariable=self.durationVar, width=5,
                 bg='white', relief='solid', bd=1).pack(side='left', padx=2)
        tk.Button(rampRow, text="▶ Нагрев", command=self.startRamp,
                  bg='#FF9800', fg='white', font=('Arial', 9, 'bold')).pack(side='left', padx=10)


        mainFrame = tk.Frame(self.root, bg='#f0f0f0')
        mainFrame.pack(fill='both', expand=True, padx=5, pady=5)

        # молекулы
        leftFrame = tk.Frame(mainFrame, bg='white', relief='ridge', bd=2)
        leftFrame.pack(side='left', fill='both', expand=True, padx=2)
        tk.Label(leftFrame, text="МОЛЕКУЛЫ", font=('Arial', 10, 'bold'), bg='white').pack()

        self.figMol = plt.Figure(figsize=(5, 5), dpi=100)
        self.axMol = self.figMol.add_subplot(111)
        self.axMol.set_facecolor('#f0f8ff')
        self.canvasMol = FigureCanvasTkAgg(self.figMol, leftFrame)
        self.canvasMol.get_tk_widget().pack(fill='both', expand=True)

        # графики
        midFrame = tk.Frame(mainFrame, bg='white', relief='ridge', bd=2)
        midFrame.pack(side='left', fill='both', expand=True, padx=2)
        tk.Label(midFrame, text="ГРАФИКИ", font=('Arial', 10, 'bold'), bg='white').pack()

        self.figGraph = plt.Figure(figsize=(5, 5), dpi=100)
        self.axGraph1 = self.figGraph.add_subplot(211)
        self.axGraph2 = self.figGraph.add_subplot(212)
        self.figGraph.tight_layout(pad=1.5)
        self.canvasGraph = FigureCanvasTkAgg(self.figGraph, midFrame)
        self.canvasGraph.get_tk_widget().pack(fill='both', expand=True)

        # гистограммы
        rightFrame = tk.Frame(mainFrame, bg='white', relief='ridge', bd=2)
        rightFrame.pack(side='left', fill='both', expand=True, padx=2)
        tk.Label(rightFrame, text="ГИСТОГРАММЫ", font=('Arial', 10, 'bold'), bg='white').pack()

        self.figHist = plt.Figure(figsize=(5, 5), dpi=100)
        self.axHist1 = self.figHist.add_subplot(211)
        self.axHist2 = self.figHist.add_subplot(212)
        self.figHist.tight_layout(pad=1.5)
        self.canvasHist = FigureCanvasTkAgg(self.figHist, rightFrame)
        self.canvasHist.get_tk_widget().pack(fill='both', expand=True)


        statusFrame = tk.Frame(self.root, bg='#e0e0e0', relief='ridge', bd=1, height=30)
        statusFrame.pack(fill='x', padx=5, pady=5)
        statusFrame.pack_propagate(False)

        self.statusVar = tk.StringVar(value="Готов к работе")
        tk.Label(statusFrame, textvariable=self.statusVar,
                 font=('Arial', 10), bg='#e0e0e0').pack(side='left', padx=10)

        self.heatStatusVar = tk.StringVar(value="")
        tk.Label(statusFrame, textvariable=self.heatStatusVar,
                 font=('Arial', 10), fg='#FF9800', bg='#e0e0e0').pack(side='left', padx=20)

    def initSimulator(self):
        try:
            width = float(self.widthVar.get())
            height = float(self.heightVar.get())
            num = int(self.moleculesVar.get())
            temp = float(self.temperatureVar.get())

            if temp > 1500:
                if not messagebox.askyesno( f"Температура {temp}K слишком высокая.\n"
                                           f"Рекомендуется до 1000K.\nПродолжить?"):
                    return
            if temp < 10:
                temp = 10

            if num > 30000:
                if not messagebox.askyesno( f"Вы запросили {num} молекул.\n"
                                           f"Рекомендуется до 15000 для комфортной работы.\n"
                                           f"Продолжить?"):
                    return
                num = 20000

            self.simulator = Simulator(width=width, height=height,
                numMolecules=num, temperature=temp)

            self.isRunning = True
            self.statusVar.set(f"Создано: {num} молекул, T={temp}K")
            self.startAnimation()

        except Exception as e:
            messagebox.showerror(f"Не удалось создать симулятор:\n{e}")

    def applyParams(self):
        self.stopSimulation()
        self.initSimulator()

    # Запуск анимации
    def startAnimation(self):
        if self.animation:
            self.animation.event_source.stop()

        self.axMol.clear()
        self.axMol.set_xlim(0, self.simulator.width)
        self.axMol.set_ylim(0, self.simulator.height)
        self.axMol.set_aspect('equal')
        self.axMol.set_facecolor('#f0f8ff')
        self.axMol.grid(True, alpha=0.2)

        self.scatter = self.axMol.scatter([], [], s=10, c='blue', alpha=0.7)

        legendElements = [ Patch(facecolor='blue', alpha=0.7, label='Жидкость'),
            Patch(facecolor='red', alpha=0.7, label='Газ'), ]
        self.axMol.legend(handles=legendElements, loc='upper right', fontsize=7)

        self.animation = FuncAnimation(
            self.figMol, self.updateAll,
            interval=30, cache_frame_data=False)

    #пауза
    def stopSimulation(self):
        if self.animation:
            self.animation.event_source.stop()
            self.animation = None
        self.isRunning = False
        self.statusVar.set("Остановлена")
        self.heatStatusVar.set("")

    # обновление всех графиков
    def updateAll(self, frame):
        if not self.isRunning or not self.simulator:
            return

        currentTime = time.time()
        self.lastFrameTime = currentTime

        self.simulator.update(dt=0.03)#0,03- прост частота отрисовки
        stats = self.simulator.getStatistics()
        molecules = self.simulator.getMolecules()

        # отрисовка молекул
        xs = [mol.x for mol in molecules]
        ys = [mol.y for mol in molecules]
        colors = [(0.0, 0.0, 1.0, 0.7) if mol.isLiquid else (1.0, 0.0, 0.0, 0.7)
                  for mol in molecules]
        sizes = [(mol.radius * 15) ** 2 for mol in molecules]

        self.scatter.set_offsets(np.column_stack((xs, ys)))
        self.scatter.set_facecolors(colors)
        self.scatter.set_sizes(sizes)

        updateTimeMs = stats.get('updateTime', 0) * 1000
        self.axMol.set_title(
            f'Время: {stats["time"]:.1f}s | T: {stats["temperature"]:.1f}K '
            f'Обновление: {updateTimeMs:.0f}мс', fontsize=9
        )
        self.canvasMol.draw()

        self.frameCount += 1
        if self.frameCount % 5 == 0:
            self.updateGraphs(stats)
            self.updateHistograms(stats)

        #обновляем статусы))
        if self.simulator.tempChangeActive:
            progress = min(100, self.simulator.tempElapsed / self.simulator.tempDuration * 100)
            self.heatStatusVar.set(
                f" {self.simulator.tempStart:.0f} -> {self.simulator.tempEnd:.0f}K ({progress:.0f}%)"
            )
        else:
            self.heatStatusVar.set("")

        self.statusVar.set(
            f"Время: {stats['time']:.1f}s  "
            f"Фаза: {stats['phase']}  "
            f"Жидкость: {stats['liquidCount']}  "
            f"Газ: {stats['gasCount']} "
            f"T: {stats['temperature']:.1f}K"
        )

    def updateGraphs(self, stats):
        #температура
        self.axGraph1.clear()
        if self.simulator.temperatureHistory:
            x = list(range(len(self.simulator.temperatureHistory)))
            self.axGraph1.plot(x, self.simulator.temperatureHistory,
                               'b-', label='Температура', linewidth=1.5)
            self.axGraph1.axhline(y=self.simulator.temperature, color='red',
                                  linestyle='--', linewidth=1.5,
                                  label=f'Заданная T={self.simulator.temperature:.0f}K')
        self.axGraph1.set_title('Температура', fontsize=9)
        self.axGraph1.set_xlabel('Шаг', fontsize=7)
        self.axGraph1.set_ylabel('T (K)', fontsize=7)
        self.axGraph1.grid(True, alpha=0.3)
        self.axGraph1.legend(fontsize=7)

        # давление
        self.axGraph2.clear()
        if self.simulator.pressureHistory:
            x = list(range(len(self.simulator.pressureHistory)))
            self.axGraph2.plot(x, self.simulator.pressureHistory,
                               'purple', label='Давление', linewidth=1.5)
        self.axGraph2.set_title('Давление', fontsize=9)
        self.axGraph2.set_xlabel('Шаг', fontsize=7)
        self.axGraph2.set_ylabel('P', fontsize=7)
        self.axGraph2.grid(True, alpha=0.3)
        self.axGraph2.legend(fontsize=7)

        self.figGraph.tight_layout(pad=1.5)
        self.canvasGraph.draw()

    def updateHistograms(self, stats):

        self.axHist1.clear()
        speedsRaw = self.simulator.getSpeeds()

        if speedsRaw:
            sortedSpeeds = sorted(speedsRaw)
            cutIndex = int(len(sortedSpeeds) * 0.7)
            if cutIndex < 5:
                cutIndex = len(sortedSpeeds)
            speeds = sortedSpeeds[:cutIndex]

            if speeds and max(speeds) > 0:
                maxSpeed = max(speeds)
                numBins = min(25, max(5, int(maxSpeed / 0.3)))
                if numBins < 3:
                    numBins = 5

                self.axHist1.hist(speeds, bins=numBins, density=True, alpha=0.7, color='green', edgecolor='black')
                self.axHist1.set_title('Распределение скоростей', fontsize=9)
                self.axHist1.set_xlabel('Скорость', fontsize=7)
                self.axHist1.set_ylabel('Плотность', fontsize=7)
                self.axHist1.grid(True, alpha=0.3)

                avg = sum(speeds) / len(speeds)
                self.axHist1.axvline(x=avg, color='red', linestyle='--', label=f'Средняя: {avg:.2f}')
                self.axHist1.legend(fontsize=7)
            else:
                self.axHist1.text(0.5, 0.5, 'Недостаточно данных', transform=self.axHist1.transAxes, ha='center', va='center')
                self.axHist1.set_title('Распределение скоростей', fontsize=9)
        else:
            self.axHist1.text(0.5, 0.5, 'Нет данных', transform=self.axHist1.transAxes, ha='center', va='center')
            self.axHist1.set_title('Распределение скоростей', fontsize=9)

        # фазы
        self.axHist2.clear()
        liquid = stats['liquidCount']
        gas = stats['gasCount']

        counts = []
        labels = []
        colors = []

        if liquid > 0:
            counts.append(liquid)
            labels.append('Жидкость')
            colors.append('blue')
        if gas > 0:
            counts.append(gas)
            labels.append('Газ')
            colors.append('red')

        if sum(counts) > 0:
            self.axHist2.pie(counts, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            self.axHist2.set_title('Фазовый состав', fontsize=9)
        else:
            self.axHist2.text(0.5, 0.5, 'Нет данных', transform=self.axHist2.transAxes, ha='center', va='center')
            self.axHist2.set_title('Фазовый состав', fontsize=9)

        self.figHist.tight_layout(pad=1.5)
        self.canvasHist.draw()

    # нагревание
    def startRamp(self):
        try:
            start = float(self.startTempVar.get())
            end = float(self.endTempVar.get())
            duration = float(self.durationVar.get())

            if end > 1500:
                messagebox.showerror( f"Максимум 1500K (Вы ввели {end}K)")
                return
            if start < 10:
                messagebox.showerror( "Минимум 10K")
                return
            if start >= end:
                messagebox.showerror(f"Начальная T ({start}K) должна быть меньше конечной ({end}K)")
                return
            if duration < 1:
                messagebox.showerror( "Длительность >= 1 секунды")
                return
            if not self.simulator:
                messagebox.showerror("Симулятор не создан")
                return

            self.simulator.startTemperatureRamp(start, end, duration)
            self.statusVar.set(f"Нагрев: {start} → {end}K за {duration}с")

        except ValueError:
            messagebox.showerror("Введите корректные числа")



    def run(self):
        self.root.mainloop()