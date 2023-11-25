import threading
import time



def first_thread_function():
    print("First thread started")
    time.sleep(5)
    print("First thread finished")

def second_thread_function():
    while True:
        print("Second thread started")
        time.sleep(3)
        print("Second thread finished")



if __name__ == '__main__':
    first_thread = threading.Thread(target=first_thread_function)
    second_thread = threading.Thread(target=second_thread_function)

    second_thread.start()
    first_thread.start()



    #second_thread.join()
    #second_thread.join()
