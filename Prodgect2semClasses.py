import math
import random
import time
MAX_TEMPERATURE = 2000
MAX_SPEED = 25.0
MAX_COLLISIONS = 8000
EVAPORATION_THRESHOLD = 2.5
CONDENSATION_THRESHOLD = 0.8
CELL_SIZE = 2.5
MAX_HISTORY = 500

class Molecule:
    def __init__(self, x, y, vx, vy, radius=0.4, color='blue'):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.color = color
        self.isLiquid = True

    def speed(self):
        return math.hypot(self.vx, self.vy)

    def kineticEnergy(self):
        return 0.5 * (self.vx ** 2 + self.vy ** 2)

    def move(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

class Grid:
    def __init__(self, cellSize):
        self.cellSize = cellSize
        self.cells = {}

    def clear(self):
        self.cells.clear()

    def getKey(self, x, y):
        return (int(x / self.cellSize), int(y / self.cellSize))

    def addMolecule(self, index, x, y):
        key = self.getKey(x, y)
        if key not in self.cells:
            self.cells[key] = []
        self.cells[key].append(index)

    def getNeighbors(self, x, y):
        cx = int(x / self.cellSize)
        cy = int(y / self.cellSize)
        neighbors = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                key = (cx + dx, cy + dy)
                if key in self.cells:
                    neighbors.extend(self.cells[key])
        return neighbors

class Simulator:
    def __init__(self, width, height, numMolecules, temperature):
        self.width = width
        self.height = height
        self.numMolecules = numMolecules
        self.temperature = temperature

        self.evaporationThreshold = EVAPORATION_THRESHOLD
        self.condensationThreshold = CONDENSATION_THRESHOLD
        self.useThermostat = True

        self.molecules = []
        self.time = 0.0
        self.stepCount = 0
        self.liquidCount = 0
        self.gasCount = 0
        self.evaporatedCount = 0
        self.condensedCount = 0

        self.temperatureHistory = []
        self.pressureHistory = []
        self.phaseHistory = []
        self.speedHistory = []

        self.cellSize = CELL_SIZE
        self.grid = Grid(self.cellSize)

        self.tempChangeActive = False
        self.tempStart = temperature
        self.tempEnd = temperature
        self.tempDuration = 60.0
        self.tempElapsed = 0.0
        self.lastUpdateTime = 0

        self.createMolecules()
        self.phase = "liquid"
        self.forceTemperature(temperature)

    def limitSpeed(self, mol):
        speed = mol.speed()
        if speed > MAX_SPEED:
            scale = MAX_SPEED / speed
            mol.vx *= scale
            mol.vy *= scale
    def gaussianRandom(self, mu, sigma): #мю это среднее
        u1 = max(0.0001, random.random())
        u2 = random.random()
        #метод Бокса-Мюллера
        z = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)#два равномерно распределённых числа в одно нормально распределённое
        return mu + sigma * z #z стандартное норм распределение сигма= 1

    def forceTemperature(self, targetTemp):
        n = len(self.molecules)

        totalEnergy = 0.0
        for mol in self.molecules:
            totalEnergy += mol.kineticEnergy()
        avgEnergy = totalEnergy / n
        currentTemp = 2 * avgEnergy

        if currentTemp < 0.001:
            return

        scaling = math.sqrt(targetTemp / currentTemp)
        if 0.01 < scaling < 100.0:
            for mol in self.molecules:
                mol.vx *= scaling
                mol.vy *= scaling
                self.limitSpeed(mol)

    def createMolecules(self):
        n = self.numMolecules
        if n < 1:
            n = 1

        self.molecules = []
        liquidCount = int(n * 0.7)#70 процентав жидкости
        sigma = math.sqrt(self.temperature / 50)#масштабный коэффициент (на угад)

        for i in range(n):
            x = random.uniform(1, self.width - 1)
            y = random.uniform(1, self.height - 1)
            vx = self.gaussianRandom(0, sigma)
            vy = self.gaussianRandom(0, sigma)

            if i < liquidCount:
                vx *= 0.3
                vy *= 0.3
                mol = Molecule(x, y, vx, vy, radius=0.4, color='blue')
                mol.isLiquid = True
            else:
                vx *= 2.0
                vy *= 2.0
                mol = Molecule(x, y, vx, vy, radius=0.3, color='red')
                mol.isLiquid = False

            self.limitSpeed(mol)
            self.molecules.append(mol)

    def buildGrid(self):
        self.grid.clear()
        for i, mol in enumerate(self.molecules):
            self.grid.addMolecule(i, mol.x, mol.y)

    def processCollision(self, i, j):
        mol1 = self.molecules[i]
        mol2 = self.molecules[j]

        dx = mol1.x - mol2.x
        dy = mol1.y - mol2.y
        distSq = dx * dx + dy * dy
        minDist = mol1.radius + mol2.radius

        if distSq < minDist * minDist and distSq > 1e-6:
            dist = math.sqrt(distSq)
            nx = dx / dist
            ny = dy / dist

            dvx = mol1.vx - mol2.vx
            dvy = mol1.vy - mol2.vy
            dvn = dvx * nx + dvy * ny

            if dvn > 0:
                return

            mol1.vx -= dvn * nx
            mol1.vy -= dvn * ny
            mol2.vx += dvn * nx
            mol2.vy += dvn * ny

            self.limitSpeed(mol1)
            self.limitSpeed(mol2)

            overlap = (minDist - dist) / 2
            mol1.x += overlap * nx
            mol1.y += overlap * ny
            mol2.x -= overlap * nx
            mol2.y -= overlap * ny

    # столкновение молекул
    def molecularCollisions(self):
        n = len(self.molecules)
        if n > 2000:
            self.fastCollisions()
        else:
            self.gridCollisions()

    #через сетку
    def gridCollisions(self):
        self.buildGrid()
        checked = set()
        collisionsDone = 0

        for i, mol1 in enumerate(self.molecules):
            if collisionsDone > MAX_COLLISIONS:
                break
            neighbors = self.grid.getNeighbors(mol1.x, mol1.y)

            for j in neighbors:
                if j <= i:
                    continue
                pair = (i, j) if i < j else (j, i)
                if pair in checked:
                    continue
                checked.add(pair)
                collisionsDone += 1
                if collisionsDone > MAX_COLLISIONS:
                    break
                self.processCollision(i, j)

    # столкновение пар молекул
    def fastCollisions(self):
        n = len(self.molecules)
        maxPairs = min(n * 3, 3000)
        checked = set()
        attempts = 0

        while len(checked) < maxPairs and attempts < maxPairs * 5:
            attempts += 1
            i = random.randint(0, n - 1)
            j = random.randint(0, n - 1)
            if i == j:
                continue
            pair = (min(i, j), max(i, j))
            if pair in checked:
                continue
            checked.add(pair)
            self.processCollision(i, j)

    #обработка стенок
    def wallCollisions(self):
        for mol in self.molecules:
            if mol.x - mol.radius < 0:
                mol.x = mol.radius
                mol.vx = abs(mol.vx)
            elif mol.x + mol.radius > self.width:
                mol.x = self.width - mol.radius
                mol.vx = -abs(mol.vx)

            if mol.y - mol.radius < 0:
                mol.y = mol.radius
                mol.vy = abs(mol.vy)
            elif mol.y + mol.radius > self.height:
                mol.y = self.height - mol.radius
                mol.vy = -abs(mol.vy)
            self.limitSpeed(mol)

    # переход
    def checkPhaseTransitions(self):
        n = len(self.molecules)
        if n == 0:
            return

        sumX = 0.0
        sumY = 0.0
        for mol in self.molecules:
            sumX += mol.x
            sumY += mol.y
        centerX = sumX / n
        centerY = sumY / n

        maxTransitions = min(n // 20 + 1, 30)
        transitionsDone = 0
        tempFactor = 1.0 + self.temperature / 1000
        evapThreshold = self.evaporationThreshold * tempFactor
        condThreshold = self.condensationThreshold * tempFactor

        for mol in self.molecules:
            if transitionsDone > maxTransitions:
                break
            dx = mol.x - centerX
            dy = mol.y - centerY
            dist = math.hypot(dx, dy)
            speed = mol.speed()

            if mol.isLiquid and dist > self.width * 0.3 and speed > evapThreshold:
                mol.isLiquid = False
                mol.color = 'red'
                mol.radius = 0.3
                mol.vx *= 1.2
                mol.vy *= 1.2
                self.evaporatedCount += 1
                transitionsDone += 1
                self.limitSpeed(mol)

            elif not mol.isLiquid and dist < self.width * 0.2 and speed < condThreshold:
                mol.isLiquid = True
                mol.color = 'blue'
                mol.radius = 0.4
                mol.vx *= 0.5
                mol.vy *= 0.5
                self.condensedCount += 1
                transitionsDone += 1

    def updateStatistics(self):
        n = len(self.molecules)
        if n == 0:
            return

        self.liquidCount = 0
        self.gasCount = 0
        speeds = []
        totalEnergy = 0.0

        for mol in self.molecules:
            if mol.isLiquid:
                self.liquidCount += 1
            else:
                self.gasCount += 1

            v = mol.speed()
            speeds.append(v)
            totalEnergy += 0.5 * v * v

        if self.liquidCount > n * 0.7:
            self.phase = "liquid"
        elif self.gasCount > n * 0.7:
            self.phase = "gas"
        else:
            self.phase = "mixed"
        self.phaseHistory.append(self.phase)

        avgEnergy = totalEnergy / n
        temp = min(2 * avgEnergy, MAX_TEMPERATURE)
        self.temperatureHistory.append(temp)

        if self.width > 0 and self.height > 0 and avgEnergy > 0:
            volume = self.width * self.height
            pressure = (2 / 3) * (n / volume) * avgEnergy
            self.pressureHistory.append(pressure)

        self.speedHistory = speeds
        self.stepCount += 1

        if len(self.temperatureHistory) > MAX_HISTORY:
            self.temperatureHistory = self.temperatureHistory[-MAX_HISTORY:]
            self.pressureHistory = self.pressureHistory[-MAX_HISTORY:]
            self.phaseHistory = self.phaseHistory[-MAX_HISTORY:]

    def applyThermostat(self):
        n = len(self.molecules)
        if n == 0:
            return

        totalEnergy = sum(mol.kineticEnergy() for mol in self.molecules)
        currentTemp = 2 * (totalEnergy / n)
        if currentTemp < 0.001:
            return

        targetTemp = min(self.temperature, MAX_TEMPERATURE)
        scaling = math.sqrt(targetTemp / currentTemp)

        if 0.1 < scaling < 10.0:
            for mol in self.molecules:
                mol.vx *= scaling
                mol.vy *= scaling
                self.limitSpeed(mol)

    def update(self, dt=0.05):
        n = len(self.molecules)
        if n == 0:
            return
        startTime = time.time()

        if n > 5000:
            dt *= 0.7

        if self.tempChangeActive:
            self.tempElapsed += dt
            progress = min(self.tempElapsed / self.tempDuration, 1.0)
            self.temperature = self.tempStart + (self.tempEnd - self.tempStart) * progress
            if progress >= 1.0:
                self.tempChangeActive = False
                self.temperature = self.tempEnd

        for mol in self.molecules:
            mol.move(dt)

        self.wallCollisions()
        self.molecularCollisions()
        self.checkPhaseTransitions()
        if self.useThermostat:
            self.applyThermostat()
        self.updateStatistics()

        self.time += dt
        self.lastUpdateTime = time.time() - startTime

    # негрев
    def startTemperatureRamp(self, startTemp, endTemp, duration):
        self.tempStart = max(10, min(startTemp, MAX_TEMPERATURE))
        self.tempEnd = max(10, min(endTemp, MAX_TEMPERATURE))
        self.tempDuration = max(1, duration)
        self.tempElapsed = 0.0
        self.tempChangeActive = True
        self.temperature = self.tempStart

    def getStatistics(self):
        return {
            'time': self.time,
            'phase': self.phase,
            'liquidCount': self.liquidCount,
            'gasCount': self.gasCount,
            'evaporated': self.evaporatedCount,
            'condensed': self.condensedCount,
            'temperature': self.temperatureHistory[-1] if self.temperatureHistory else self.temperature,
            'pressure': self.pressureHistory[-1] if self.pressureHistory else 0,
            'totalMolecules': len(self.molecules),
            'updateTime': self.lastUpdateTime
        }

    def getMolecules(self):
        return self.molecules

    def getSpeeds(self):
        return self.speedHistory