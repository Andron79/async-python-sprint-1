from multiprocessing import Pool, TimeoutError, current_process
import time, os


def worker(x):
    print('WORKER() => ', current_process().name)
    return x * x


if __name__ == '__main__':
    # запуск 4 рабочих процессов
    with Pool(processes=4) as pool:
        # результаты получим в
        # порядке поступления задач
        res = pool.map(worker, range(10))
        print(res)

    #     # результаты получим в порядке их
    #     # готовности (могут быть не по порядку)
    #     for i in pool.imap_unordered(worker, range(10)):
    #         print(i, end=', ')
    #     print()
    #
        # вычислит "worker(20)" асинхронно
        # запустится только один процесс
        res = pool.apply_async(worker, (20,))
        # получение результата
        async_worker = res.get(timeout=1)
        print('1 процесс, worker(20) => ', async_worker)

        # вычислит "os.getpid()" асинхронно
        # запустится только один процесс
        res = pool.apply_async(os.getpid, ())
        # получение результата
        async_getpid = res.get(timeout=1)
        print('1 процесс, os.getpid()  => ', async_getpid)

        # запуск нескольких асинхронных вычислений
        # *может* использовать больше процессов
        multiple_results = [pool.apply_async(os.getpid, ()) for i in range(4)]
        # получение асинхронных результатов
        async_multi = [res.get(timeout=1) for res in multiple_results]
        print('4 асинхронных процесса, os.getpid():')
        print(async_multi)
    #
    #     # заставим спать один рабочий в течение 10 секунд
    #     res = pool.apply_async(time.sleep, (10,))
    #     try:
    #         # получение результата
    #         res_sleep = res.get(timeout=1)
    #         print(res_sleep)
    #     except TimeoutError:
    #         print("time.sleep(10) => получили multiprocessing.TimeoutError")
    #
    #     print("На этот момент пул остается доступным для дополнительной работы")
    #
    # # выход из блока 'with' остановил пул
    # print("Теперь пул закрыт и больше не доступен")