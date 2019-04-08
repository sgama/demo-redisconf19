import redis


def main():
    r = redis.Redis(host="localhost", port=6379)

    for i in range(100):
        r.set(str(i), str(i))


if __name__ == '__main__':
    main()
