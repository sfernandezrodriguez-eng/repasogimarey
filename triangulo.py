n = int(input("Digite un número de las pollas que se come mario: "))

while n > 0:
    for i in range(1, n + 1):
        print(" " * (n - i) + "*" * (2 * i - 1))
    break