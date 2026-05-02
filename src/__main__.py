from src.parser import Parser

if __name__ == "__main__":
    pars = Parser('easy')
    data = pars.parser()
    count = 0
    x_max = 0
    y_max = 0
    for hub in data[0]['hubs']:
        if hub['x'] > x_max:
            x_max = hub['x']
        if hub['y'] > y_max:
            y_max = hub['y']
    print(f"Max x: {x_max}, Max y: {y_max}")
    grid = [["." for _ in range(x_max + 1)] for _ in range(y_max + 1)]
    for row in reversed(grid):
        print(" ".join(row))

