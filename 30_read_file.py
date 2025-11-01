with open('data.txt', 'r+', encoding='utf-8') as f:
    lines = f.readlines()
    for line in lines:
        print(line)

    f.write('\n测试4')
    print(f.read())