import fcntl
import termios
import sys
import time

def type_string(text, delay=0.1):
    with open('/dev/tty1', 'w') as fd:
        for c in text:
            fcntl.ioctl(fd, termios.TIOCSTI, bytes([ord(c)]))
            time.sleep(delay)

if __name__ == '__main__':
    text = sys.argv[1] if len(sys.argv) > 1 else 'echo test'
    type_string(text)
