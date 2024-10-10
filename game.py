table = list(range(1,10)) # генирирую игравой стол
def game_table(table): # функция вывода игравого стола
    print("-" * 13)
    for position in range(3):
        print("|",table[0+position*3], "|",table[1+position*3],"|",table[2+position*3], "|")
        print("-" * 13)
def check_winner(): # функция опредиления победителя
    victory_lines = [ # список победных линий
        [1,2,3],[4,5,6],[7,8,9], # горизанталь
        [1,4,7],[2,5,8],[3,6,9], # вертикаль
        [1,5,9],[3,6,9] # диоганаль
    ]
    for cell in victory_lines:
        if table[cell[0]-1] == table[cell[1]-1] == table[cell[2]-1]:
            return table[cell[0]-1] # возврашение победителя Х или 0
    else:
        None
def create_game(): # функция игры
    player = "X" # флаг текущего игрока
    timer = 0 # таймер счетчика ходов до ничьей
    game_table(table)
    while True:
        player_1 = input(f' Выход из программы. Введите: 10\n Игрок {player}, сделайте свой ход укажите число от 1 до 9:\n ')
        if not player_1.isnumeric(): # проверка, что введены цифры
            game_table(table)
            print("Неверно указан диапазон. Укажите число от 1 до 9")
            continue
        player_1 = int(player_1) # преобразование из строки в целое число
        if player_1 == 10: # прерывание игры
            print("Игра прервана!")
            break
        if 1 <= player_1 <= 9 and table[player_1-1] not in ["X","0"]: # проверка коректности ввода
            table[player_1-1] = player
            timer += 1
            game_table(table)
            winner = check_winner() # вызов функции проверки победителя
            if winner:
                print(f'Победил игрок {winner}!')
                return
            player = "0" if player == "X" else "X" # флаг для переключения игрока
        else:
            game_table(table)
            print ("Клетка занята")
            continue
        if timer == 9: # достижение максимального количества ходов без побидителя
            game_table(table)
            print("Ничья!")
            return
create_game()

