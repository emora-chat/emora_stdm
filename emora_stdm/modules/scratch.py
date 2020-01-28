
to_add = ['karate', 'volunteer']

if __name__ == '__main__':

    with open("hobbies.txt", "r") as f:
        lines = f.readlines()
        options = []
        for line in lines:
            colon = line.index(":")
            options.append(line[1:colon])
    options.extend(to_add)
    options.sort()
    print('\n'.join(options))