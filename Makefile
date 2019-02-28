TARGETS = acquire

CC = g++
CFLAGS = -Wall --std=c++11
LDLIBS = -lBitLib -lz -lcnpy

all: $(TARGETS)

clean:
	rm -f $(TARGETS)
